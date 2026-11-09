export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);

    if (pathname === "/api/health") {
      return Response.json({
        ok: true,
        service: "__NAME__",
        served_by: "cloudflare-workers",
        at: new Date().toISOString(),
      });
    }

    return env.ASSETS.fetch(request);
  },
};
