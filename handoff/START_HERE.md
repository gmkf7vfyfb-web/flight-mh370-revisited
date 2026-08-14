# Start here: receiving-harness handoff

This document is the entry point for a new AI harness or human collaborator.

## Required reading order

1. Root `AGENTS.md` — binding scientific and provenance rules.
2. `handoff/PROJECT_STATE.md` — completed work and headline results.
3. `handoff/ASSUMPTIONS.md` — explicit assumptions and exclusions.
4. `handoff/REPRODUCIBILITY_STATUS.md` — what can and cannot be rerun exactly.
5. `handoff/OPEN_QUESTIONS.md` — prioritized next work.
6. `handoff/DATA_AND_PROVENANCE.md` — source and publication controls.
7. `history/PROJECT_CONVERSATION_TIMELINE.md` — reconstructed development
   history; replace/supplement it with the exported verbatim transcript.

## Bootstrap instruction for the receiving model

> You are joining the research project *Flight MH370 Revisited: Integrated
> Bayesian Estimation without a Prespecified End-of-Flight Scenario*. Read
> `AGENTS.md` and every file in `handoff/` before proposing or executing new
> analysis. Treat the 00:11 airborne state, the 00:19 state, and the eventual
> impact point as distinct. Do not assume uncontrolled flight, continuous
> cruise, high altitude, fuel-exhaustion timing, or proximity to the seventh
> arc. Keep Pleiades results conditional. Distinguish exact reproduction,
> reconstruction, new analysis and diagnostic sensitivity. Inspect run
> manifests and the source register before relying on numerical outputs. State
> any missing data or model component rather than silently substituting it.

## First verification task

Before changing anything, the receiving model should answer:

1. What evidence is included through 00:11 and what is deliberately excluded?
2. Why may an impact be more than 100 NM from the seventh arc?
3. Why is the Pleiades posterior conditional rather than model-averaged with a
   specified scenario probability?
4. Which analyses are reconstructions or diagnostics rather than exact reruns?
5. Which missing upstream files prevent complete reproduction?

If those answers are wrong or incomplete, reread the handoff before continuing.

## Repository state at handoff

- Snapshot date: 2026-08-14 UTC.
- Original workspace: approximately 243 MB and 516 files before addition of
  migration documentation.
- Library cross-check: 148 canonical files (approximately 602 MiB) materialized
  under `library_full_audit/MH370/`; this layer intentionally overlaps working
  files and must remain immutable.
- No prior Git commit history was available in the workspace.
- Python runtime observed: 3.12.13.
- Node runtime observed: 24.14.0.
- Repository should remain private during collaborative development.
