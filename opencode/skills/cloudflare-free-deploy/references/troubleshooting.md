# Troubleshooting

Match the symptom, then apply the fix. Each entry is a failure mode that actually happens on the free plan.

## Error 1027 — "exceeded allotted requests"

The 100k/day account cap is spent; the Worker returns 1027 for everyone until 00:00 UTC. No bill. Before blaming traffic, look for self-inflicted loops:

- A frontend that polls an endpoint every second — 86k hits/day from a single open tab.
- A public endpoint with no rate limit getting scanned by bots.
- A Worker calling itself through its own public URL instead of `env.SELF.fetch()`.

Check real numbers in the dashboard under Workers & Pages → Observability, or stream with `npx wrangler tail`.

## `node` / `npx` not found right after installing Node

The shell's environment predates the install. Do not re-run the installer. Either start a new session or call the binary by full path:

```sh
"/c/Program Files/nodejs/npx" wrangler --version
```

`preflight.sh` appends the usual install dirs to PATH for exactly this reason — run it instead of debugging by hand.

## Deploy succeeds but there is no workers.dev URL

New accounts often ship without a subdomain. Claim one:

```sh
npx wrangler subdomain my-name
```

or enable it at Workers & Pages → Settings → Subdomain. If the visitor's network blocks `workers.dev` rather than the subdomain being missing, route the Worker on a domain you control instead — Worker routes on a Cloudflare zone cost nothing.

## D1 says "no such table", but only in one environment

Local and remote D1 are two separate SQLite databases, and `wrangler dev` uses the local one unless passed `--remote`. Applying the schema to only one side is the most common cause of "works locally, 500s in production".

```sh
npx wrangler d1 execute my-db --local  --file=./schema.sql
npx wrangler d1 execute my-db --remote --file=./schema.sql
```

Inspect either side with `--command="SELECT name FROM sqlite_master"` plus `--local` or `--remote`.

## 500 on the first request after a successful deploy

A binding exists in code but not in the deployed environment.

```sh
npx wrangler secret list
```

Remember `.dev.vars` is local-only and gitignored — every value in it must be re-created with `npx wrangler secret put NAME` before it exists in production. Plain non-secret config belongs in `vars` inside `wrangler.jsonc`.

## CORS blocked in the browser

Handle `OPTIONS` before routing, and set the header on the actual response, not only on the preflight. For a public demo, `Access-Control-Allow-Origin: https://your-site.example` beats `*`; reflecting arbitrary origins alongside `Allow-Credentials: true` is a real vulnerability, not a shortcut.

## SPA deep links 404

In the `assets` block set `"not_found_handling": "single-page-application"`, and keep `"run_worker_first": false` unless the Worker genuinely needs to intercept asset requests — with it set to `true`, every static path goes through your handler first and 404s unless you explicitly fall back to `env.ASSETS.fetch(request)`.

## `wrangler deploy` refuses the config

Validate cheaply with `npx wrangler dev`, which parses `wrangler.jsonc` before serving. Usual causes: missing or very old `compatibility_date`, a `name` that breaks npm/Worker naming rules (lowercase, digits, internal hyphens only — `new-project.sh` enforces this), duplicate binding names, or JSONC comments closed incorrectly.

## Build works locally, fails in Cloudflare CI

The build image runs a pinned Node and a clean cache. Reproduce with `rm -rf node_modules && npm ci` before pushing, and commit a lockfile — without one the CI install and the local install are different trees.

## "I want websockets / a background worker that never sleeps"

Not a free-plan fit. Say so rather than deploying something that sleeps, misses events, or exhausts CPU at 10 ms. Options are the Paid plan, or a genuinely always-on free VM (Oracle Cloud Always Free) accepting that signup capacity is unreliable.
