# log-heating-oil-price

The overall goal is to get some data from the web, visualize it on the web, and keep the data up to date.

This repo does 3 things
1. Gets Irving heating oil prices from the [Eastrise (formerly VSECU) fuel buying program](https://www.eastrise.com/personal/fuel-buying-program/) and stores them in a csv.
2. Generates a website to visualize the data: an [Observable Framework](https://observablehq.com/framework) project in `of/`, hosted on Cloudflare Pages at https://log-heating-oil-price.pages.dev/
3. Automates this process to get new data daily


## Dependencies
* The dealer JSON embedded in the Eastrise page to get the data, with [Playwright](https://playwright.dev/python/) as a fallback.
* [Observable Framework](https://observablehq.com/framework) to generate the website, hosted on [Cloudflare Pages](https://pages.cloudflare.com/).
* Github Actions to get new data.
* [act](https://github.com/nektos/act) for testing Github Action locally.


## Running locally
Get data
```
uv sync
source .venv/bin/activate
playwright install-deps webkit
pytest --browser=webkit search.py
```

Run website (see `of/README.md`)
```
cd of
npm ci
npm run dev
```


Test Github action locally
```
act -s GITHUB_TOKEN="$(gh auth token)" workflow_dispatch
```

## Daily phone notifications
The daily Github Action can send the current price and change over the last 1, 7 and 30 days to your phone using [ntfy](https://ntfy.sh).

1. Install the ntfy app ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/us/app/ntfy/id1625396347)) and subscribe to a hard-to-guess topic name, e.g. `oil-price-8f3k2x9q`. Anyone who knows the topic name can read it, so treat it like a password.
2. In the repo go to Settings → Secrets and variables → Actions and add a secret `NTFY_TOPIC` with that name.
3. Run the workflow manually (Actions → Run script → Run workflow) to test.

To resend today's notification without scraping, use Actions → Send notification → Run workflow.

To turn notifications off, delete the `NTFY_TOPIC` secret. Optionally add `NTFY_TOKEN` if you use a reserved topic or self-hosted server.

Preview the message locally
```
python notify.py --dry-run
```

## Deploy
### Data
Data is updated via Github actions. See `.github/workflows/run.yml`

The daily run is started at 19:04 UTC by a Cloudflare Worker in `scheduler/`, because GitHub's own schedule runs hours late. GitHub's schedule is kept as a backup. Setup, the GitHub token it uses, and when that token expires: see [`scheduler/README.md`](scheduler/README.md).

### Website
Cloudflare Pages builds and hosts the site from `of/`.

## Rationale for my original approach
1. I like Github pages because it is free, doesn't require another account to set up, deployment is simple/automatic and just hosts static files so is very stable.
2. I wanted a project to learn more Python so I focused on solutions that use Python.
3. After exploring various Python dashboarding tools like Dash, Streamlit, and Voila I decided I liked Panel the best. Not sure I can pin down why.
4. I wanted an excuse to try running Python in the browser to see how well it worked.

### Why I moved away from that
The site has since moved from Panel on Github Pages to Observable Framework on Cloudflare Pages.
1. Python is too slow, and I wanted to try out Observable Framework.
2. Github Pages only allows one environment and I wanted to be able to test out branches live.
