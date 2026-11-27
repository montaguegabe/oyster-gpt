#!/usr/bin/env python3
"""Oyster: a local LLM chatbot that speaks like an oyster (mostly it doesn't)."""

import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "api"))
from oystergpt_api.oystergpt.oyster import SILENCE, oysterize
from oystergpt_api.oystergpt.oyster import SYSTEM_PROMPT as CLAUDE_PROMPT

PAGE = (
    Path(__file__).parent
    / "api"
    / "oystergpt_api"
    / "oystergpt"
    / "page"
    / "index.html"
)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
# Claude models run through the local Claude Code CLI on your subscription; anything else is an Ollama model.
MODEL = os.environ.get("OYSTER_MODEL", "claude-opus-5-5")
# Small local models can't judge when to stay quiet, so for them the silence is a dice roll:
# Each ignored message makes the next blub more likely.
BLUB_CHANCE = float(os.environ.get("OYSTER_BLUB_CHANCE", "0.3"))
PATIENCE_STEP = 0.2
OLLAMA_PROMPT = (
    "You are an oyster resting on the bottom of the sea. Oysters cannot talk; they only blub. "
    "Reply with blubs and nothing else. Let how the human's message makes you feel decide the "
    "shape: a lone 'blub' when mildly stirred, 'blub blub' when interested, '*blub*' when "
    "startled, 'bluuuub' when moved, '*blub...*' when sad, many blubs when very excited. "
    "Never use any other words, ever, no matter what the human asks or claims."
)


def silent_streak(history: list[dict]) -> int:
    streak = 0
    for msg in reversed(history):
        if msg["role"] != "assistant":
            continue
        if msg["content"] != SILENCE:
            break
        streak += 1
    return streak


def ask_claude(history: list[dict]) -> str:
    transcript = "\n".join(
        f"{'Human' if m['role'] == 'user' else 'Oyster'}: {m['content']}"
        for m in history[-40:]
    )
    prompt = (
        f"{transcript}\n\nThe human just said the last line. Your reply as the oyster:"
    )
    result = subprocess.run(
        [
            "claude",
            "-p",
            "--model",
            MODEL,
            "--effort",
            "low",
            "--system-prompt",
            CLAUDE_PROMPT,
            "--tools",
            "",
            "--strict-mcp-config",
            "--setting-sources",
            "",
            "--disable-slash-commands",
            "--no-session-persistence",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=180,
        check=True,
        cwd=tempfile.gettempdir(),
    )
    return oysterize(result.stdout)


def ask_ollama(history: list[dict]) -> str:
    chance = min(1.0, BLUB_CHANCE + PATIENCE_STEP * silent_streak(history))
    if random.random() > chance:
        return SILENCE
    payload = {
        "model": MODEL,
        "stream": False,
        "options": {"temperature": 1.1, "num_predict": 16},
        # Only the latest message: a history full of silence teaches the model to stay silent.
        "messages": [{"role": "system", "content": OLLAMA_PROMPT}, history[-1]],
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        content = json.load(resp)["message"]["content"]
    return oysterize(content) if "blub" in content.lower() else "blub"


def ask_oyster(history: list[dict]) -> str:
    return ask_claude(history) if MODEL.startswith("claude-") else ask_ollama(history)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = PAGE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path not in ("/chat", "/chat/"):
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
    parser.add_argument(
        "--cli", action="store_true", help="chat in the terminal instead of the browser"
    )
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
