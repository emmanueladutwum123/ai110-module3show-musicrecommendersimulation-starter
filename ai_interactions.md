# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

"Let's do the stretch features" — an open-ended instruction, not a step-by-step
spec. I let the agent (Claude, via Claude Code) propose what to build and then
carry out the full multi-step implementation on its own: design a Strategy
pattern for the scoring logic, wire it through both existing APIs without
breaking them, add a demo, extend the test suite, verify everything, and
document the process here.

**Prompts used:**

The only prompt for this stretch feature was: `let's do the stretch features`.
Everything else (the specific design, the three strategy implementations, the
test cases, this documentation) was the agent's own multi-step plan executed
without further step-by-step direction from me — that's what made it an
agentic workflow rather than a scripted one.

**What did the agent generate or change?**

- `src/recommender.py` — extracted the scoring logic (previously one hardcoded
  `_score_core` function) into a `ScoringStrategy` abstract base class with
  three implementations: `BalancedStrategy` (the original default recipe,
  now with configurable weights), `EnergyFocusedStrategy` (Phase 4's
  weight-shift experiment, made permanent and reusable instead of a
  throwaway runtime patch), and `GenreOnlyStrategy` (a new minimal baseline).
  Both `Recommender` and `recommend_songs`/`score_song` now accept an
  optional `strategy` argument, defaulting to the original balanced recipe.
- `src/main.py` — added `compare_strategies()`, which runs the same profile
  through all three strategies and prints each ranking side by side.
- `tests/test_recommender.py` — added 4 new tests, including two that
  specifically prove the pattern works (not just that it runs): a hand-built
  two-song case where `BalancedStrategy` and `EnergyFocusedStrategy`
  provably disagree on the winner, tested against both the OOP and the
  functional API.
- Ran `pytest` (6/6 passed, up from 2/2) and `python -m src.main` after the
  change to confirm nothing regressed.

**What did you verify or fix manually?**

Ran the actual test suite and CLI output myself rather than trusting the
agent's summary of what it built — the two flip-case tests
(`test_energy_focused_strategy_can_flip_the_ranking` and the functional-API
equivalent) were run and confirmed passing, not just written. I also checked
that the original two starter tests still passed unmodified, since the
refactor touched the exact code path they depend on (`Recommender.__init__`
gained a new parameter — needed to confirm the old no-strategy call signature
still worked). Also spot-checked that `EnergyFocusedStrategy`'s output
matched the exact numbers from Phase 4's manual weight-shift experiment
(Rooftop Lights 3.88, Gym Hero 3.61) — it did, which cross-validates that the
"stretch feature" refactor preserved the earlier finding instead of quietly
changing the math.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

**Strategy pattern** — `ScoringStrategy` is the abstract interface
(`score(user_prefs, song) -> (score, reasons)`), with `BalancedStrategy`,
`EnergyFocusedStrategy`, and `GenreOnlyStrategy` as interchangeable concrete
implementations.

**How did AI help you brainstorm or implement it?**

The choice wasn't arbitrary — it came directly out of Phase 4's weight-shift
experiment, where the weights were temporarily monkey-patched at the module
level (`recommender.GENRE_WEIGHT = 1.0`) to test sensitivity, then reverted.
That experiment was real but throwaway: there was no clean way to keep both
the original and the experimental scoring recipe available at the same time,
or to add a third variant, without duplicating the whole scoring function.
Strategy is the standard fix for "the same operation needs multiple
interchangeable algorithms decided at runtime" — so instead of a new
monkey-patch or a duplicated function, the scoring logic became a swappable
object.

**How does the pattern appear in your final code?**

`src/recommender.py`: the `ScoringStrategy` abstract base class, its three
concrete subclasses, and the `strategy` parameter on `Recommender.__init__`,
`recommend_songs()`, and `score_song()` (all defaulting to
`DEFAULT_STRATEGY = BalancedStrategy()` so existing calls are unaffected).
`src/main.py`: `compare_strategies()` demonstrates substitutability directly
— the exact same catalog and user profile produce three different top-3
lists purely by swapping which strategy object gets passed in, with zero
changes to the ranking or CLI code itself.
