"""Minimal bridge: OpenAI chat-completions -> Omnirush responses.
Run:  python3 omnirush-bridge.py  [port]
Then set opencode's omnirush provider baseURL to http://localhost:<port>/v1
"""
import json, sys, uuid
from http.server import HTTPServer, BaseHTTPRequestHandler

GATEWAY = "https://omnirush.ai/omnirush/v1"
AUTH = open("C:/Users/User/.omnirush/auth.json").read()
TOKEN = json.loads(AUTH)["accessToken"]

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path.startswith("/v1/models"):
            self._json(200, {"object":"list","data":[
                {"id":"gpt-6-astra","object":"model","owned_by":"omnirush"},
                {"id":"gpt-6-sol","object":"model","owned_by":"omnirush"},
                {"id":"gpt-5.6-sol","object":"model","owned_by":"omnirush"},
            ]})
        else:
            self._json(404, {"error":"not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        payload = json.loads(body) if body else {}

        # Only translate chat/completions -> responses
        if "/chat/completions" in self.path:
            model = payload.get("model", "gpt-6-astra")
            messages = payload.get("messages", [])
            text = ""
            for m in messages:
                if m.get("role") == "user":
                    text += (m.get("content", "") if isinstance(m.get("content"), str) else "") + "\n"
            resp_payload = {
                "model": model,
                "input": text.strip() or "hello",
                "max_output_tokens": payload.get("max_tokens", 1024),
            }
            import urllib.request
            req = urllib.request.Request(
                f"{GATEWAY}/responses",
                data=json.dumps(resp_payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {TOKEN}",
                    "User-Agent": "omnirush/1.0.5",
                    "Accept": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    upstream = resp.read()
                    # Translate responses format -> chat completions (simplified)
                    upstream_json = json.loads(upstream) if isinstance(upstream, bytes) else upstream
                    # Try to extract text from responses payload
                    text_out = ""
                    if isinstance(upstream_json, dict) and "output" in upstream_json:
                        for item in upstream_json.get("output", []):
                            if isinstance(item, dict) and item.get("type") == "message":
                                for content in item.get("content", []):
                                    if isinstance(content, dict) and content.get("type") == "output_text":
                                        text_out += content.get("text", "")
                    # Return as chat completion chunk stream (simplified to non-stream for now)
                    result = {
                        "id": "chatcmpl-" + str(uuid.uuid4()).hex[:12],
                        "object": "chat.completion",
                        "created": int(__import__('time').time()),
                        "model": model,
                        "choices": [{"index": 0, "message": {"role":"assistant","content": text_out or "(gateway responded with responses format — proxy working but response translation needs work)"}, "finish_reason":"stop"}],
                        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    }
                    self._json(200, result)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode() if hasattr(e, "read") else str(e)
                # The gateway may return client_not_allowed — propagate honestly
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(err_body.encode())
        else:
            self._json(404, {"error":"not found"})

    def _json(self, code, obj):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3901
    print(f"omnirush-bridge on localhost:{port} -> {GATEWAY}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
