const MAX_NAME = 120;
const MAX_EMAIL = 254;
const MAX_MESSAGE = 5000;
const HOUR_QUOTA = 10;

const bad = (msg) => Response.json({ error: msg }, { status: 400 });

function clean(value, limit) {
  if (typeof value !== "string") return "";
  return value.trim().slice(0, limit);
}

async function verifyTurnstile(token, secret, ip) {
  const body = new URLSearchParams({ secret, response: token });
  if (ip) body.set("remoteip", ip);
  const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body,
  });
  const data = await res.json().catch(() => null);
  return Boolean(data && data.success);
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);

    if (pathname === "/api/health") {
      return Response.json({ ok: true, service: "__NAME__", db: Boolean(env.DB) });
    }

    if (pathname !== "/api/contact") {
      return env.ASSETS.fetch(request);
    }

    if (request.method !== "POST") {
      return Response.json({ error: "method not allowed" }, { status: 405 });
    }

    const payload = await request.json().catch(() => null);
    if (!payload || typeof payload !== "object") return bad("expected a JSON body");

    const name = clean(payload.name, MAX_NAME);
    const email = clean(payload.email, MAX_EMAIL).toLowerCase();
    const message = clean(payload.message, MAX_MESSAGE);

    if (!name) return bad("name is required");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return bad("email looks invalid");
    if (message.length < 10) return bad("message is too short");

    // Cloudflare sets this on every request through its edge.
    const ip = request.headers.get("cf-connecting-ip") || "unknown";

    // Skip the check when the secret is unset, so the template runs before
    // Turnstile is configured. Set TURNSTILE_SECRET before going public.
    if (env.TURNSTILE_SECRET) {
      const token = clean(payload.turnstileToken, 2048);
      const passed = await verifyTurnstile(token, env.TURNSTILE_SECRET, ip);
      if (!passed) return Response.json({ error: "captcha failed" }, { status: 403 });
    }

    const usage = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM messages WHERE ip = ? AND created_at > datetime('now', '-1 hour')"
    )
      .bind(ip)
      .first();

    if (usage && usage.n >= HOUR_QUOTA) {
      return Response.json({ error: "too many messages, try again later" }, { status: 429 });
    }

    // Parameterised: never concatenate user input into the SQL string.
    await env.DB.prepare(
      "INSERT INTO messages (name, email, message, ip) VALUES (?1, ?2, ?3, ?4)"
    )
      .bind(name, email, message, ip)
      .run();

    return Response.json({ ok: true }, { status: 201 });
  },
};
