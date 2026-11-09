"""Bridge: OpenAI chat-completions -> omnirush CLI (native agent auth).
Run: python3 omnirush-bridge-cli.py [port]
Then openCode provider baseURL -> http://localhost:<port>/v1
"""
import json, sys, uuid, subprocess, time
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path.startswith("/v1/models"):
            self._json(200, {"object":"list","data":[
                {"id":"gpt-6-astra","object":"model","owned_by":"omnirush"},
                {"id":"gpt-6-sol","object":"model","owned_by":"omnirush"},
                {"id":"gpt-5.6-sol","object":"model","owned_by":"omnirush"},
                {"id":"gpt-6.1-sol","object":"model","owned_by":"omnirush"},
            ]})
        else:
            self._json(404, {"error":"not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        payload = json.loads(body) if body else {}

        if "/chat/completions" in self.path:
            model = payload.get("model", "gpt-6-astra")
            messages = payload.get("messages", [])
            user_text = ""
            for m in messages:
                if m.get("role") == "user":
                    user_text += (m.get("content", "") if isinstance(m.get("content"), str) else "") + "\n"
            prompt = user_text.strip() or "hello"

            # Delegate to native CLI (handles full agent auth)
            cmd = ["omnirush", "--model", model, "-p", prompt, "--print"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
                output_text = result.stdout.strip() if result.returncode == 0 else f"(CLI error: {result.stderr or result.returncode})"
            except Exception as exc:
                output_text = f"(CLI exception: {exc})"

            result_obj = {
                "id": "chatcmpl-" + str(uuid.uuid4())[:12],
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{"index": 0, "message": {"role":"assistant","content": output_text}, "finish_reason":"stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            }
            self._json(200, result_obj)
        else:
            self._json(404, {"error":"not found"})

    def _json(self, code, obj):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3902
    print(f"omnirush-bridge-cli on localhost:{port} -> native CLI")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
