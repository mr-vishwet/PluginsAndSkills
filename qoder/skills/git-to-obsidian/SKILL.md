---
name: git-to-obsidian
description: Reads git changes from a project and maps them into the correct Obsidian vault notes — updates README, Architecture, Code Flow, Data Layer, App Flow, Screens, SOLID Principles, or KT Quickstart as the change warrants. Activates when the user says "git to obsidian", "map changes to obsidian", "recent changes obsidian", "list changes and map", "git log mapping", "update obsidian from git", "sync obsidian from repo", "git-to-obsidian", or explicitly asks to list recent changes and map them in the Obsidian vault.
---

# Git-to-Obsidian

Map git changes from project repos into the correct Obsidian vault notes.

## Context (fixed)

- **Vault**: `C:/Users/User/Desktop/Vishwet/Experiments/ObsessionWithObsedian`
- **Projects root (Mac)**: `C:/Users/User/Desktop/Vishwet/Appristine projects`
- **Source of Truth**: `[[Apps/_Source of Truth]]` in the vault
- **Note structure**: 8 notes per app, defined in `[[Apps/_Tone Guide]]`

## Input Parsing

From the user's message, extract:

1. **Project path** — if the user specifies one, use it. Otherwise, default to ALL apps under the Mac projects root (from Source of Truth).
2. **Scope** — if the user says "last week", "today", "last 5 commits", parse that. Otherwise default to last 10 commits.
3. **Specific apps** — if they name an app, limit to that app's repo.

## Workflow

### Step 1: Discover projects and run git

For each project directory, run:

```bash
cd "<project-path>" && git log --oneline -<n> --no-merges && echo "---DIFFSTAT---" && git diff --stat HEAD~<n> HEAD && echo "---FILELIST---" && git diff --name-only HEAD~<n> HEAD
```

Also run `git status` to catch uncommitted changes.

### Step 2: Categorize changes by file path

Map changed files to note types using these rules:

| Changed files/patterns | Notes to update |
|---|---|
| `lib/`, `app/src/main/java/`, `app/src/main/kotlin/`, `app/src/main/` (generic code) | Code Flow.md, Architecture.md |
| `ui/`, `screens/`, `widgets/`, `compose/`, `views/` | Screens.md, App Flow.md, Code Flow.md |
| `api/`, `network/`, `retrofit/`, `client/`, `endpoint` | Data Layer.md (APIs), Code Flow.md |
| `model/`, `data/`, `entity/`, `dto/`, `schema/` | Data Layer.md (Models), Architecture.md (Layers) |
| `db/`, `room/`, `database/`, `local/`, `cache/`, `storage/` | Data Layer.md (Database & Local Storage), Architecture.md |
| `nav/`, `navigation/`, `route/`, `graph` | App Flow.md (Navigation Graph), Code Flow.md (Navigation) |
| `state/`, `viewmodel/`, `provider/`, `bloc/`, `cubit/` | Architecture.md (State Management), Data Layer.md (State Management) |
| `di/`, `hilt/`, `dagger/`, `koin/`, `module/` | Architecture.md (Dependency Injection) |
| `build.gradle`, `build.gradle.kts`, `pubspec.yaml`, `Package.json`, `pom.xml`, `CMakeLists` | README.md (Platform & Stack), Architecture.md (Third-Party Choices) |
| `test/`, `testing/` | README.md (Known Gaps if gaps identified), SOLID Principles.md |
| `auth/`, `login/`, `token/`, `session/`, `biometric/` | Data Layer.md (Auth), Architecture.md |
| `utils/`, `helper/`, `extension/` | Code Flow.md (App Initialization if used at startup) |
| `manifest/`, `AndroidManifest.xml`, `Info.plist` | Architecture.md (Third-Party Choices), Screens.md (permissions) |
| `service/`, `worker/`, `background/`, `notification/` | App Flow.md (Screens & Roles), Code Flow.md (Feature Execution Path) |

If a changed file matches multiple rows, update all relevant notes.

### Step 3: Determine what to write in each note

For each note that needs updating, follow the Tone Guide heading contract and add a **Changes** section (or update the relevant sub-section):

**README.md** — update:
- `## Known Gaps` — remove items that are now implemented, add new gaps found
- `## Platform & Stack` — if dependencies or build config changed
- Add a `> **Recent Changes:**` block at top noting what changed and when

**Architecture.md** — update:
- `## Folder Structure` tree if paths added/removed
- `## Layers` if new layers or moved code
- `## Dependency Injection` if DI changed
- `## State Management` if state approach changed
- `## Third-Party Choices` if new libraries added

**Code Flow.md** — update:
- `## Feature Execution Path` if execution paths changed
- `## App Initialization` if startup sequence changed
- `## Navigation` if routes changed

**Data Layer.md** — update:
- `## APIs` if endpoints/clients changed
- `## Models` if data classes changed
- `## Database & Local Storage` if schema changed
- `## Auth` if auth flow changed

**App Flow.md** — update:
- `## Navigation Graph` if navigation changed
- `## Screens & Roles` if screen access changed
- `## Role / Access Matrix` if roles changed

**Screens.md** — update:
- `## Screen List` if screens added/removed
- `## Widgets` if reusable widgets changed

**SOLID Principles.md** — update:
- Add/remove `### Real Example` references citing changed files with `file:line`
- Update `### Honest Verdict` if principles applied/not changed

**KT Quickstart.md** — update:
- `### 2 hours — read the code` if key files changed
- `### Half day — make a change` if the onboarding task should reflect new reality

### Step 4: Generate and write notes

For each note to update:
1. Read the existing note from the vault
2. Apply changes using the **Changes** section pattern — add a clearly marked section at the end:

```markdown
---
## Recent Changes (YYYY-MM-DD)

- **What changed:** <plain-language description>
- **Files affected:** `path/to/file.ext` (from `<project-root>`)
- **Impact:** <how this affects developers using this note>
```

3. Write the updated note back

### Step 5: Update index files

If new apps or significant structural changes occurred:
- Update `Apps/_Overview.md` — add/remove app links
- Update `Apps/_Source of Truth.md` — if paths or platform assignments changed
- Update `Apps/_Scratch & Exclusions.md` — if folders were added/removed from exclusion list

## Rules

- **Never invent content.** If a note can't be truthfully updated, say so. Don't fabricate file paths or architecture details.
- **Cite real files.** Every change entry must reference actual file paths from the git diff.
- **Use `[[wikilinks]]`** between related notes (per Tone Guide).
- **Respect the 8-note structure.** Don't create new note types unless the change truly warrants a category the Tone Guide doesn't cover — in that case, add a 9th note only for that app and note the deviation.
- **One Changes section per note per sync.** Don't scatter updates across multiple sections; consolidate at the bottom.
- **If the user only wants diff output** (not note updates), just show the git log and diff stat and stop. Don't write anything to the vault unless explicitly asked to map.

## Quick Commands Reference

```bash
# Single project — last 5 commits
cd "C:/Users/User/Desktop/Vishwet/Appristine projects/Android/RFID" && \
  git log --oneline -5 --no-merges && \
  git diff --stat HEAD~5 HEAD && \
  git diff --name-only HEAD~5 HEAD

# All projects — collect changed files across repos
find "C:/Users/User/Desktop/Vishwet/Appristine projects" -maxdepth 3 -name ".git" -type d | \
  while read g; do echo "=== $(dirname $g) ==="; \
    cd "$(dirname $g)" && git log --oneline -3 --no-merges; done
```
