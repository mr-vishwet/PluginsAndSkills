# Cloudflare Free Tier — Verified Quotas

Checked 2026-11-05 against `developers.cloudflare.com/workers/platform/pricing` and `.../limits`. Re-verify before quoting these to a client — Cloudflare has revised these numbers before, and third-party "free hosting compared" posts are routinely out of date.

## Compute (Workers, $0 plan)

| Item | Free limit |
|---|---|
| Requests | 100,000 per day, resets 00:00 UTC |
| CPU per invocation | 10 ms |
| Subrequests per invocation | 50 |
| Workers per account | 100 |
| Cron triggers | 5 |
| Bundled workers (Node runtime) | not available on free |

Exceed the daily request cap and every further request returns **Error 1027** and stops serving until midnight UTC. The free plan throttles; it never bills. There is no surprise invoice path.

## Static assets

- Unlimited requests and unlimited bandwidth — this is the part of "unlimited projects" that is actually true.
- 20,000 files per Worker version.
- 25 MiB per individual file.
- 500 builds per month across the account when deploying through CI build pipelines.

## Storage and plumbing

| Service | Free quota |
|---|---|
| D1 | 5 GB stored; 5M rows read/day; 100k rows written/day |
| KV | 1 GB stored; 100k reads/day; 1k writes/day |
| R2 | 10 GB stored; 1M Class A ops/month; 10M Class B ops/month; **zero egress fees** |
| Queues | 10k operations/day |
| Workflows | 100k requests/day; 1 GB-month storage |
| Hyperdrive | 100k queries/day |

## Free regardless of plan

Turnstile (captcha), custom domains and Worker routes on a zone already on Cloudflare, TLS, analytics/logs basics, preview URLs, unlimited public and private Git-connected projects.

## What still costs money

- **A domain name**, roughly $10-12/yr. `*.workers.dev` and `*.pages.dev` are free but a large fraction of corporate, school and public-library networks block the shared `workers.dev` domain. Anything a recruiter will click from an office laptop needs a real domain or a Cloudflare-managed zone.
- **Always-on processes.** No containers, no VMs, no persistent sockets, no cron-style daemons. If the requirement is "a server that stays up", free Cloudflare is the wrong answer — Oracle Cloud Always Free is the honest alternative, with spotty capacity at signup.
- **Outbound email at volume.** Sending from a Worker is restricted on the free plan; call a transactional email API over HTTPS from the Worker instead, or accept that SMTP needs a paid service.
- **CPU beyond 10 ms.** Image processing, hashing, and large JSON transforms spill over this almost immediately.

## Signals to upgrade

1. Sustained Error 1027 with legitimate traffic → Paid at $5/mo, which removes the request cap and raises CPU.
2. Any endpoint needing more than 10 ms → refactor into Queues/Workflows, or move to Paid.
3. R2 past 10 GB → $0.015/GB-month, still no egress charge, usually far cheaper than S3 + egress.

## Honest summary for a "zero cost, unlimited projects" request

Unlimited **sites** and unlimited **bandwidth**: yes. Unlimited **compute**: no — 100k requests/day per account is the ceiling, shared across every Worker on it. Say so up front rather than discovering it on a day the project gets linked from somewhere popular.
