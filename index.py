import panel as pn

# Page setup
pn.extension(sizing_mode="stretch_width", template="fast")


# Header
pn.state.template.param.update(
    site_url="",
    site="VSECU Oil Price",
    title="Data",
)


# Intro
pn.panel(
    "This is a log of the price of Irving Oil from [VSECU](https://www.vsecu.com/personal/home-heating/fuel-buying-program)"
).servable()


# Get data
import pandas as pd
from bokeh.models import ColumnDataSource

csv_file = 'https://raw.githubusercontent.com/chrowe/log-heating-oil-price/main/irving_oil_prices.csv'
data = pd.read_csv(csv_file, parse_dates=['date'])


# Graph
from bokeh.plotting import figure

TOOLTIPS = [
    ("Date", "@date{%F}"),
    ("Price", "$@price"),
]

source = ColumnDataSource(data)

p = figure(x_axis_type="datetime", title="Oil Price", height=350, width=800, tooltips=TOOLTIPS)
p.xgrid.grid_line_color=None
p.ygrid.grid_line_alpha=0.5
p.xaxis.axis_label = 'Day'
p.yaxis.axis_label = 'Price'
p.hover.formatters = { "@date": "datetime"}

p.line(x='date', y='price', source=source)

pn.panel(
    p
).servable()


# Table
pn.panel(
    data
).servable()
    