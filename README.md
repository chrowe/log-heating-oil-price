# log-heating-oil-price

The oval goal is to get some data from the web, visualize it the web, and keep the data up to date.

This repo does 3 things
1. Gets Irving VSECU heating oil prices and stores them in a csv.
2. Generates a website hosted on Github pages to visualize the data. (based on [this article](https://towardsdatascience.com/how-to-deploy-a-panel-visualization-dashboard-to-github-pages-2f520fd8660))
3. Automates this process to get new data daily


## Dependencies
* [Playwright](https://playwright.dev/python/) to get the data.
* [Panel](https://panel.holoviz.org/) to generate the website.
* [Pyodide](https://github.com/pyodide/pyodide) to run Python in the browser.
* Github Actions to get new data and deploy website updates.
* [act](https://github.com/nektos/act) for testing Github Action locally.


## Running locally
Get data
```
uv sync
source .venv/bin/activate
playwright install-deps webkit
pytest --browser=webkit search.py
```

Run website
```
conda install panel hvplot -c pyviz
panel serve index.py --show --autoreload
```


Test Github action locally
```
act --container-architecture linux/amd64 workflow_dispatch
```
note: `--container-architecture linux/amd64` is only needed if you are running on an M1 Mac.

## Deploy
### Data
Data is updated via Github actions. See `.github/workflows/run.yml`

### Website
```
panel convert index.py --to pyodide-worker --pwa --title "VSECU Oil Price" --out docs
git add docs/*
git commit -m 'Deploy website'
```

## Rational for my approach
1. I like Github pages because it is free, doesn't require another account to set up, deployment is simple/automatic and just hosts static files so is very stable.
2. I wanted a project to learn more Python so I focused on solutions that use Python.
3. After exploring various Python dashboarding tools like Dash, Streamlit, and Voila I decided I liked Panels the best. Not sure I can pin down why.
4. I wanted an excuse to try running Python in the browser to see how well it worked.

