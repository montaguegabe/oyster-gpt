# Oyster

A local LLM chatbot that speaks like an oyster. Mostly it doesn't respond. Occasionally it blubs.

It runs on [Ollama](https://ollama.com) (default model `gemma3:1b`). A system prompt tells the model it is an oyster, and a filter removes every word that isn't a blub, so even a jailbroken oyster can only say `...` or `blub`.

## Run

```sh
./oyster.py            # web chat at http://127.0.0.1:8765
./oyster.py --cli      # chat in the terminal
OYSTER_MODEL=llama3.2:3b ./oyster.py   # use another Ollama model
```

It needs Python 3.10+ (standard library only) and Ollama running on `127.0.0.1:11434` (override with `OLLAMA_URL`).
