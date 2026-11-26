# OysterGPT

OysterGPT: an LLM chatbot that speaks like an oyster. Mostly it doesn't respond. Occasionally it blubs.

It uses Claude Opus 5.5 by default, through the local `claude` CLI on your Claude subscription (no API key). Opus sees the whole conversation and decides for itself when to stay silent and when a blub is called for. Set `OYSTER_MODEL` to an [Ollama](https://ollama.com) model (such as `gemma3:1b`) to run fully offline; small models can't judge when to stay quiet, so there the silence is a dice roll (30% chance to answer, `OYSTER_BLUB_CHANCE`, plus 20 points for every ignored message). Either way, a filter removes every word that isn't a blub.

## Run

```sh
./oyster.py            # web chat at http://127.0.0.1:8765
./oyster.py --cli      # chat in the terminal
OYSTER_MODEL=gemma3:1b ./oyster.py     # fully local via Ollama
```

It needs Python 3.10+ (standard library only), plus the `claude` CLI signed in for Claude models or Ollama on `127.0.0.1:11434` (override with `OLLAMA_URL`) for local ones.
