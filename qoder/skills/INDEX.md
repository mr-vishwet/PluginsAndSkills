# Qoder skill index

All 20 user skills. Each row links to its `SKILL.md` for the full instructions.
Most skills activate from their description. `gsd`, `ralph`, and `rea` are also
invoked by name, for example `/gsd new-project`.

| Skill | Use it when | Runtime needs |
| --- | --- | --- |
| [app-demo-recorder](app-demo-recorder/SKILL.md) | Recording an Android walkthrough, removing client branding, adding chapter captions, writing a timecoded session doc | `adb`, `ffmpeg`, Pillow, pinned `.venv` |
| [app-store-assets](app-store-assets/SKILL.md) | Making or refreshing Play Store and App Store graphics at exact sizes | Chrome, macOS `sips` |
| [brand-flow](brand-flow/SKILL.md) | Extracting a live site's brand tokens and full page flow, then generating screens | Node, Python 3, browser evaluate |
| [cloudflare-free-deploy](cloudflare-free-deploy/SKILL.md) | Scaffolding and deploying a free Cloudflare Worker, static site, D1, KV, R2, or Queue | `wrangler`, Node |
| [coding-decisions](coding-decisions/SKILL.md) | Any code-writing or review task; default scope, comment, and verification rules | None |
| [daily-summary](daily-summary/SKILL.md) | A task sheet, daily plan, recap, or completion checklist in plain language | None |
| [docs-skill](docs-skill/SKILL.md) | Generating a DOCX or PDF from Markdown with branded cover, TOC, tables, and footers | `python-docx`, `reportlab` |
| [git-to-obsidian](git-to-obsidian/SKILL.md) | Mapping recent git changes into the correct Obsidian vault notes | Git, vault path |
| [gsd](gsd/SKILL.md) | Initializing a project, mapping a codebase, writing a roadmap, planning or executing phases, UAT, milestone audits | Node, Git |
| [gsd-map-codebase](gsd-map-codebase/SKILL.md) | Running the standalone codebase mapping entry point | Node, Git |
| [gsd-plan-milestone-gaps](gsd-plan-milestone-gaps/SKILL.md) | Converting audit gaps into closure phases | Node, Git |
| [gsd-project-researcher](gsd-project-researcher/SKILL.md) | Researching the domain and ecosystem for a new project | Node, Git, web access |
| [gsd-verify-work](gsd-verify-work/SKILL.md) | Running conversational UAT on built features | Node, Git |
| [kill-the-vibecode](kill-the-vibecode/SKILL.md) | Designing, building, restyling, or reviewing any website or web app | Bash, browser |
| [kill-the-vibecode-mobile](kill-the-vibecode-mobile/SKILL.md) | The same for Flutter, SwiftUI, Compose, React Native, and mobile web | Bash |
| [lily-autoresearch](lily-autoresearch/SKILL.md) | Running an overnight experiment loop evaluated against an Obsidian vault | Python 3, vault path |
| [mobile-app-ui-design](mobile-app-ui-design/SKILL.md) | Designing mobile screens, flows, onboarding, navigation, and components | None |
| [ponytail](ponytail/SKILL.md) | Always, through `AGENTS.md`; also usable directly for engineering standards | None |
| [ralph](ralph/SKILL.md) | Turning a feature into a PRD and looping one story at a time until tests pass | `jq`, Git, an agent CLI |
| [rea](rea/SKILL.md) | Reverse-engineering a native, managed, Electron, firmware, or browser target | External REA MCP for tool-backed work |

## Notes

- `app-demo-recorder` was a symlink on the source machine. It is a real folder
  here, with its scripts and tests, but not its virtual environment.
- `git-to-obsidian` hardcodes the source vault. Edit it before use.
- `lily-autoresearch` expects the project's `.envs/lily.env` with `VAULT_PATH`.
- The five `gsd-*` folders are convenience entry points. The full system lives in
  `gsd/`, which contains its own `agents/`, `skills/`, `workflows/`, and templates.
