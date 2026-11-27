1. Playwright has versions for multiple languages. When you are looking at their docs make sure it says Python at the top (especially important when Googling)
2. Python dependencies are managed with [uv](https://docs.astral.sh/uv/) in `pyproject.toml` and `uv.lock`. Run `uv sync` to install them. They only cover the scraper and the notifier; the website's dependencies are in `of/package.json`.
