from flask import Flask, render_template, request
from sqlalchemy import create_engine, MetaData, Table, select, and_, func, asc, desc
from collections import deque

app = Flask(__name__)

# Database setup
engine = create_engine("sqlite:///sales.db")
metadata = MetaData()
metadata.reflect(bind=engine)

sales = metadata.tables['sales']
customers = metadata.tables['customers']
products = metadata.tables['products']

# Join graph definition
join_graph = {
    "sales": {
        "customers": sales.c.customer_name == customers.c.customer_name,
        "products": sales.c.product == products.c.product_name
    },
    "customers": {
        "sales": customers.c.customer_name == sales.c.customer_name
    },
    "products": {
        "sales": products.c.product_name == sales.c.product
    }
}

# BFS to find join path
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

@app.route('/', methods=['GET', 'POST'])
def index():
    report_data = []
    chart_data = {}
    graph_types = ['Bar Chart', 'Line Chart', 'Pie Chart', 'Scatter Plot']
    all_tables = {"sales": sales, "customers": customers, "products": products}
    attributes = {table: [col.name for col in all_tables[table].columns] for table in all_tables}
    regions = ["North", "South", "East", "West"]

    with engine.connect() as conn:
        min_date = conn.execute(select(func.min(sales.c.order_date))).scalar()
        max_date = conn.execute(select(func.max(sales.c.order_date))).scalar()

    if request.method == 'POST':
        table1 = request.form.get('table1')
        table2 = request.form.get('table2')
        selected_fields = request.form.getlist('fields')
        region = request.form.get('region')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        aggregate = request.form.get('aggregate')
        sort_field = request.form.get('sort_field')
        sort_order = request.form.get('sort_order')
        distinct = request.form.get('distinct') == 'on'
        selected_graph = request.form.get('graph_type')

        path = bfs_join_path(join_graph, table1, table2)
        if not path:
            return render_template("index.html", attributes=attributes, regions=regions, 
                                   min_date=min_date, max_date=max_date, graph_types=graph_types, 
                                   error="No join path found between selected tables.")

        from sqlalchemy.sql import Join
        from_clause = all_tables[path[0]]
        for i in range(1, len(path)):
            left = path[i - 1]
            right = path[i]
            join_condition = join_graph[left][right]
            from_clause = from_clause.join(all_tables[right], join_condition)

        columns = []
        for field in selected_fields:
            for table in all_tables.values():
                if field in table.c:
                    columns.append(table.c[field])
                    break

        if aggregate and 'amount' in selected_fields:
            if aggregate == 'sum':
                agg_column = func.sum(sales.c.amount).label('total_amount')
            elif aggregate == 'avg':
                agg_column = func.avg(sales.c.amount).label('average_amount')
            elif aggregate == 'count':
                agg_column = func.count(sales.c.amount).label('count_amount')
            else:
                agg_column = sales.c.amount
            columns.append(agg_column)

        query = select(*columns).select_from(from_clause)
        if distinct:
            query = query.distinct()

        filters = []
        if region:
            filters.append(sales.c.region == region)
        if start_date and end_date:
            filters.append(sales.c.order_date.between(start_date, end_date))
        if filters:
            query = query.where(and_(*filters))

        if aggregate:
            group_columns = [col for col in columns if not isinstance(col, (func.count, func.sum, func.avg))]
            if group_columns:
                query = query.group_by(*group_columns)

        if sort_field:
            for table in all_tables.values():
                if sort_field in table.c:
                    sort_col = table.c[sort_field]
                    query = query.order_by(asc(sort_col) if sort_order == 'asc' else desc(sort_col))
                    break

        with engine.connect() as conn:
            result = conn.execute(query)
            report_data = result.mappings().all()

        if report_data:
            first_key = list(report_data[0].keys())[0]
            last_key = list(report_data[0].keys())[-1]
            chart_data['labels'] = [str(row[first_key]) for row in report_data]
            chart_data['values'] = [float(row[last_key]) if row[last_key] is not None else 0.0 for row in report_data]
            chart_data['label'] = str(last_key)
            chart_data['graph_type'] = selected_graph

    return render_template(
        "index.html",
        report_data=report_data,
        attributes=attributes,
        regions=regions,
        min_date=min_date,
        max_date=max_date,
        graph_types=graph_types,
        chart_data=chart_data
    )

if __name__ == '__main__':
    app.run(debug=True)
