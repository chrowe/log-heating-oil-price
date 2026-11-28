// Starts the daily scrape (.github/workflows/run.yml) on time.
// GitHub's own `schedule` trigger runs hours late (issue #51), but a
// workflow_dispatch call starts within seconds. Cloudflare runs this at the
// cron time in wrangler.toml; GITHUB_TOKEN is an encrypted Worker secret.

const ATTEMPTS = 3;
const RETRY_DELAY_MS = 30_000;

export async function dispatch(env, fetchImpl = fetch) {
  const url = `https://api.github.com/repos/${env.GITHUB_REPO}/actions/workflows/${env.WORKFLOW}/dispatches`;
  let lastError;
  for (let attempt = 1; attempt <= ATTEMPTS; attempt++) {
    try {
      const res = await fetchImpl(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "log-heating-oil-price-scheduler",
        },
        body: JSON.stringify({ ref: env.REF }),
      });
      if (res.ok) {
        console.log(`Started ${env.WORKFLOW} on ${env.REF} (HTTP ${res.status})`);
        return;
      }
      lastError = new Error(`GitHub returned HTTP ${res.status}: ${await res.text()}`);
      // A bad or expired token won't fix itself, so don't retry it.
      if (res.status === 401 || res.status === 403 || res.status === 404) break;
    } catch (err) {
      lastError = err;
    }
    console.warn(`Attempt ${attempt} failed: ${lastError.message}`);
    if (attempt < ATTEMPTS) await new Promise((r) => setTimeout(r, RETRY_DELAY_MS));
  }
  // Throwing marks this cron run as failed in the Cloudflare dashboard.
  // GitHub's backup schedule in run.yml still runs later that day.
  throw lastError;
}

export default {
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(dispatch(env));
  },
};
