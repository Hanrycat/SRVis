import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool

output_file('my_first_graph.html')

x = [1, 3, 5, 7]
y = [2, 4, 6, 8]

p = figure()

df = pd.read_csv('..\Autocross last run June 22 18.log')
# print(df)
# print(df.columns.tolist())

sample = df.sample(50)
source = ColumnDataSource(sample)

p = figure()
p.line(x='Interval|"ms"|0|0|1', y='EngineTemp|"C"|0|200|1',
       line_width=2,
       source=source,
       legend='EngineTemp')

p.title.text = 'Engine Temp over Time'
p.xaxis.axis_label = 'Time'
p.yaxis.axis_label = 'Temp (degC)'

# hover = HoverTool()
# hover.tooltips = [
#     ('Temp', '@EngineTemp|"C"|0|200|1'),
#     ('Time', '@Interval|"ms"|0|0|1')
# ]
#
# p.add_tools(hover)

show(p)
