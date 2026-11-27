# AGENTS.md

Notes for AI coding agents working in this repo. See README.md for what the project does.

## How I like to work

- **Use existing tools first.** Before building something, check for an open source tool that already does it and suggest that. I'd rather contribute to an existing project than start a new one.
- **Do what's asked.** When I ask for a change or a PR, make it. Don't come back with a plan to approve first unless I ask for one or the request is unclear.
- **Ask before outward-facing actions I didn't request**, such as closing issues, commenting, or merging. Once I say yes, do it without asking again.

## Keeping GitHub records accurate

I want issues and PRs to say exactly what happened.

- **Closing keywords only when true.** Put "Closes #N" in a PR description only if merging that PR fully resolves #N and #N is still open. If it does part of the work, write "Part of #N". If the issue is already closed, just link it.
- **Keywords only work in two places**: a PR description when the PR is merged into `main`, and commit messages that land on `main`. Comments never close issues, and editing a merged PR's description doesn't either. If a merged PR finished an issue but didn't reference it, close the issue by hand with a comment that links the PR(s).
- **Check related issues before opening a PR.** Read the open issues and reference the ones the change touches.
- **Close superseded PRs** with a short comment saying what replaced them.
- **Update descriptions when things change.** If a PR's scope changes, or an issue item is done or no longer applies, edit the description so it stays accurate.
- **Issue style:** short sections (Problem, Fix or Options, Done when), checklists for multi-part work, and links to the related issues.

## Repo layout

- `search.py`: Playwright scraper, run as a pytest test (`test_scrape_prices`), one run per zip code. Source: https://www.eastrise.com/personal/fuel-buying-program/ (Eastrise was formerly VSECU).
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
