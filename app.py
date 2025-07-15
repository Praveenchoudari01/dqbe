from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from sqlalchemy import create_engine, MetaData, select, and_, func, asc, desc, text
from collections import deque

app = Flask(__name__)
app.secret_key = 'dqbe_dashboard'

# Database setup
engine = create_engine("sqlite:///sales.db")
metadata = MetaData()
metadata.reflect(bind=engine)

# Dynamically get all tables
all_tables = {table.name: table for table in metadata.sorted_tables}

# Build join graph dynamically
join_graph = {
    "sales": {
        "customers": all_tables["sales"].c.customer_name == all_tables["customers"].c.customer_name,
        "products": all_tables["sales"].c.product == all_tables["products"].c.product_name,
    },
    "customers": {
        "sales": all_tables["customers"].c.customer_name == all_tables["sales"].c.customer_name,
    },
    "products": {
        "sales": all_tables["products"].c.product_name == all_tables["sales"].c.product,
    }
}

def bfs_join_path(graph, start, end):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, {}):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    return None

@app.route('/add_to_dashboard', methods=['POST'])
def add_to_dashboard():
    sql_query = request.form.get('sql_query')
    selected_type = request.form.get('chart_type')
    label_field = request.form.get('label_field')
    value_field = request.form.get('value_field')

    normalized_type = selected_type.strip().lower() if selected_type else ""

    chart_type_map = {
        "bar chart": "bar", "barchart": "bar", "bar": "bar",
        "line chart": "line", "linechart": "line", "line": "line",
        "pie chart": "pie", "piechart": "pie", "pie": "pie",
        "doughnut chart": "doughnut", "doughnutchart": "doughnut", "doughnut": "doughnut",
        "radar chart": "radar", "radarchart": "radar", "radar": "radar",
        "polar area": "polarArea", "polararea": "polarArea"
    }

    chart_type = chart_type_map.get(normalized_type, 'bar')

    if 'dashboard_charts' not in session:
        session['dashboard_charts'] = []

    charts = session['dashboard_charts']
    charts.append({
        "query": sql_query,
        "graph_type": chart_type,
        "label_field": label_field,
        "value_field": value_field
    })

    session['dashboard_charts'] = charts
    return redirect(url_for('index'))

@app.route('/view_dashboard')
def view_dashboard():
    charts = []
    dashboard_charts = session.get('dashboard_charts', [])

    with engine.connect() as conn:
        for chart_def in dashboard_charts:
            try:
                result = conn.execute(text(chart_def['query']))
                data = result.mappings().all()
                if not data:
                    continue

                labels = [str(row.get(chart_def['label_field'], '')) for row in data]
                values = []
                for row in data:
                    raw_value = row.get(chart_def['value_field'], 0)
                    try:
                        values.append(float(raw_value))
                    except (ValueError, TypeError):
                        values.append(0.0)

                charts.append({
                    'graph_type': chart_def['graph_type'],
                    'labels': labels,
                    'values': values,
                    'label': chart_def['value_field'],
                    'label_field': chart_def['label_field'],
                    'value_field': chart_def['value_field'],
                    'sql_query': chart_def['query']
                })
            except Exception as e:
                print("Chart render error:", e)
                continue

    return render_template('dashboard.html', dashboard=charts)

@app.route('/update_chart_action', methods=['POST'])
def update_chart_action():
    chart_id = int(request.form.get('chart_id'))
    action = request.form.get('action')

    if 'dashboard_charts' in session:
        charts = session['dashboard_charts']
        if 0 <= chart_id < len(charts):
            if action == 'remove':
                charts.pop(chart_id)
            elif action == 'save':
                charts[chart_id]['saved'] = True

        session['dashboard_charts'] = charts

    return redirect(url_for('view_dashboard'))

