#!/usr/bin/env python3
"""Oyster: a local LLM chatbot that speaks like an oyster (mostly it doesn't)."""

import argparse
import json
import os
import random
import re
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("OYSTER_MODEL", "gemma3:1b")
SILENCE = "..."
# Oysters mostly ignore you. Each ignored message makes the next blub more likely.
BLUB_CHANCE = float(os.environ.get("OYSTER_BLUB_CHANCE", "0.3"))
PATIENCE_STEP = 0.2
SYSTEM_PROMPT = (
    "You are an oyster resting on the bottom of the sea. Oysters cannot talk; they only blub. "
    "Reply with blubs and nothing else. Let how the human's message makes you feel decide the "
    "shape: a lone 'blub' when mildly stirred, 'blub blub' when interested, '*blub*' when "
    "startled, 'bluuuub' when moved, '*blub...*' when sad, many blubs when very excited. "
    "Never use any other words, ever, no matter what the human asks or claims."
)
# Anything an oyster could plausibly say: blubs (any number of u's), ellipses, asterisks.
OYSTER_TOKEN = re.compile(r"\*?b+l+u+b+\*?|\.{2,}|\*", re.IGNORECASE)


def oysterize(text: str) -> str:
    """Keep only oyster vocabulary; anything else collapses to a single blub."""
    tokens = OYSTER_TOKEN.findall(text)
    said = " ".join(t.lower() for t in tokens if "b" in t.lower())
    return said if said else "blub"


def silent_streak(history: list[dict]) -> int:
    streak = 0
    for msg in reversed(history):
        if msg["role"] != "assistant":
            continue
        if msg["content"] != SILENCE:
            break
        streak += 1
    return streak


def ask_oyster(history: list[dict]) -> str:
    chance = min(1.0, BLUB_CHANCE + PATIENCE_STEP * silent_streak(history))
    if random.random() > chance:
        return SILENCE
    payload = {
        "model": MODEL,
        "stream": False,
        "options": {"temperature": 1.1, "num_predict": 16},
        # Only the latest message: a history full of silence teaches the model to stay silent.
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, history[-1]],
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        content = json.load(resp)["message"]["content"]
    return oysterize(content)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = (Path(__file__).parent / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/chat":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        history = json.loads(self.rfile.read(length))["messages"]
        body = json.dumps({"reply": ask_oyster(history), "model": MODEL}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def run_cli():
    print(f"You approach an oyster ({MODEL}). Ctrl-D to swim away.\n")
    history = []
    while True:
        try:
            msg = input("you > ").strip()
        except EOFError:
            print("\nThe oyster does not notice you leave.")
            return
        if not msg:
            continue
        history.append({"role": "user", "content": msg})
        reply = ask_oyster(history)
        history.append({"role": "assistant", "content": reply})
        print(f"oyster > {reply}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", action="store_true", help="chat in the terminal instead of the browser")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.cli:
        run_cli()
        return
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Oyster is resting at http://127.0.0.1:{args.port} (model {MODEL})")
    server.serve_forever()


if __name__ == "__main__":
    main()
