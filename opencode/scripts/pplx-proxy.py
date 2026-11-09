import json

import http.client
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

UPSTREAM_HOST = "127.0.0.1"
UPSTREAM_PORT = 8000
app = FastAPI()


def rewrite(body: bytes) -> bytes | None:
    data = json.loads(body) if body else None
    if not data or not isinstance(data.get("messages"), list):
        return body if body else None
    if isinstance(data.get("tools"), list):
        data["tools"] = []  # scraper models have no tool-calling schema
    msgs = []
    for m in data["messages"]:
        if m.get("role") == "tool":
            content = m.get("content")
            if isinstance(content, list):
                text = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            else:
                text = str(content or "")
            msgs.append({"role": "user", "content": f"[tool result] {text}"})
            continue
        if m.get("role") == "system" and not m.get("content"):
            m = {**m, "content": ""}
        if m.get("role") == "assistant" and m.get("tool_calls"):
            m = {**m, "content": m.get("content") or "", "tool_calls": None}
        msgs.append(m)
    data["messages"] = msgs
    return json.dumps(data).encode()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(path: str, request: Request):
    body = await request.body()
    out = rewrite(body)

    conn = http.client.HTTPConnection(UPSTREAM_HOST, UPSTREAM_PORT)
    upstream_path = f"/{path}"
    if request.query_params:
        upstream_path += f"?{request.query_params}"
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")}
    if out is not None:
        headers["content-length"] = str(len(out))
    conn.request(request.method, upstream_path, body=out, headers=headers)
    resp = conn.getresponse()

    def gen():
        try:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                yield chunk
        finally:
            conn.close()

    return StreamingResponse(gen(), status_code=resp.status,
                             headers={k: v for k, v in resp.getheaders() if k.lower() != "content-length"})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)