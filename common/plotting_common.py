from bokeh.models import DataTable, ColumnDataSource, TableColumn
from bokeh.plotting import figure


def plot_image(path, width=700, height=300):
    p = figure(x_range=(0, 1), y_range=(0, 1), width=width, plot_height=height, toolbar_location=None)
    p.image_url(url=[path], x=0, y=1, w=1, h=1)
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.xaxis.visible = False
    p.yaxis.visible = False
    return p


def create_table(data, filename, width=1400, height=300):
    source = ColumnDataSource(data)
    column_list =[]
    for column in source.column_names:
        column_list.append(TableColumn(field=column, title=column.split('|')[0]))

    data_table = DataTable(source=source, columns=column_list, sizing_mode='scale_both', width=width, height=height)
    return data_table
