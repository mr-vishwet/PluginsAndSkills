---
name: cloudflare-free-deploy
description: Scaffold and deploy Cloudflare projects on the $0 plan using wrangler — Workers, static-asset sites, D1, KV, R2, Queues and Turnstile. Use when the user wants free hosting without a credit card, asks what Cloudflare's free tier actually allows, wants a portfolio/resume/toolkit project deployed, compares Cloudflare against Vercel, Netlify, Render or Railway for zero-cost hosting, or hits Error 1027. Also use to create a wrangler.jsonc project from scratch.
---

# Cloudflare Free-Tier Deploy

## Overview

Take a project from nothing to a live `*.workers.dev` URL without a card and without a bill. Every limit quoted here was checked against Cloudflare's docs; read `references/free-tier-limits.md` before promising someone "unlimited".

## Step 1 — Preflight

Run this first, every time. It fixes the PATH problem that catches most Windows sessions and reports auth state:

```sh
sh <skill-dir>/scripts/preflight.sh
```

Interpret the `next:` line it prints. Do not assume `node` is on PATH just because it was installed — a session started before the install has a stale environment, which is why the script appends `/c/Program Files/nodejs` itself.

## Step 2 — Route the need to a product

| The user wants | Use | Free ceiling |
|---|---|---|
| A site, docs, landing page | Worker + `assets` binding | Unlimited requests, 20k files/version |
| An API, webhook, proxy | Worker | 100k req/day, 10ms CPU each |
| Store form submissions, users, rows | D1 | 5GB, 5M reads / 100k writes per day |
| Serve uploads, images, backups | R2 | 10GB, **no egress fee** |
| Cache, config, session blobs | KV | 1GB, 100k reads / 1k writes per day |
| Stop bots on a contact form | Turnstile | Free, unlimited |
| A nightly job | Cron Triggers | 5 per Worker |

Do not reach for Pages as a separate product for new work — Cloudflare now ships static sites as Workers with an `assets` binding, so one `wrangler deploy` covers frontend and API together. Keep an existing Pages project on Pages.

Reject the request honestly when it needs an always-on process, WebSockets past 10ms CPU, or more than 100k hits a day. Free tier throttles; it does not bill.

## Step 3 — Scaffold

```sh
sh <skill-dir>/scripts/new-project.sh <static-site|worker-api|fullstack-d1> <project-name> [target-dir]
```

`fullstack-d1` is the one to reach for on resume work: static form, Worker handler, D1 insert, Turnstile verification, and an IP rate limiter already wired.

Then in the generated project:

```sh
cd <project-name> && npm install
```

## Step 4 — Develop locally, before any account exists

Local work needs no login and no card. Verified: `wrangler dev` and `wrangler d1 execute --local` both run happily against the template's placeholder `database_id`, so a newcomer can build and test the entire frontend + API + database flow before touching Cloudflare.

```sh
npx wrangler d1 execute <name>-db --local --file=./schema.sql   # fullstack-d1 only
npx wrangler dev                                                # http://localhost:8787
curl -s http://localhost:8787/api/health
```

Exercise the write path with a real POST and expect `{"ok":true}`; a missing schema surfaces as `D1_ERROR: no such table`, fixed by the line above.

## Step 5 — Authenticate and deploy

Only now is an account needed. `wrangler login` opens a browser and waits on a human — the agent cannot finish OAuth alone. Tell the user to run it, then confirm with `npx wrangler whoami`.

If they refuse to log in interactively, use an API token instead: have them set `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` in their shell, never in a committed file.

To show someone something live before any account exists, `npx wrangler deploy --temporary` pushes to a throwaway preview account — good for a quick share, gone in 24h and not a real deployment.

**Do not claim a production deploy before whoami returns an account.**

```sh
npx wrangler deploy
```

Report the exact URL printed by deploy. A deploy is not "done" until a live URL is in the transcript. Verify it with a real request:

```sh
curl -sS https://<name>.<subdomain>.workers.dev/api/health
```

For D1, remember local and remote are separate SQLite stores — apply the schema to `--remote` too, or the deployed site 500s while local dev looks perfect:

```sh
npx wrangler d1 execute <name>-db --remote --file=./schema.sql
```

## Step 6 — Guardrails

- Never commit `wrangler` OAuth output, API tokens, or `Turnstile secret`. Secrets go through `npx wrangler secret put NAME`.
- Free plan CPU is 10ms per invocation. Crypto, image work, or large JSON parsing will exceed it — move to Queues or accept the Paid plan.
- A project can be parked on a `*.workers.dev` subdomain for free, but that shared domain is frequently blocked by corporate and school networks. For anything on a CV, put it behind a route on a real domain.
- 500 builds/month and 100 Workers are the actual caps on the number of things you can have, not bandwidth.

## Resources

- `scripts/preflight.sh` — env + auth check, repairs Node PATH on Windows
- `scripts/new-project.sh` — copies a template and substitutes the project name
- `references/free-tier-limits.md` — verified quotas; read before answering "is this unlimited"
- `references/troubleshooting.md` — Error 1027, missing subdomain, D1 local/remote, CORS
