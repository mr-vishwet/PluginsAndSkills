"""Direct Perplexity web-API OpenAI bridge for opencode.

Replaces the perplexity-webui-scraper (8000) + pplx-proxy (8001) stack with
a single stdlib server that POSTs opencode's chat history straight to
Perplexity's web SSE endpoint using the logged-in session cookie.

Env:
  PERPLEXITY_SESSION_TOKEN   __Secure-next-auth.session-token cookie
  PPLX_META                  JSON file (default ~/.config/opencode/pplx-meta.json)
                             with the remaining static cookies + account id.
Run:  python3 pplx-direct.py            (listens on 127.0.0.1:8001)
"""

import json
import os
import re
import sys
import time
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

API = "https://www.perplexity.ai/rest/sse/perplexity_ask"
META_PATH = os.environ.get("PPLX_META", os.path.expanduser("~/.config/opencode/pplx-meta.json"))
VERSION = "2.18"
CITE_RE = re.compile(r"\[\d+\]")

PRO_MODELS = {
    "perplexity/sonar-2": {"identifier": "experimental", "name": "Sonar 2"},
    "openai/gpt-5.4-thinking": {"identifier": "gpt54_thinking", "name": "GPT-5.4 thinking"},
    "anthropic/claude-sonnet-4.6-thinking": {"identifier": "claude46sonnetthinking", "name": "Claude Sonnet 4.6 thinking"},
    "google/gemini-3.1-pro-thinking-high": {"identifier": "gemini31pro_high", "name": "Gemini 3.1 Pro thinking"},
    "x-ai/grok-4.6-thinking": {"identifier": "grok46medium", "name": "Grok 4.6 thinking"},
    "moonshot/kimi-k2.6-thinking": {"identifier": "kimik26thinking", "name": "Kimi K2.6 thinking"},
    "nvidia/nemotron-3-super-thinking": {"identifier": "nv_nemotron_3_super", "name": "Nemotron 3 Super thinking"},
}


def cookie_header() -> str:
    token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "")
    meta = json.load(open(META_PATH)) if os.path.exists(META_PATH) else {}
    extra = meta.get("cookie", "")
    parts = [p for p in f"__Secure-next-auth.session-token={token}".split("; ") if not p.endswith("=")]
    parts += [p for p in extra.split("; ") if p]
    return "; ".join(parts)


def model_identifier(model: str) -> str:
    return PRO_MODELS.get(model, {}).get("identifier", "experimental")


def fold_messages(messages: list[dict]) -> str:
    """Flatten OpenAI chat history into a single prompt, mirroring the scraper."""
    parts: list[str] = []
    for m in messages:
        role = m.get("role")
        content = m.get("content")
        if isinstance(content, list):
            bits = []
            for p in content:
                if isinstance(p, dict):
                    if p.get("type") == "text":
                        bits.append(p.get("text", ""))
                    elif p.get("type") == "image_url":
                        bits.append("[image]")
            content = " ".join(bits)
        text = str(content or "")
        if role == "system" and text:
            parts.insert(0, f"[System]: {text}")
        elif role in ("user", "assistant") and text:
            parts.append(text)
        elif role == "tool" and text:
            parts.append(f"[tool result] {text}")
    return "\n\n".join(parts) if parts else ""


def build_payload(query: str, identifier: str) -> dict:
    frontend = str(uuid.uuid4())
    return {
        "params": {
            "attachments": [],
            "language": "en-US",
            "timezone": "Asia/Kolkata",
            "search_focus": "internet",
            "sources": ["web"],
            "frontend_uuid": frontend,
            "mode": "copilot",
            "model_preference": identifier,
            "is_related_query": False,
            "is_sponsored": False,
            "frontend_context_uuid": str(uuid.uuid4()),
            "prompt_source": "user",
            "query_source": "home",
            "is_incognito": False,
            "time_from_first_type": 1000,
            "local_search_enabled": False,
            "use_schematized_api": True,
            "send_back_text_in_streaming_api": False,
            "dsl_query": query,
            "skip_search_enabled": True,
            "source": "default",
            "always_search_override": False,
            "override_no_search": False,
            "extended_context": False,
            "version": VERSION,
        },
        "query_str": query,
    }


def stream_ask(payload: dict, cookies: str) -> bytes:
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:156.0) Gecko/20100101 Firefox/156.0",
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "Origin": "https://www.perplexity.ai",
            "Referer": "https://www.perplexity.ai/",
            "x-perplexity-request-endpoint": API,
            "x-perplexity-request-reason": "ask-query-state-provider",
            "x-perplexity-request-try-number": "1",
            "x-perplexity-request-id": str(uuid.uuid4()),
            "Cookie": cookies,
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


# ---------------- SSE parsing ----------------

