from bokeh.plotting import figure


def plot_image(path, width=900, height=300):
    p = figure(x_range=(0, 1), y_range=(0, 1), width=width, plot_height=height, toolbar_location=None)
    p.image_url(url=[path], x=0, y=1, w=1, h=1)
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.xaxis.visible = False
    p.yaxis.visible = False
    return p
