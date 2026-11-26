# Contributing to Glyphwerk

Thank you for helping improve Glyphwerk! It's a toolkit for translating and porting GBA Gen-3 ROM projects safely. Every contribution helps other translation projects, from a single test to a new gate.

New here? Look for issues labeled [`good first issue`](https://github.com/pokemon-unbound-de/glyphwerk/labels/good%20first%20issue). Each one says which file to touch and how to know you're done. Comment on the issue before you start so two people don't work on the same thing.

## Core Rules
1. **Zero Copyrighted Game Data:** Never commit GBA ROMs (`.gba`), saves (`.sav`), savestates (`.ss0`), patch files (`.bps`/`.ips`/`.ups`), or extracted commercial game scripts/text dumps. This includes screenshots of game text, font sheets ripped from a ROM, and real ROM offsets copied together with the bytes found there.
2. **Synthetic Tests Only:** Every bug fix or new quality gate must include a deterministic unit test under `tests/` running against small generated binary fixtures (see `glyphwerk/demo_data.py` and `tests/conftest.py`).
3. **Profile-Driven Design:** Never hardcode game-specific ROM offsets in `glyphwerk/`. Put structural offsets into a JSON profile under `profiles/` matching `docs/GAME_PROFILE_SCHEMA.md`.
4. **License Compatibility:** Contributions must be compatible with the MIT License. Keep GPL/AGPL binaries (such as `flips`) external via CLI wrappers.

## Using AI tools

AI assistants (chat models, coding agents, autocomplete) are welcome here. We build Glyphwerk with them ourselves. The rules are the same for everyone:

1. **Say so in the PR.** Tick the AI box in the pull request template and name the tool, for example "Claude Code wrote the first draft of the tests". You don't need to share prompts.
2. **Tests stay green.** `ruff`, `pytest`, the demo and `glyphwerk secret-scan .` must pass locally and in CI. A PR that only passes because a test was weakened or skipped will be closed.
3. **A human stands behind it.** You have read every changed line, you can explain it in review, and you answer follow-up questions yourself. PRs opened by bots without a responsible person will be closed.
4. **No game data, not even via AI.** Don't paste ROM bytes, save files or game text into an AI tool to generate fixtures, and don't commit what it produces from them. Fixtures are built synthetically in the test.
5. **Keep it small.** One topic per PR. Large AI-generated refactors are hard to review. Open an issue first and agree on the plan.

Reviewers treat AI-assisted and hand-written PRs the same: the code has to be correct, tested and understandable.

## Local Workflow
```bash
pip install -e ".[dev]"
ruff check glyphwerk tests examples
pytest -v
python examples/minimal_synthetic_demo/run_demo.py
glyphwerk secret-scan .
```

## Pull Requests
- Branch from `main`, one topic per PR, and fill in the template.
- Link the issue (`Fixes #12`).
- New behavior comes with a test. A bug fix comes with a test that fails without the fix.
- Commit messages in English, short and in the imperative ("Add LZ77 round-trip tests").
- `main` is protected: merges happen after review and green CI.

## Labels
| Label | Meaning |
|---|---|
| `good first issue` | Small, clearly scoped, no ROM knowledge needed |
| `help wanted` | Bigger, but we'd love outside help |
| `bug` | Something behaves wrong |
| `enhancement` | New feature or improvement |
| `tests` | Missing or better tests |
| `documentation` | Docs, examples, translations of docs |
| `ai-assisted` | PR was written with AI help (set by the template checkbox or a maintainer) |
| `glyphwerk-kandidat` | Proposed by the Pokémon Unbound DE pipeline for upstreaming into Glyphwerk |
| `needs-triage` | New, not yet looked at |

## Questions
Open an [issue](https://github.com/pokemon-unbound-de/glyphwerk/issues), or ask in English or German on our [Discord](https://discord.gg/fSkhHppgcv).