def parse_sse(byte_chunks):
    """Yield parsed JSON data objects from an SSE byte stream."""
    buf = b""
    for chunk in byte_chunks:
        if not chunk:
            break
        buf += chunk
        while True:
            nl = buf.find(b"\n")
            if nl == -1:
                break
            line = buf[:nl].decode("utf-8", "replace").rstrip("\r")
            buf = buf[nl + 1:]
            if line.startswith("data: "):
                try:
                    yield json.loads(line[6:])
                except Exception:
                    pass
    # trailing data line without newline
    if buf:
        line = buf.decode("utf-8", "replace").rstrip("\r")
        if line.startswith("data: "):
            try:
                yield json.loads(line[6:])
            except Exception:
                pass


def extract_delta(obj: dict):
    """Return (is_final, text) for the newest answer text in this block.
    DONE carries the full cumulative 'answer'; IN_PROGRESS carries only deltas."""
    for blk in obj.get("blocks") or []:
        mb = blk.get("markdown_block")
        if not mb:
            continue
        if isinstance(mb.get("answer"), str) and mb.get("answer"):
            return True, CITE_RE.sub("", mb["answer"])
        chunks = mb.get("chunks") or []
        if chunks:
            return False, CITE_RE.sub("", "".join(chunks))
    return False, ""


def chat_complete(messages, model: str, stream: bool):
    query = fold_messages(messages)
    identifier = model_identifier(model)
    payload = build_payload(query, identifier)
    cookies = cookie_header()
    meta = json.load(open(META_PATH)) if os.path.exists(META_PATH) else {}
    account = meta.get("account", "")

    resp = stream_ask(payload, cookies)

    full = ""

    if stream:
        def gen():
            nonlocal full
            yield sse_open(model)
            for is_final, text in (extract_delta(o) for o in parse_sse((resp,))):
                if not text:
                    continue
                if is_final:
                    if text.startswith(full) and len(text) > len(full):
                        new = text[len(full):]
                        full += new
                        if new:
                            yield sse_chunk(model, new)
                else:
                    full += text
                    yield sse_chunk(model, text)
            yield sse_chunk(model, "", finish="stop")
            yield sse_done()
        return gen()
    else:
        for is_final, delta in (extract_delta(o) for o in parse_sse((resp,))):
            if not delta:
                continue
            if is_final:
                if len(delta) >= len(full):
                    full = delta
            elif full.endswith(delta):
                pass
            else:
                full += delta
        return non_stream_payload(model, full)


# ---------------- OpenAI-format helpers ----------------

def _chunk_payload(model: str, text: str, finish) -> dict:
    return {"id": "chatcmpl-" + uuid.uuid4().hex, "object": "chat.completion.chunk",
            "created": int(time.time()), "model": model,
            "choices": [{"index": 0, "delta": {"content": text} if text else {}, "finish_reason": finish}]}


def sse_open(model: str) -> bytes:
    p = _chunk_payload(model, "", None)
    p["choices"][0]["delta"] = {"role": "assistant"}
    return (b"data: " + json.dumps(p).encode() + b"\n\n")


def sse_chunk(model: str, text: str, finish=None) -> bytes:
    return b"data: " + json.dumps(_chunk_payload(model, text, finish)).encode() + b"\n\n"


def sse_done() -> bytes:
    return b"data: [DONE]\n\n"


def non_stream_payload(model: str, content: str) -> dict:
    return {
        "id": "chatcmpl-" + uuid.uuid4().hex,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                     "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


# ---------------- HTTP server ----------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write((fmt % args) + "\n")

    def _log_req(self):
        sys.stderr.write(f"{self.command} {self.path}\n")
        self.log_message("headers: %s", dict(self.headers))

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._log_req()
        if self.path.startswith("/v1/models"):
            models = [{"id": mid, "object": "model", "owned_by": "perplexity", "created": int(time.time())}
                      for mid in PRO_MODELS]
            self._send_json({"object": "list", "data": models})
        elif self.path == "/healthz":
            self._send_json({"ok": True})
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        self._log_req()
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            req = json.loads(body)
        except Exception:
            return self._send_json({"error": "invalid json"}, 400)

        messages = req.get("messages", [])
        model = req.get("model", "perplexity/sonar-2")
        stream = bool(req.get("stream", False))

        try:
            result = chat_complete(messages, model, stream)
        except Exception as exc:
            return self._send_json({"error": f"upstream error: {exc}"}, 502)

        if stream:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            try:
                for chunk in result:
                    try:
                        self.wfile.write(chunk)
                        self.wfile.flush()
                    except Exception:
                        break
                self.wfile.flush()
            except Exception:
                pass
        else:
            self._send_json(result)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"pplx-direct on 127.0.0.1:{port}")
    server.serve_forever()