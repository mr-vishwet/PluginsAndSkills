import { createServer, type IncomingMessage, type ServerResponse } from "node:http"
import { pathToFileURL } from "node:url"

const PAGE = "https://oxalpha.com/chat"
const CHAT = "https://oxalpha.com/api/chat"
const MODEL = "z-ai/glm-5.3-flash"
const PORT = Number(process.env.OXALPHA_BRIDGE_PORT || 3900)

let csrf = ""
let started = false

async function refreshCsrf(): Promise<void> {
  try {
    const res = await fetch(PAGE, { headers: { "User-Agent": "Mozilla/5.0" } })
    const html = await res.text()
    const m = html.match(/name="csrf-token" content="([^"]+)"/)
    if (m) csrf = m[1]
  } catch {}
}

function json(res: ServerResponse, code: number, body: unknown): void {
  res.writeHead(code, { "Content-Type": "application/json" })
  res.end(JSON.stringify(body))
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = ""
    req.on("data", (c: Buffer) => (data += c))
    req.on("end", () => resolve(data))
    req.on("error", reject)
  })
}

function normalizeMessages(value: unknown): { role: string; content: string }[] {
  if (!Array.isArray(value)) return []
  return value
    .map((message) => {
      if (!message || typeof message !== "object") return null
      const item = message as { role?: unknown; content?: unknown }
      const role = item.role === "developer" ? "system" : item.role === "tool" ? "user" : item.role
      if (typeof role !== "string") return null
      const content = Array.isArray(item.content)
        ? item.content.map((part) => {
            if (typeof part === "string") return part
            if (!part || typeof part !== "object") return ""
            const value = part as { text?: unknown; content?: unknown }
            return typeof value.text === "string" ? value.text : typeof value.content === "string" ? value.content : ""
          }).join("\n")
        : typeof item.content === "string"
          ? item.content
          : ""
      return { role, content }
    })
    .filter((message): message is { role: string; content: string } => message !== null && message.content.length > 0)
}

async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  try {
    const url = new URL(req.url ?? "/", "http://localhost")
    if (req.method === "GET" && (url.pathname === "/v1/models" || url.pathname === "/models")) {
      json(res, 200, { object: "list", data: [{ id: "ox-alpha", object: "model", owned_by: "ox-alpha" }] })
      return
    }
    if (req.method === "POST" && url.pathname.endsWith("/chat/completions")) {
      let body: { messages?: unknown } = {}
      try {
        body = JSON.parse(await readBody(req))
      } catch {}
      const messages = normalizeMessages(body.messages)
      if (!csrf) await refreshCsrf()
      const up = await fetch(CHAT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-TOKEN": csrf,
          "User-Agent": "Mozilla/5.0",
          Origin: "https://oxalpha.com",
          Referer: "https://oxalpha.com/chat",
        },
        body: JSON.stringify({ model: MODEL, messages }),
      })
      if (!up.ok || !up.body) {
        const text = await up.text().catch(() => "")
        json(res, up.status, { error: { message: text || "upstream error" } })
        return
      }
      res.writeHead(200, {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no",
      })
      const reader = up.body.getReader()
      const decoder = new TextDecoder()
      try {
        for (;;) {
          const { done, value } = await reader.read()
          if (done) break
          res.write(decoder.decode(value))
        }
      } finally {
        res.end()
      }
      return
    }
    json(res, 404, { error: { message: "not found" } })
  } catch (error) {
    if (!res.headersSent) json(res, 502, { error: { message: error instanceof Error ? error.message : "bridge error" } })
    else res.end()
  }
}

async function start(): Promise<void> {
  if (started) return
  started = true
  await refreshCsrf()
  setInterval(refreshCsrf, 5 * 60 * 1000)
  const server = createServer(handler)
  server.on("error", () => {})
  server.listen(PORT, "127.0.0.1")
}

const isMain = process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url
if (isMain) start()

export default async () => {
  await start()
  return {}
}
