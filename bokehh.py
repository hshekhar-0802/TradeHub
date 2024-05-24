from bokeh.plotting import figure, show, output_file
from bokeh.models import NumeralTickFormatter, DatetimeTickFormatter, HoverTool
from datetime import datetime
from bokeh.embed import components
import pandas as pd
from bokeh.models import ColumnDataSource, Band
from bokeh.palettes import Category20

def graph(dates, closing_prices, open, stock_symbol, colour):
    p = figure(x_axis_type="datetime", title="Closing Prices", width=900, height=410)
    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price"
    p.background_fill_color = "#131B23"
    line = p.line(dates, closing_prices, color="#33FF33" if colour=='green' else "#ff2200", line_width=2)
    p.xaxis.formatter = DatetimeTickFormatter()
    p.yaxis.formatter = NumeralTickFormatter(format="0,0")
    hover = HoverTool(renderers=[line], tooltips=[("Date", "@x{%F}"), ("Price", "@y{0,0}")], formatters={"@x": "datetime"})
    p.add_tools(hover)
    script, div = components(p)
    return script, div

def multipleplot(stocklist, dates, data, parameter):
    p = figure(x_axis_type="datetime", title=parameter, width=900, height=550)
    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = parameter
    p.background_fill_color = "#131B23"
    colors = ["#ff2200", "#33FF33", "#3399FF", "#FF3366", "#33FFFF","#FFD633", "#FF66B2", "#33FF99", "#9966FF", "#FF9933","#33CCFF", "#FF3366", "#33FFCC", "#FFCC33", "#3366FF","#FF3333", "#33FF66", "#FF66CC", "#33FF33", "#FF9933","#33FF66", "#FF66CC", "#33FF33", "#FF9933", "#33FF66","#FF66CC", "#33FF33", "#FF9933", "#33FF66", "#FF66CC"]
    for i in range(len(stocklist)):
        p.line(dates[i], data[i], color=colors[i%len(colors)], line_width=2, legend_label=stocklist[i])
    p.yaxis.formatter = NumeralTickFormatter(format="0,0")
    p.xaxis.formatter = DatetimeTickFormatter()
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.legend.spacing = 2 
    p.legend.label_text_font_size = "8pt" 
    script, div = components(p)
    return script, div
