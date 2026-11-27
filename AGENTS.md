# AGENTS.md

Notes for AI coding agents working in this repo. See README.md for what the project does.

## What this is for

A personal tool for tracking the price of heating oil for my home. It scrapes Irving's price (and other dealers' prices) from the Eastrise fuel buying program daily, shows the history on a website, and sends a daily phone notification with the price and how it has changed. It's also a project for learning new tools (it started as a way to learn Python, and the site moved to Observable Framework partly to try it out).

## How I like to work

- **Act like a product manager, not an order-taker.** My requests are often brief. Before building:
  - Work out what I'm trying to achieve and why, given what this app is for.
  - If my intent isn't clear, ask me questions. Don't guess.
  - If there's a better or simpler way to meet the need than what I asked for, suggest it, and explain the trade-off. Don't treat my request as the spec.
- **Use existing tools first.** Before building something, check for an open source tool that already does it and suggest that. I'd rather contribute to an existing project than start a new one.
- **Ask before outward-facing actions I didn't request**, such as closing issues, commenting, or merging. Once I say yes, do it without asking again.
- **Every PR starts from an issue.** When I ask for a change, don't go straight to a PR. First look for an open issue that covers the work.
  - If there is one, check it says what will be done and how to test it, and suggest updates if it doesn't.
  - If there isn't one, recommend creating one, with a draft I can approve, before writing code.
  - The PR then links the issue ("Closes #N" or "Part of #N").

## Keeping GitHub records accurate

I want issues and PRs to say exactly what happened.

- **Closing keywords only when true.** Put "Closes #N" in a PR description only if merging that PR fully resolves #N and #N is still open. If it does part of the work, write "Part of #N". If the issue is already closed, just link it.
- **Keywords only work in two places**: a PR description when the PR is merged into `main`, and commit messages that land on `main`. Comments never close issues, and editing a merged PR's description doesn't either. If a merged PR finished an issue but didn't reference it, close the issue by hand with a comment that links the PR(s).
- **Reference related issues.** Besides the issue a PR is for, link other open issues the change touches.
- **Close superseded PRs** with a short comment saying what replaced them.
- **Update descriptions when things change.** If a PR's scope changes, or an issue item is done or no longer applies, edit the description so it stays accurate.
- **Issue style:** short sections (Problem, Fix or Options, How to test, Done when), checklists for multi-part work, and links to the related issues. "How to test" is required: say how to check the change works, such as the commands to run or what to look for on the Cloudflare preview.

## Repo layout

- `search.py`: Playwright scraper, run as a pytest test (`test_search_button_exists`), one run per zip code. Source: https://www.eastrise.com/personal/fuel-buying-program/ (Eastrise was formerly VSECU).
- `irving_oil_prices.csv`, `oil_prices_by_dealer.csv`: data. GitHub Actions (`.github/workflows/run.yml`) appends to these and commits to `main` daily. Don't edit them by hand, and branch from the latest `main` to avoid CSV conflicts.
- `notify.py`: daily ntfy phone notification. `.github/workflows/notify.yml` sends a real notification on PRs that change it.
- `of/`: the website, an Observable Framework project. Cloudflare Pages builds it from `of/` (only changes under `of/` trigger a build).
  - Production: https://log-heating-oil-price.pages.dev/
  - Every branch gets a preview at `https://<branch-name-with-slashes-as-dashes>.log-heating-oil-price.pages.dev/`.
  - The page loads its data from the CSV on `main` (raw.githubusercontent.com), so previews always show `main`'s data.
- The old Panel/Pyodide site and GitHub Pages hosting are gone (#28). Don't bring them back.
- `run.yml` is pinned to `ubuntu-24.04` because the locked Playwright can't install webkit on newer Ubuntu (#20).

## Tooling

- Python: [uv](https://docs.astral.sh/uv/) (`pyproject.toml`, `uv.lock`). Run `uv sync`.
- Website: npm with `package-lock.json`. In `of/`, run `npm ci`, not `npm install`.

## Checks before pushing

- Python changes: `uv lock --check` and `uv run pytest --collect-only -q search.py`. A real scrape needs `playwright install webkit` and hits the live site, so only run it when the scraper changes.
- Notifier changes: `python3 notify.py --dry-run`.
- Website changes: `cd of && npm ci && npm run build`, with no warnings. Then check the Cloudflare preview for the PR.
