from flask import Flask, render_template, request
from sqlalchemy import create_engine, MetaData, Table, select, and_, func, asc, desc

app = Flask(__name__)

# Database setup
engine = create_engine("sqlite:///sales.db")
metadata = MetaData()
metadata.reflect(bind=engine)
sales = metadata.tables['sales']

@app.route('/', methods=['GET', 'POST'])
def index():
    report_data = []
    chart_data = {}
    graph_types = ['Bar Chart', 'Line Chart', 'Pie Chart', 'Scatter Plot']
    attributes = [col.name for col in sales.columns]
    regions = ["North", "South", "East", "West"]

    with engine.connect() as conn:
        min_date = conn.execute(select(func.min(sales.c.order_date))).scalar()
        max_date = conn.execute(select(func.max(sales.c.order_date))).scalar()

    if request.method == 'POST':
        selected_fields = request.form.getlist('fields')
        region = request.form.get('region')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        aggregate = request.form.get('aggregate')
        sort_field = request.form.get('sort_field')
        sort_order = request.form.get('sort_order')
        distinct = request.form.get('distinct') == 'on'
        selected_graph = request.form.get('graph_type')

        columns = [sales.c[field] for field in selected_fields if field != 'amount']

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
        elif 'amount' in selected_fields:
            columns.append(sales.c.amount)

        query = select(*columns)
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
            group_columns = [sales.c[field] for field in selected_fields if field != 'amount']
            if group_columns:
                query = query.group_by(*group_columns)

        if sort_field:
            sort_col = getattr(sales.c, sort_field, None)
            if sort_col is not None:
                query = query.order_by(asc(sort_col) if sort_order == 'asc' else desc(sort_col))

        with engine.connect() as conn:
            result = conn.execute(query)
            report_data = result.mappings().all()  # Ensure mappings() for dict-like rows

        if report_data:
            first_key = list(report_data[0].keys())[0]
            last_key = list(report_data[0].keys())[-1]
            chart_data['labels'] = [str(row[first_key]) for row in report_data]
            chart_data['values'] = [
                float(row[last_key]) if row[last_key] is not None else 0.0
                for row in report_data
            ]
            chart_data['label'] = str(last_key)
            chart_data['graph_type'] = selected_graph

            # Debugging Print (optional, remove in production)
            print("chart_data:", chart_data)

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
