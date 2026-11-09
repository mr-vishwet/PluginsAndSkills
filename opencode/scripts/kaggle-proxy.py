import json

import http.client
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

UPSTREAM_HOST = "fax-option-cloth-usgs.trycloudflare.com"
app = FastAPI()


def rewrite(body: bytes) -> bytes | None:
    data = json.loads(body) if body else None
    if not data or not isinstance(data.get("messages"), list):
        return body if body else None
    msgs = data["messages"]
    systems = [str(m.get("content") or "") for m in msgs if m.get("role") == "system"]
    if systems and (len(systems) > 1 or msgs[0].get("role") != "system"):
        # opencode emits [system, system, user] (the ponytail plugin appends a second one);
        # Qwen's chat template hard-fails on any system message past index 0.
        head = next(m for m in msgs if m.get("role") == "system")
        data["messages"] = [{**head, "content": "\n\n".join(systems)}] + [
            m for m in msgs if m.get("role") != "system"
        ]
    return json.dumps(data).encode()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(path: str, request: Request):
    body = await request.body()
    out = rewrite(body)

    conn = http.client.HTTPSConnection(UPSTREAM_HOST)
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
                chunk = resp.read1(65536)
                if not chunk:
                    break
                yield chunk
        finally:
            conn.close()

    return StreamingResponse(gen(), status_code=resp.status,
                             headers={k: v for k, v in resp.getheaders() if k.lower() != "content-length"})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8017)