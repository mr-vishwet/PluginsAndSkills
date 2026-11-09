# OpenCode providers

Three providers are configured. Two point at a local service; one is a remote
API. Local keys are dummy values, the remote key is read from the environment.

## Provider table

| ID | Name in config | Base URL | Kind | Models |
| --- | --- | --- | --- | --- |
| `ox-alpha` | Ox Alpha | `http://localhost:3900/v1` | local | `ox-alpha` |
| `omniroute` | OmniRoute | `http://localhost:20128/v1` | local | 10 auto and vendor-routed models |
| `explabs` | Experiential Labs | `https://api.experientiallabs.ai/v1` | remote | 30 models |

All providers use the `@ai-sdk/openai-compatible` adapter.

Keys:

- `ox-alpha` — `oxalpha-chat`, a fixed dummy key for the local service.
- `omniroute` — `YOUR_OMNIROUTE_API_KEY` in the template; replace it with the key
  from the OmniRoute install.
- `explabs` — `{env:EXPLABS_API_KEY}`, so the config stays free of the secret.

Defaults:

- `model`: `opencode/big-pickle`
- `small_model`: `opencode/mimo-v2.5-free`

`opencode/*` refers to models served by the OpenCode provider, not by one of the
three listed above. Keep those defaults only if the new install can reach them.

## Which local service backs which port

| Port | Provider | Started by |
| --- | --- | --- |
| 3900 | `ox-alpha` | The ox-alpha local service, paired with `plugin/oxalpha-chat.ts` |
| 20128 | `omniroute` | OmniRoute, installed separately |

Only start the ones you use. A provider whose port is closed shows up as a
connection error, not as a missing model.

## Free Claude Code

FCC is a fourth model source, but it is not saved into `opencode.json`. The
`fcc-opencode` launcher builds a process-local config with provider ID
`free-claude-code`, key `{env:FCC_OPENCODE_API_KEY}`, and a model list from the
running proxy. Detail in [../fcc/README.md](../fcc/README.md).

## Legacy bridge scripts

The scripts under `scripts/` still work, but the current template does not start
them and no provider points at their ports. Add a provider back if you want one:

| Script | Port | Old provider |
| --- | --- | --- |
| `pplx-direct.py` | 8001 | `pplx-pro` |
| `pplx-proxy.py` | 8001 | `pplx-pro` |
| `kaggle-proxy.py` | 8017 | `kaggle-ollama` |
| `omnirush-bridge.py` | 3901 or 3902 | `omnirush` |
| `omnirush-bridge-cli.py` | 3902 | `omnirush` |

## Adding a provider

```json
"my-provider": {
  "name": "My Provider",
  "npm": "@ai-sdk/openai-compatible",
  "options": {
    "baseURL": "https://api.example.com/v1",
    "apiKey": "{env:MY_PROVIDER_KEY}"
  },
  "models": { "my-model": { "name": "My Model" } }
}
```

Then select it with `opencode --model my-provider/my-model` or set `model` in the
config.

## Verify

```bash
# JSON parses
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null && echo ok

# Local ports that should be listening
for p in 3900 20128; do
  nc -z 127.0.0.1 "$p" && echo "$p open" || echo "$p closed"
done
```

A closed port is only a problem if you intend to use that provider.
