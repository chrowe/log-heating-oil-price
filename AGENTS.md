# AGENTS.md

Notes for AI coding agents working in this repo. See README.md for what the project does.

## What this is for

A personal tool for buying heating oil at the best price. Every day it scrapes dealer prices from the Eastrise fuel buying program, shows the history on a website, and sends a phone notification with the price and how it has changed.

- **Main decision: when to buy oil for my house** (zip 05048, currently from Irving) to get the cheapest price.
- **Second decision: which dealer to use.** My partner lives in 05602 and uses a different dealer, not Irving. That's why the scraper records every dealer in both zip codes: so each of us can compare our options, and compare the two areas.
- **Users:** just me and my partner.
- **Also for fun:** I like knowing the numbers and playing with the data, and the project is a way to learn new tools (it started as a way to learn Python, and the site moved to Observable Framework partly to try it out).

## How I like to work

- **Act like a product manager, not an order-taker.** My requests are often brief. Before building:
  - Work out what I'm trying to achieve and why, given what this app is for.
  - If my intent isn't clear, ask me questions. Don't guess.
  - If there's a better or simpler way to meet the need than what I asked for, suggest it, and explain the trade-off. Don't treat my request as the spec.
- **Use existing tools first.** Before building something, check for an open source tool that already does it and suggest that. I'd rather contribute to an existing project than start a new one.
- **Ask before outward-facing actions I didn't request**, such as closing issues, commenting, or merging. Once I say yes, do it without asking again.
- **In chat, link issues and PRs with their titles.** Write [#41 Roadmap: order of work](https://github.com/chrowe/log-heating-oil-price/issues/41), not a bare "#41". On GitHub, a bare `#41` is fine, because GitHub links it and shows a preview on hover.
- **Check the roadmap for priorities.** [issue #41](https://github.com/chrowe/log-heating-oil-price/issues/41) sets the order of work. Fetch the current list of open issues before suggesting new ones, since issues are often added between sessions.
- **Every PR starts from an issue.** When I ask for a change, don't go straight to a PR. First look for an open issue that covers the work.
  - If there is one, check it says what will be done and has a "Done when" section whose items can each be checked. Suggest updates if it doesn't.
  - If there isn't one, recommend creating one, with a draft I can approve, before writing code.
  - The PR then links the issue ("Closes #N" or "Part of #N").

## Keeping GitHub records accurate

I want issues and PRs to say exactly what happened.

- **Closing keywords only when true.** Put "Closes #N" in a PR description only if merging that PR fully resolves #N and #N is still open. If it does part of the work, write "Part of #N". If the issue is already closed, just link it.
- **Keywords only work in two places**: a PR description when the PR is merged into `main`, and commit messages that land on `main`. Comments never close issues, and editing a merged PR's description doesn't either. If a merged PR finished an issue but didn't reference it, close the issue by hand with a comment that links the PR(s).
- **Say whether a number is a PR or an issue.** In repo files like this one, write `PR #N` or `issue #N`, not a bare `#N`. GitHub numbers issues and PRs from one sequence, so a bare number doesn't say which it is.
- **Reference related issues.** Besides the issue a PR is for, link other open issues the change touches.
- **Close superseded PRs** with a short comment saying what replaced them.
- **Update descriptions when things change.** If a PR's scope changes, or an issue item is done or no longer applies, edit the description so it stays accurate.
- **Issue style:** short sections (Problem or Why, Fix or Idea, Done when), checklists for multi-part work, and links to the related issues. "Done when" is required, and each item must say how to check it. For example, "With a CSV whose last row is old, the site shows the banner", not "Stale data is handled". Don't add a separate "How to test" section. Generic checks are in "Checks before pushing" below.

## Issue status

Use GitHub's issue statuses ([announcement](https://github.blog/changelog/2026-11-23-issue-statuses-and-repository-boards-are-in-public-preview/)) to show where each issue is:

| Status | When |
|---|---|
| Backlog | New issues and ideas we haven't decided to do |
| Todo | Chosen at a planning check-in (a comment on issue #41) and added to that batch's milestone, named "Batch N" (e.g. Batch 1). See "How we pick what's next" in issue #41 |
| In progress | Work has started: a draft PR is open |
| In review | The PR is ready for review |
| Done | The PR is merged |
| Not planned | We decided not to do it. Close with reason "not planned" and a comment saying why |
| Duplicate | Another issue covers it. Close with reason "duplicate" and link the other issue |

- **Let GitHub's automation do the moves where it can.** Linking a draft PR to an issue moves it to In progress, and marking the PR ready for review (or linking an open PR) moves it to In review. So open PRs as drafts while working, and mark them ready when the work and checks are done.
- **"Part of #N" doesn't link a PR to the issue**, so it won't move the status. For partial work, set the status by hand or link the PR from the issue's Development sidebar.
- **If a status didn't change as expected, or your tools can't set it, say so** and ask me to set it, rather than leaving it wrong.

## Repo layout

- `search.py`: scraper, run as a pytest test (`test_scrape_prices`), one run per zip code. Source: https://www.eastrise.com/personal/fuel-buying-program/ (Eastrise was formerly VSECU).
  - JSON first (#50): it downloads the page once with `urllib` and parses the dealer JSON the page embeds (`var vsecuVheatDealers = [...]`). It checks the result (every zip has oil prices, Irving is listed for 05048, prices are $1–$15) before trusting it.
  - Playwright fallback: if the JSON step fails, the run drives the page with Playwright as before, prints a `::warning::` with the reason, and `notify.py` adds a line about it to that day's notification.
  - `SCRAPE_SOURCE=json` or `SCRAPE_SOURCE=playwright` forces one path, e.g. to compare them.
- `irving_oil_prices.csv`, `oil_prices_by_dealer.csv`, `scrape_log.csv`: data. GitHub Actions (`.github/workflows/run.yml`) appends to these and commits to `main` daily. `scrape_log.csv` has one line per run (`date,source,detail`): whether prices came from `json` or `playwright` and, for a fallback, why. Don't edit them by hand, and branch from the latest `main` to avoid CSV conflicts.
- `notify.py`: daily ntfy phone notification. `.github/workflows/notify.yml` sends a real notification on PRs that change it.
- `.github/workflows/claude-code-review.yml`: Claude reviews every non-draft PR from a branch in this repo and posts inline comments. It skips PRs from forks and from Dependabot, which don't get the repo secret below. Treat its findings like any other review: fix them or reply explaining why not. It also skips PRs that change `claude-code-review.yml` itself, because the action only runs when that file matches `main`. If your PR edits it, tell Chris in the PR description and in chat that it needs a manual review. `.github/workflows/claude.yml` answers `@claude` mentions in issues and PRs. Both use the `CLAUDE_CODE_OAUTH_TOKEN` repo secret (issue #44).
- `of/`: the website, an Observable Framework project. Cloudflare Pages builds it from `of/` (only changes under `of/` trigger a build).
  - Production: https://log-heating-oil-price.pages.dev/
  - Every branch gets a preview at `https://<branch-name-with-slashes-as-dashes>.log-heating-oil-price.pages.dev/`.
  - The page loads its data from the CSV on `main` (raw.githubusercontent.com), so previews always show `main`'s data.
- The old Panel/Pyodide site and GitHub Pages hosting are gone (PR #28). Don't bring them back.
- `run.yml` installs webkit only when it's needed (issue #56). It first runs the scrape with `SCRAPE_SOURCE=json`, which needs no browser. Only if that step fails does it install webkit, reset the data CSVs, and run the normal scrape, which tries the JSON again and falls back to Playwright, logging why. So the `scrape_log.csv` reason comes from that second JSON attempt.
- `run.yml` is pinned to `ubuntu-24.04` because the locked Playwright can't install webkit on newer Ubuntu (issue #20).

## Tooling

- Python: [uv](https://docs.astral.sh/uv/) (`pyproject.toml`, `uv.lock`). Run `uv sync`.
- Website: npm with `package-lock.json`. In `of/`, run `npm ci`, not `npm install`.

## Checks before pushing

- Python changes: `uv lock --check` and `uv run pytest --collect-only -q search.py`. A real scrape hits the live site, so only run it when the scraper changes. The JSON path needs no browser; testing the fallback (`SCRAPE_SOURCE=playwright`) needs `playwright install webkit`.
- Notifier changes: `python3 notify.py --dry-run`.
- Website changes: `cd of && npm ci && npm run build`, with no warnings. Then check the Cloudflare preview for the PR.
