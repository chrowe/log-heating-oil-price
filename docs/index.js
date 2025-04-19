importScripts("https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js");
import { Inputs } from "@observablehq/inputs";

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.2/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.2/dist/wheels/panel-0.14.2-py3-none-any.whl', 'pyodide-http==0.1.0', 'pandas']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

import panel as pn
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import DateRangeSlider

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

csv_file = 'https://raw.githubusercontent.com/chrowe/log-heating-oil-price/main/irving_oil_prices.csv'
data = pd.read_csv(csv_file, parse_dates=['date'])

# Date Slider
date_slider = Inputs.date({
  label: "Start Date",
  min: new Date(data['date'].min()),
  max: new Date(data['date'].max()),
  value: new Date(data['date'].min())
})

# Filtered data
filtered_data = data[data['date'] >= date_slider.value]

# Graph
source = ColumnDataSource(filtered_data)
p = figure(x_axis_type="datetime", title="Oil Price", height=350, width=800)
p.xgrid.grid_line_color=None
p.ygrid.grid_line_alpha=0.5
p.xaxis.axis_label = 'Day'
p.yaxis.axis_label = 'Price'

p.line('date', 'price', source=source)

# Update function
def update_data(event):
    filtered_data = data[data['date'] >= event.new]
    source.data = ColumnDataSource(filtered_data).data

date_slider.addEventListener("input", update_data)

layout = column(date_slider, p)

pn.panel(
    layout
).servable()


# Table
pn.panel(
    data
).servable()
    

await write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.runPythonAsync(`
    import json

    state.curdoc.apply_json_patch(json.loads('${msg.patch}'), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads("""${msg.location}""")
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()
