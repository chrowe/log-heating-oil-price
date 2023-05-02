# log-heating-oil-price
This repo does 2 things
1. Gets Irving VSECU heating oil prices and stores them in a csv.
2. Generates a website hosted on Github pages to visualize the data. (based on [this article](https://towardsdatascience.com/how-to-deploy-a-panel-visualization-dashboard-to-github-pages-2f520fd8660))


## Requirements
* [Playwright](https://playwright.dev/python/) to get the data.
* [Panel](https://panel.holoviz.org/) to generat the website.
* [act](https://github.com/nektos/act) for testing Github Action locally


## Running locally
Get data
```
conda install python3.9 playwright==1.29.1 pytest-playwright==0.3.0
playwright install-deps
playwright install firefox
pytest --browser=firefox search.py
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

## Deploy
### Data
Github actions

### Website
```
panel convert index.py --to pyodide-worker --pwa --title "VSECU Oil Price" --out docs
git add docs/*
git commit -m 'Deploy website'
```