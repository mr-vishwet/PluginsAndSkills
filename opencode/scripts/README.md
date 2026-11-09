# Local bridge scripts

These convert an OpenAI-compatible chat request into whatever the upstream
service actually speaks. They are optional: start only the ones your providers
need. Each runs in the foreground, so use `tmux`, `nohup`, or a launch agent if it
should survive a terminal closing.

None of them is wired into the current `opencode.json`; the live providers are
`ox-alpha`, `omniroute`, and `explabs`. Keep them as the reference
implementation when you add one of those providers back.

| Script | Listen | Upstream | Python deps | Secret source |
| --- | --- | --- | --- | --- |
| `pplx-direct.py` | `127.0.0.1:8001` (optional first argument) | Perplexity web SSE endpoint | standard library only | `PERPLEXITY_SESSION_TOKEN` env plus `pplx-meta.json` |
| `pplx-proxy.py` | `127.0.0.1:8001` | `127.0.0.1:8000`, the Perplexity web UI scraper | `fastapi`, `uvicorn` | owned by the scraper |
| `kaggle-proxy.py` | `127.0.0.1:8017` | A Kaggle Ollama tunnel, currently an ephemeral `trycloudflare.com` host | `fastapi`, `uvicorn` | none |
| `omnirush-bridge.py` | `127.0.0.1:3901` by default | `https://omnirush.ai/omnirush/v1` | standard library only | `~/.omnirush/auth.json`, field `accessToken` |
| `omnirush-bridge-cli.py` | `127.0.0.1:3902` by default | The local `omnirush` CLI, using its native login | standard library only | the CLI's own session |

## Perplexity

`pplx-direct.py` is the newer single-process option. It replaces the old pair of
the web UI scraper on port 8000 and `pplx-proxy.py` on port 8001.

```bash
export PERPLEXITY_SESSION_TOKEN='...'      # __Secure-next-auth.session-token
cp ~/.config/opencode/pplx-meta.template.json ~/.config/opencode/pplx-meta.json
# fill cookie and account in pplx-meta.json from a logged-in browser session
python3 ~/.config/opencode/scripts/pplx-direct.py
```

The cookie expires. When Perplexity starts rejecting requests, refresh both the
env token and the cookie fields. This is the credential that produced the
523-character `pplx-pro` key in the old config, so do not paste it into a repo.

`pplx-proxy.py` is only needed if you still run the scraper:

```bash
python3 -m pip install fastapi uvicorn
python3 ~/.config/opencode/scripts/pplx-proxy.py
```

It forwards to port 8000 and strips the `tools` field because the scraper models
do not support tool calling.

## Kaggle Ollama

```bash
python3 ~/.config/opencode/scripts/kaggle-proxy.py
```

The upstream host in the script is a temporary Cloudflare tunnel. When the tunnel
rotates, edit the `UPSTREAM_HOST` constant at the top of the file. The proxy also
normalizes system-message ordering and removes tools for the same compatibility
reason.

`kaggle-proxy.py` logs to `~/.config/opencode/kaggle-proxy.log` on the source
machine; the log is not part of the export.

## Omnirush

Two bridges exist because Omnirush has two auth paths.

```bash
# Reads ~/.omnirush/auth.json, token saved by the web login
python3 ~/.config/opencode/scripts/omnirush-bridge.py 3902

# Shells out to the omnirush CLI, uses its native session
python3 ~/.config/opencode/scripts/omnirush-bridge-cli.py
```

The config points `omnirush` at port 3902, which matches the CLI bridge's default.
If you use the JSON-token bridge instead, pass `3902` explicitly or change the
provider base URL.

Both bridges expose the same model IDs: `gpt-6-astra`, `gpt-6-sol`, and
`gpt-5.6-sol`. The CLI bridge also answers `gpt-6.1-sol` on its model list.

## Install dependencies

Only the two FastAPI proxies need packages:

```bash
python3 -m pip install fastapi uvicorn
```

A virtual environment is fine; just run the script with that interpreter.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `connection refused` from OpenCode | The bridge is not running, or the port does not match the provider base URL |
| 401 or 403 from Perplexity | Expired session token or cookie |
| 404 from Kaggle | The Cloudflare tunnel host changed |
| Tool calls ignored | Expected on the scraper-backed models; the proxies strip tools |
| `ModuleNotFoundError: fastapi` | Installed into a different Python than the one running the script |
