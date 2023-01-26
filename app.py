import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")

pn.state.template.param.update(
    site_url="https://awesome-panel.org",
    site="Awesome Panel",
    title="Hello World",
)

pn.panel(
    "This is a log of the price of Irving Oil from [VSECU](https://www.vsecu.com/personal/home-heating/fuel-buying-program)"
).servable()

import pandas as pd; import numpy as np; import matplotlib.pyplot as plt

csv_file = 'https://raw.githubusercontent.com/chrowe/log-heating-oil-price/main/irving_oil_prices.csv'
data = pd.read_csv(csv_file, parse_dates=['date'], index_col='date')

pn.panel(
    data
).servable()
    