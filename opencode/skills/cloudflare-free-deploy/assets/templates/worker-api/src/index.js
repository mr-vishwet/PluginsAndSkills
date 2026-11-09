// ALLOWED_ORIGIN is a comma-separated list, or "*" for a public demo endpoint.
function cors(request, env) {
  const list = (env.ALLOWED_ORIGIN || "*").split(",").map((s) => s.trim()).filter(Boolean);
  const origin = request.headers.get("origin") || "";
  const allow = list.includes("*") ? "*" : list.includes(origin) ? origin : list[0];
  return {
    "access-control-allow-origin": allow,
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "600",
    "vary": "Origin",
  };
}

function json(data, status, headers) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...headers },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const h = cors(request, env);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: h });

    if (url.pathname === "/api/health") {
      return json({ ok: true, service: "__NAME__", at: new Date().toISOString() }, 200, h);
    }

    if (url.pathname === "/api/time") {
      return json({ epoch: Date.now(), utc: new Date().toUTCString() }, 200, h);
    }

    if (url.pathname === "/api/echo" && request.method === "POST") {
      const body = await request.json().catch(() => null);
      if (body === null) return json({ error: "expected a JSON body" }, 400, h);
      return json({ received: body }, 200, h);
    }

    // Demonstrates a KV binding; comment out until CACHE exists in wrangler.jsonc.
    if (url.pathname === "/api/hits" && env.CACHE) {
      const key = "hits";
      const next = Number((await env.CACHE.get(key)) || 0) + 1;
      await env.CACHE.put(key, String(next));
      return json({ hits: next }, 200, h);
    }

    return json({ error: "not found", path: url.pathname }, 404, h);
  },
};
