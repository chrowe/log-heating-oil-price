// Run with: node scheduler/test.mjs
import assert from "node:assert/strict";
import { dispatch } from "./src/index.js";

const env = { GITHUB_REPO: "o/r", WORKFLOW: "run.yml", REF: "main", GITHUB_TOKEN: "t" };
globalThis.setTimeout = (fn) => fn(); // skip retry waits

// Success: one POST to the dispatches endpoint with ref main.
let calls = [];
await dispatch(env, async (url, init) => {
  calls.push({ url, init });
  return new Response(null, { status: 204 });
});
assert.equal(calls.length, 1);
assert.equal(calls[0].url, "https://api.github.com/repos/o/r/actions/workflows/run.yml/dispatches");
assert.equal(calls[0].init.method, "POST");
assert.equal(calls[0].init.headers.Authorization, "Bearer t");
assert.deepEqual(JSON.parse(calls[0].init.body), { ref: "main" });

// Server error: retried, then succeeds.
calls = [];
await dispatch(env, async () => {
  calls.push(1);
  return calls.length < 2 ? new Response("oops", { status: 502 }) : new Response(null, { status: 204 });
});
assert.equal(calls.length, 2);

// Bad token: not retried, and the error is thrown.
calls = [];
await assert.rejects(
  dispatch(env, async () => {
    calls.push(1);
    return new Response("Bad credentials", { status: 401 });
  }),
  /HTTP 401/,
);
assert.equal(calls.length, 1);

// Network error every time: three attempts, then thrown.
calls = [];
await assert.rejects(dispatch(env, async () => { calls.push(1); throw new Error("down"); }), /down/);
assert.equal(calls.length, 3);

console.log("scheduler tests passed");
