# Exact revision of earlier flight histories

This is the owner’s isolated implementation investigation, begun 18 September
2026. It is not a second product implementation or a new MH370 posterior.
The frozen source/executables and independent data checks live here; uncertain
code is in `/tmp/mh370-cruise-ancestor-sampling` until assessed.

The model is unchanged. Its initial mode probabilities, Mach/altitude priors,
command processes, observation uncertainties, marginalized BFO bias and fuel
propagation are retained. The complete observation schedule sets the fuel
condition at 00:11; these short controls stop at 19:41 and do not score fuel
prematurely. No generating-truth files enter inference.

The new transition is conditional particle Gibbs with exact ancestor sampling
in simulator-innovation space. For each possible earlier history, all remaining
retained innovations are replayed and their full likelihood and prior/proposal
factors recomputed. Thus later data can revise an earlier physical history.
No truncated suffix, physical-state splicing or coordinate-only replay move is
used. The archived full-history and ordered forward/backward variants did not
implement this transition.

Independent exact-rational recreation: repository
`.sources/lindsten-2014-particle-gibbs-ancestor-sampling/README.md` (Lindsten,
Jordan & Schön 2014, Algorithm 2, eqs.3/22). The generic kernel’s independent
transition-row and worker-count checks pass. Flight path, correlated BFO
likelihood and complete-suffix checks are in `independent-verification.json`.

The 32-sweep pilots changed initial physical conditions 13/7 times; matched
ordinary particle Gibbs made no changes. Continuing each for 512 sweeps made
79/229 more initial changes, but last-half coordinate CDFs still differ by
58.37 percentage points. This establishes an ability to revise histories,
not satisfactory posterior exploration, recovery or convergence.

`mixing-diagnosis.json` identifies near-single-predecessor mass at the second
observation block. `exchange-design.json` defines the next correction: fixed
likelihood-only replica exchanges around the exact PGAS kernel. The beta=1
chain has the original target. Auxiliary chains use the same physical prior
and proposal correction, with likelihood powers 1/16, 1/8, 1/4 and 1/2.
Exact independent exchange invariance and default-target compatibility passed
before running the paired 128-sweep controls. Their results must be checked
using `verify_exchanges.py` before assessment or reporting.

Provenance and reproduction:

- `design.json`: baseline, first prototype and full-suffix-check source hashes.
- `exchange-design.json`: later source/executable hashes, fixed protocol and
  mathematical correction; the initial references and all input identities are
  included in each run summary.
- `execute.py`, `continue_chains.py`, `run_exchanges.py`: exact recorded queues.
  They refuse existing outputs. Do not relaunch them unchanged.
- `*-resources.json`: full command, wall/CPU time, peak resident memory.
- `verify.py`, `verify_exchanges.py`: saved-data independent calculations; these
  can be run without another aircraft ensemble.
- `progress.json`: actual last queue state, not a promise of unattended work.

The canonical report command is `mh370 report-impact-mixture`, using
`../terminal-refined-mixture/estimator-stability-inputs.json`. New cruise controls
are labelled synthetic diagnostics; existing MH370 impact/drift/search weights
remain unchanged. A dependent Markov-chain state is not a new independent
candidate trajectory, and these conditional chains do not estimate evidence.

The replica pair completed in 291.12 s combined wall time, with 61/32 changes to
initial conditions. All 6,450 contact and target-factor checks, 512 exchanges,
5,120 ancestor normalizations and 2,559 complete-suffix replay checks passed.
Last-half coordinate CDF gaps were 81.54 percentage points. This fixed exchange
configuration did not resolve exploration and is not integrated; its temporary
source extension was removed after archiving. Original full-suffix PGAS remains
under investigation. About 26 effective incoming filtering particles contract
to approximately one compatible predecessor under the retained full suffix,
which identifies the next diagnosis. See predecessor-concentration.json.