@app.route('/', methods=['GET', 'POST'])
def index():
    report_data = []
    chart_data = None
    graph_types = ['Bar Chart', 'Line Chart', 'Pie Chart', 'Scatter Plot']
    attributes = {table: [col.name for col in all_tables[table].columns] for table in all_tables}
    regions = ["North", "South", "East", "West"]

    with engine.connect() as conn:
        min_date = conn.execute(select(func.min(all_tables["sales"].c.order_date))).scalar()
        max_date = conn.execute(select(func.max(all_tables["sales"].c.order_date))).scalar()

    query_string = ""
    all_columns = []
    groupable_fields = []

    if request.method == 'POST':
        table1 = request.form.get('table1')
        table2 = request.form.get('table2')
        selected_fields = request.form.getlist('fields')
        region = request.form.get('region')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        aggregate = request.form.get('aggregate')
        aggregate_field = request.form.get('aggregate_field')  # <-- ✅ ADDED THIS LINE
        sort_field = request.form.get('sort_field')
        sort_order = request.form.get('sort_order')
        distinct = request.form.get('distinct') == 'on'
        selected_graph = request.form.get('graph_type')
        group_by_field = request.form.get('group_by')

        selected_tables = []
        if table1:
            selected_tables.append(all_tables[table1])
        if table2 and table2 != table1:
            selected_tables.append(all_tables[table2])

        if table1 and table2:
            all_columns = list(set(attributes.get(table1, []) + attributes.get(table2, [])))
            groupable_fields = [col for col in all_columns if col.lower() not in ('id', 'amount')]

        path = bfs_join_path(join_graph, table1, table2) if table2 else [table1]
        if not path:
            return render_template("index.html", attributes=attributes, regions=regions,
                                   min_date=min_date, max_date=max_date, graph_types=graph_types,
                                   all_columns=all_columns, groupable_fields=groupable_fields,
                                   error="No join path found between selected tables.")

        from_clause = all_tables[path[0]]
        for i in range(1, len(path)):
            left = path[i - 1]
            right = path[i]
            join_condition = join_graph[left][right]
            from_clause = from_clause.join(all_tables[right], join_condition)

        columns = []
        group_columns = []
        agg_column = None

        # Handle group_by field
        if group_by_field:
            for table in selected_tables:
                if group_by_field in table.c:
                    group_col = table.c[group_by_field]
                    group_columns.append(group_col)
                    columns.append(group_col)
                    break

        # Handle aggregation
        if aggregate and aggregate_field:
            for table_name, table in all_tables.items():
                if aggregate_field in table.c:
                    target_col = table.c[aggregate_field]
                    if aggregate == 'sum':
                        agg_column = func.sum(target_col).label(f"sum_{aggregate_field}")
                    elif aggregate == 'avg':
                        agg_column = func.avg(target_col).label(f"avg_{aggregate_field}")
                    elif aggregate == 'count':
                        agg_column = func.count(target_col).label(f"count_{aggregate_field}")
                    break
            if agg_column is not None:
                columns.append(agg_column)
        else:
            for field in selected_fields:
                for table in selected_tables:
                    if field in table.c:
                        col = table.c[field]
                        if col not in columns:
                            columns.append(col)
                        break

        # Build query
        query = select(*columns).select_from(from_clause)
        if distinct:
            query = query.distinct()

        filters = []
        if region:
            filters.append(all_tables["sales"].c.region == region)
        if start_date and end_date:
            filters.append(all_tables["sales"].c.order_date.between(start_date, end_date))
        if filters:
            query = query.where(and_(*filters))

        if group_columns:
            query = query.group_by(*group_columns)

        if sort_field:
            for table in selected_tables:
                if sort_field in table.c:
                    sort_col = table.c[sort_field]
                    query = query.order_by(asc(sort_col) if sort_order == 'asc' else desc(sort_col))
                    break

        query_string = str(query)
        print("\n[Generated SQL Query by DQBE]:\n", query_string)

        with engine.connect() as conn:
            result = conn.execute(query)
            report_data = result.mappings().all()

        # Prepare chart data
        if report_data:
            first_key = list(report_data[0].keys())[0]
            last_key = list(report_data[0].keys())[-1]
            labels = [str(row[first_key]) for row in report_data]
            raw_values = [row[last_key] for row in report_data]

            try:
                values = [float(v) if v is not None else 0.0 for v in raw_values]
                chart_data = {
                    'labels': labels,
                    'values': values,
                    'label': str(last_key),
                    'graph_type': selected_graph,
                    'label_field': first_key,
                    'value_field': last_key,
                    'query': query_string
                }
            except (ValueError, TypeError):
                chart_data = None
    else:
        groupable_fields = [col for table in attributes for col in attributes[table] if col.lower() not in ('id', 'amount')]

    return render_template(
        "index.html",
        report_data=report_data,
        attributes=attributes,
        regions=regions,
        min_date=min_date,
        max_date=max_date,
        graph_types=graph_types,
        chart_data=chart_data,
        query_string=query_string,
        all_columns=all_columns,
        groupable_fields=groupable_fields
    )

@app.route('/add_to_report', methods=['POST'])
def add_to_report():
    sql_query = request.form.get('sql_query')
    label_field = request.form.get('label_field')
    value_field = request.form.get('value_field')
    graph_type_raw = request.form.get('graph_type')

    # ✅ Map user-friendly chart names to Chart.js-compatible types
    type_mapping = {
        "Bar Chart": "bar",
        "Line Chart": "line",
        "Pie Chart": "pie",
        "Doughnut Chart": "doughnut",
        "Radar Chart": "radar",
        "Polar Area Chart": "polarArea"
    }
    graph_type = type_mapping.get(graph_type_raw.strip(), "bar")  # Default to 'bar' if invalid

    print("Received graph type:", graph_type_raw, "→ Mapped to:", graph_type)

    if not all([sql_query, label_field, value_field]):
        return "Missing data", 400

    if 'reports' not in session:
        session['reports'] = []

    reports = session['reports']
    reports.append({
        'query': sql_query,
        'label_field': label_field,
        'value_field': value_field,
        'graph_type': graph_type
    })
    session['reports'] = reports
    session.modified = True

    return redirect(url_for('view_reports'))

@app.route('/view_reports')
def view_reports():
    reports = session.get('reports', [])
    rendered_reports = []

    with engine.connect() as conn:
        for idx, rpt in enumerate(reports):
            try:
                result = conn.execute(text(rpt['query']))
                rows = result.mappings().all()

                if not rows:
                    continue

                columns = list(rows[0].keys())
                data = [dict(row) for row in rows]

                labels = [str(row[rpt['label_field']]) for row in rows]
                values = [float(row[rpt['value_field']]) if isinstance(row[rpt['value_field']], (int, float)) else 0 for row in rows]

                # print(rpt.get('graph_type'))
                rendered_reports.append({
                    'index': idx + 1,
                    'query': rpt['query'],
                    'label_field': rpt['label_field'],
                    'value_field': rpt['value_field'],
                    'graph_type': rpt.get('graph_type'),
                    'labels': labels,
                    'values': values,
                    'columns': columns,
                    'data': data
                })
            except Exception as e:
                print(f"[Report {idx+1}] Failed: {e}")
                continue

    return render_template('report_preview.html', reports=rendered_reports)


if __name__ == '__main__':
    app.run(debug=True, port=8989)
