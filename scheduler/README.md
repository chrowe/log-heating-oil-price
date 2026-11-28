# scheduler

A Cloudflare Worker that starts the daily scrape (`.github/workflows/run.yml`) at **19:04 UTC** every day (issue #51).

GitHub's own `schedule` trigger runs hours late on free runners, which made the capture time unpredictable and pushed runs past midnight. A `workflow_dispatch` call through GitHub's API starts a run within seconds, so this Worker makes that call on a Cloudflare Cron Trigger, which fires on time. The `schedule` in `run.yml` stays as a backup for days the Worker fails: it skips itself if a `workflow_dispatch` run already succeeded in the last 20 hours, so a normal day gets one scrape and one notification.

- `src/index.js`: sends `POST /repos/chrowe/log-heating-oil-price/actions/workflows/run.yml/dispatches` with `{"ref":"main"}`. It retries twice, 30 seconds apart, unless GitHub rejects the token.
- `wrangler.toml`: the cron time (UTC) and repo settings. The Worker has no public URL.
- `GITHUB_TOKEN`: an encrypted Worker secret, never in the repo.

## Setup (once)

1. **Create the token** at GitHub → Settings → Developer settings → [Fine-grained tokens](https://github.com/settings/personal-access-tokens/new):
   - Repository access: *Only select repositories* → `log-heating-oil-price`.
   - Permissions: **Actions: Read and write**. Nothing else (GitHub adds Metadata: read-only itself).
   - Expiration: up to a year. Put a reminder in your calendar a week before it expires.
2. **Deploy the Worker** from this folder (it opens a browser to log in to Cloudflare the first time):
   ```
   cd scheduler
   npx wrangler@4 deploy
   npx wrangler@4 secret put GITHUB_TOKEN   # paste the token
   ```
3. **Check it** the next day: Actions → Run script should show a `workflow_dispatch` run that started at about 19:04 UTC. Cloudflare's dashboard (Workers → log-heating-oil-price-scheduler → Logs) shows each cron run and any error.

## Changing it

- New time: edit `crons` in `wrangler.toml` (UTC; Cloudflare doesn't do daylight saving) and run `npx wrangler@4 deploy` again. Keep the backup `schedule` in `run.yml` after it.
- New token: `npx wrangler@4 secret put GITHUB_TOKEN`.
- Turn it off: `npx wrangler@4 delete`, or remove the cron in the Cloudflare dashboard. The backup schedule keeps running.

## Testing

```
node test.mjs                                  # unit tests, no network
echo 'GITHUB_TOKEN=<token>' > .dev.vars        # .dev.vars is git-ignored
npx wrangler@4 dev --test-scheduled            # then, in another terminal:
curl "http://localhost:8787/__scheduled?cron=4+19+*+*+*"
```
The `curl` starts a real scrape run if the token is valid.
