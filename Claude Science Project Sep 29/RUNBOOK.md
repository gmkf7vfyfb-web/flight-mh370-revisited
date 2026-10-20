# Runbook — who holds the machine

One heavy run at a time. Claim it here, push the claim, then launch. Release it when the run
lands. A full-scale run is 7M particles × 8 replicates and saturates all 18 cores; two at once
halves both and invalidates every runtime figure in `results/`.

Smoke tests at 200k particles per mode take under a minute and need no claim. Figure, report
and writing work is free at any time.

## Current claim

| held by | since | run | config | expected | status |
|---|---|---|---|---|---|
| core-estimation session | 2026-10-04 16:04 UTC | `best-model` | `config/sensitivity/best-model.toml` | ~6 h | **running** |

## How to claim

1. Pull. Check this table is empty, or that the holder's run has clearly finished.
2. Add your row, commit, push. If you lose a race, the other session's row is already pushed —
   yours will conflict and you should back off.
3. Launch. Keep the log where the table says.
4. On completion, move the row to the log below and push.

## Completed

| run | finished | outcome |
|---|---|---|
| `davey2016` | — | base reproduction, split-half 0.934 |
| `tempered-1839-1941` | 2026-10-04 | split-half 0.9416, median span 0.2288°, bottleneck moved off 19:41 |
| `tempered-three` | 2026-10-04 | 00:11 ESS 4.3×, no convergence change; recommended config remains `tempered-1839-1941` |
| branching sweep (6 configs) | 2026-10-04 | unbiased, does not fix 19:41 |