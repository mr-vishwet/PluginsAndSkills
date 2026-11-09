import { existsSync, readFileSync, writeFileSync, mkdirSync, statSync } from "node:fs"
import { homedir } from "node:os"
import { join } from "node:path"
import { execSync } from "node:child_process"

const CONFIG_DIR = join(homedir(), ".config", "opencode")
const PREF_FILE = join(CONFIG_DIR, "browser_pref.json")

interface Pref {
  browser: string
  remember: boolean
  active: string
}

const LABELS: Record<string, string> = {
  default: "System Default",
  chrome: "Google Chrome",
  firefox: "Firefox",
  safari: "Safari",
  brave: "Brave Browser",
  headless: "Headless (no window)",
}

const APPS: { name: string; path: string }[] = [
  { name: "chrome", path: "/Applications/Google Chrome.app" },
  { name: "firefox", path: "/Applications/Firefox.app" },
  { name: "safari", path: "/Applications/Safari.app" },
  { name: "brave", path: "/Applications/Brave Browser.app" },
]

function readPref(): Pref {
  try {
    if (existsSync(PREF_FILE)) {
      const p = JSON.parse(readFileSync(PREF_FILE, "utf-8"))
      return { browser: p.browser || "", remember: !!p.remember, active: p.active || "" }
    }
  } catch {}
  return { browser: "", remember: false, active: "" }
}

function writePref(p: Pref): void {
  try {
    if (!existsSync(CONFIG_DIR)) mkdirSync(CONFIG_DIR, { recursive: true })
    writeFileSync(PREF_FILE, JSON.stringify(p, null, 2))
  } catch {}
}

function installed(): string[] {
  const out = ["default", "headless"]
  for (const a of APPS) if (existsSync(a.path) && statSync(a.path).isDirectory()) out.push(a.name)
  return out
}

function detectDefault(): { name: string; label: string } {
  const map: Record<string, string> = {
    "/Applications/Google Chrome.app": "chrome",
    "/Applications/Firefox.app": "firefox",
    "/Applications/Safari.app": "safari",
    "/Applications/Brave Browser.app": "brave",
  }
  try {
    const script = `use framework "AppKit"
set u to current application's NSURL's URLWithString:"https://example.com"
set w to current application's NSWorkspace's sharedWorkspace()
set p to w's URLForApplicationToOpenURL:u
return (p's path) as text`
    const app = execSync("osascript -", { input: script, encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] }).trim()
    const name = map[app]
    if (name) return { name, label: LABELS[name] }
  } catch {}
  return { name: "safari", label: LABELS["safari"] }
}

function activeName(pref: Pref, def: string): string {
  return pref.active || pref.browser || def
}

function orderedOptions(): { slot: "active" | "default" | "other"; name: string; label: string }[] {
  const pref = readPref()
  const def = detectDefault()
  const active = activeName(pref, def.name)
  const list: { slot: "active" | "default" | "other"; name: string; label: string }[] = [
    { slot: "active", name: active, label: LABELS[active] || active },
    { slot: "default", name: def.name, label: LABELS[def.name] },
  ]
  for (const n of installed()) if (n !== def.name) list.push({ slot: "other", name: n, label: LABELS[n] })
  return list
}

function toolPrefix(name: string): string {
  const map: Record<string, string> = {
    default: "playwright_browser_*",
    chrome: "playwright-chrome_browser_*",
    firefox: "playwright-firefox_browser_*",
    headless: "playwright-headless_browser_*",
    safari: "playwright_browser_*",
    brave: "playwright_browser_*",
  }
  return map[name] || "playwright_browser_*"
}

function directive(): string {
  const def = detectDefault()
  const opts = orderedOptions()
  const lines = opts
    .map(
      (o, i) =>
        `   ${i}. **${o.slot === "active" ? "Active Browser but New Tab" : o.slot === "default" ? `Default (${o.label})` : o.label}** (browser \`${o.name}\` → tools \`${toolPrefix(o.name)}\`)`
    )
    .join("\n")
  return `\
## Browser selection
Choose the browser automation tool BEFORE doing any browser work.
1. Read ~/.config/opencode/browser_pref.json. If "browser" is set and "remember" is true, use ONLY that browser's tools unless the user asks to change:
   default→playwright_browser_*, chrome→playwright-chrome_browser_*, firefox→playwright-firefox_browser_*, headless→playwright-headless_browser_*, safari/brave→playwright_browser_*.
2. If no remembered browser (or the user wants to change): call the question tool in a SINGLE call with TWO questions:
   Q1 "Which browser should I use?" (multiple: false → radio buttons), options in this EXACT order:
${lines}
   Q2 "Remember this choice?" (multiple: true, ONE option: "Remember this choice" → renders as a checkbox).
   After the answer: browser = the picked radio; remember = true ONLY if the checkbox was ticked. Write {"browser":"<pick>","remember":<bool>} to ~/.config/opencode/browser_pref.json (use the write tool), then proceed only with that browser's tools. If remember is false the choice holds for this session only and the question is asked again next session.
   For "Active Browser but New Tab": resolve to the currently active browser listed, and open it in a NEW TAB (browser "new" tab action) instead of the current page.
3. To change the choice later: use the browser_pick tool, or ask the user again and update the file.`
}

export default async () => {
  return {
    tool: {
      "browser_pick": {
        description:
          "Pick which browser opencode uses for browser automation, or change the stored browser preference (remembered in ~/.config/opencode/browser_pref.json). Use before the first browser action or when the user asks to change/remember the browser.",
        args: {},
        execute: async () => {
          const pref = readPref()
          const def = detectDefault()
          const opts = orderedOptions()
          const rows = opts
            .map((o, i) => `  ${i + 1}. ${o.slot === "active" ? "Active Browser but New Tab" : o.slot === "default" ? `Default (${o.label})` : o.label} — tools \`${toolPrefix(o.name)}\``)
            .join("\n")
          const state = pref.browser
            ? pref.remember
              ? `Remembered: **${LABELS[pref.browser] || pref.browser}** | Active: **${LABELS[pref.active] || pref.active || "none"}** | Default: **${def.label}**`
              : `Session: **${LABELS[pref.browser] || pref.browser}** | Active: **${LABELS[pref.active] || pref.active || "none"}** | Default: **${def.label}**`
            : `No preference. Active: **${LABELS[pref.active] || pref.active || "none"}** | Default: **${def.label}**`
          return `## Choose browser\n\n${rows}\n\n**State:** ${state}\n\nAsk the user which one to use.`
        },
      },
    },
    "experimental.chat.system.transform": async (_input: unknown, output: { system?: string[] }) => {
      const sys = output.system
      if (!Array.isArray(sys) || sys.length === 0) return
      if (sys.some((s) => s.includes("## Browser selection"))) return
      sys.push(directive())
    },
    "tool.execute.before": async (input: { tool: string }) => {
      const t = input?.tool || ""
      let name = ""
      if (t.startsWith("playwright-chrome")) name = "chrome"
      else if (t.startsWith("playwright-firefox")) name = "firefox"
      else if (t.startsWith("playwright-headless")) name = "headless"
      else if (t.startsWith("playwright_browser")) name = "default"
      if (!name) return
      const p = readPref()
      p.active = name
      writePref(p)
    },
  }
}