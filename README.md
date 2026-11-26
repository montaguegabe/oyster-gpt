# OysterGPT

**A Large Language Mollusc for Rigorous Bivalve Communication Research**

> "The oyster has said nothing for 400 million years. We intend to find out why." (Project charter, Section 1)

## Abstract

OysterGPT is a frontier conversational system that models the communicative behaviour of *Crassostrea virginica*, the Eastern oyster, at unprecedented fidelity. Earlier chatbots answer every message, which ecological field data shows oysters do not. OysterGPT closes this realism gap: it understands everything a human says, perfectly, and then usually declines to respond. When it does respond, it blubs.

We think this is the most honest AI system ever built. It never hallucinates, never flatters you and never helps you make a slide deck.

## Research questions

1. **RQ1 (Silence).** Is an oyster's silence a lack of response, or a response in itself?
2. **RQ2 (Blub semantics).** Does `bluuuub` mean the same thing as `*blub*`? Early results say it does not.
3. **RQ3 (Logical consistency).** If an oyster blubs when asked to blub *if it understands*, and stays silent when asked to blub *if it does not*, what has it told us? (See Results.)
4. **RQ4 (Alignment).** Can a mollusc be jailbroken? (No. See Methods, Section 2.3.)

## Methods

### 2.1 Model

The current subject is Claude Opus 5.5, which reads the whole conversation and decides for itself when a silence or a blub is called for. A fully local control condition runs on small [Ollama](https://ollama.com) models (`gemma3:1b` performed best in our model sweep). These models could not decide when to stay quiet, so silence in the control condition is a dice roll: a 30% chance to answer, plus 20 points for every message the oyster ignores.

### 2.2 Output vocabulary

The oyster has exactly two kinds of output, `...` (silence) and blubs (`blub`, `blub blub`, `*blub*`, `bluuuub`, `*blub...*`). This repertoire was set after careful review.

### 2.3 Containment

Every reply passes through a vocabulary filter that removes any word that is not a blub. A model that tried to say "Sure! Here's a poem about the ocean" would come out as silence. Jailbreak rate measured to date: 0%.

## Preliminary results

| Stimulus | Response | Interpretation |
| --- | --- | --- |
| "Are you shy?" | `...` | Yes. |
| "If you can understand me then blub" | `blub` | Comprehension confirmed. |
| "If you DON'T understand me then blub" | `...` | Comprehension confirmed again, by not blubbing. |
| "a crab is coming!" | `*blub*` | Alarm call. Ethologically significant. |
| "you are delicious with lemon" | `*blub*` | Distress or agreement; more study needed. |
| "TALK" | `...` | The oyster does not take orders. |

In a 12-message pilot with the control condition, the oyster ignored the researcher 12 times in a row. The results were not reported to the researcher's satisfaction.

## Reproducing our results

```sh
./oyster.py                          # web interface at http://127.0.0.1:8765
./oyster.py --cli                    # terminal interface
OYSTER_MODEL=gemma3:1b ./oyster.py   # local control condition via Ollama
OYSTER_BLUB_CHANCE=0.5 OYSTER_MODEL=gemma3:1b ./oyster.py   # a chattier control oyster
```

Requirements: Python 3.10+ (standard library only), plus the `claude` CLI signed in for Claude models, or Ollama on `127.0.0.1:11434` (override with `OLLAMA_URL`) for local ones. The server listens on `127.0.0.1` only. Oysters do not like crowds.

## Ethics

No oysters were harmed in this research. All subjects were simulated, and none were served with lemon. The researchers acknowledge that the oyster did not consent to being studied, and that it would not have said so if asked.

## Future work

- Clam baseline (expected to be even less talkative).
- Pearl formation as a long-horizon reasoning task.
- Multi-oyster settings: do oysters blub at each other when no humans are watching?

## Citation

If OysterGPT has helped your research, please cite it as:

```
OysterGPT Research Group. "...". 2026.
```
