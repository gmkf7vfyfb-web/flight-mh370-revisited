
# Work orders, 15 October 2026 — items 6, 7, 8, 9

Written by the coordinating session. Each order is self-contained: a new thread on the named
profile needs nothing from any earlier thread. Pete's paste prompt for each is in section 5.

**Standing facts true for all three orders.** Core run I is NOT CONVERGED (all-partition
split-half: waypoints 0.916, free flight 0.830, against the 8-replicate floor 0.924). Run-i-dive
supersedes run I and the two are different priors over the end-of-flight trajectory, not
sampling variants — do not pool them. The end-of-flight uncontrolled arm is NOT CALIBRATED: the
Boeing leave-one-out gate failed in all three rounds (out-of-sample −1,282, −904, −714 nat;
13, 18, 25 of 62 targets inside tolerance; no case passed). While that gate is open, no impact
energy, attitude, flight-path angle or energy-transfer duration may be quoted as a physical
prediction. Canonical split-half is the mean over all balanced partitions, never the single
value stored in summary.json. Impact energy and duration live in the per-seed sidecar
`tau90_v1.npz`, joined by row order — the six energy columns in the impact table are non-finite.
Check the sha256 of any binary in /tmp before use and rebuild if it is missing.

---

## 1. END_OF_FLIGHT_MODULE — items 7 and 8

One order, because both tasks touch the same configuration.

### Task A (item 7) — make the dive probability match the ruling, and report acoustics as a function of it

**The defect.** The run note records a U[0,1] hyper-prior on the dive probability with marginal
0.5. The configuration holds a fixed `pushover_to_surface_probability = 0.5` and the realised
draws behave as an independent coin per descent. Measured across 6,232 parents with 20.4
push-over draws each: observed across-parent standard deviation of the dive share 0.1140,
predicted 0.1108 for a fixed p = 0.5, predicted 0.3025 for a per-parent p ~ U[0,1]. The
implementation is the fixed coin, so the uncertainty on this parameter is understated by a
factor of about 2.7.

**Why it matters.** The share of impacts in the 10–45 degree flight-path-angle band — the
acoustically decisive band — runs from 0.037 at p = 0 to 0.291 at p = 1, nearly eightfold.
Every detectability and non-detection statement depends on it.

**What to do.** (i) Decide and state whether the intended model is a per-parent hyper-prior or a
fixed coin, and make code, config and note agree; this is a prior change, so flag it for Pete
rather than choosing silently. (ii) Whichever is chosen, deliver the sweep over p by
reweighting `latent:pushover_to_surface` — 2p if the push-over continued to the surface,
2(1−p) if it did not, 1 if no push-over was drawn — which needs no new simulation. (iii) Report
the 10–45 degree band share, the loud-decile share and the impact-energy quantiles at
p = 0, 0.25, 0.5, 0.75, 1, with the effective sample at each.

**Acceptance.** A table of those quantities against p; the prior-recovery check (test 6) still
passing; a statement of which of the two models is now implemented and what changed.

### Task B (item 8) — adopt the round-3 laws as a labelled sensitivity

**What this is not.** It is not a calibration and the gate stays failed. Round 3 is the best of
the three out of sample (−713.6 nat, 25 of 62 targets inside tolerance) and it reproduced the
glide phugoid in cases 1, 7 and 8 — period and damping inside tolerance — which rounds 1 and 2
could not reach. Its laws are lagged lift, a turn rule towards the dead engine, and a
dive trigger on equivalent airspeed at the loss of control.

**The identification problem, which must travel with every number.** Leave-one-out parameters
spread widely: lift gain 0.38–0.98, spiral doubling time 23–59 s, trim offset −0.14 to −0.03.
The all-data bank cap (52.5 degrees) lies outside the range of every leave-one-out fit
(57.3–62.4). Three parameters sit on a search bound. Several local optima of similar total are
likely.

**What to do.** Run one full sweep at run-I scale with the round-3 laws enabled, as a declared
alternative beside the current production dynamics, not as a replacement. Report the held-out
log evidence and the impact-latitude median before and after, per contract rule 11. Report
impact energy, flight-path angle and duration from this arm **as a labelled sensitivity**, which
is what the task is for: it is the route to quoting those fields at all while the gate is open.

**Cost.** One sweep, 41.9 CPU-hours, 3.5 wall-hours at 12 threads. Run it under the heavy lock.

**Acceptance.** Rule-11 before-and-after table; the round-3 parameter table with the
leave-one-out spread beside each value; a COVERAGE section; the energy, angle and duration
distributions labelled as a sensitivity on uncalibrated dynamics.

### Out of scope for both tasks
Any change to the 00:19 likelihood, the family priors, `crates/ocean`, `crates/compose`, or the
core filter. Any new core request. Pooling run I with run-i-dive. Re-running the 22:41
asymmetry arm, which is complete and immaterial (at most 0.031 nat, 0.008 of any family share).

### Stop conditions
Stop and report if the round-3 sweep's held-out log evidence moves by more than 1 nat from the
production arm — that would mean the laws are changing the answer and not just the shape; if
the prior-recovery check fails; or if the dive-probability question turns out to need a prior
decision Pete has not made.

### Verbatim caveat wording
> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

---

## 2. OCEAN_DRIFT_MODULE — item 9

### Task — the Australian-coast non-recovery sensitivities, before the full run

**Why this comes first.** The interim pilot, reach-limited to 15–120 E on GLORYS12, moves the
drift-only median from about 30.7 S to 28.2 S — **north** — because southern impacts put 15–22
per cent of floating debris on Australian coasts where nothing was found. The core impact
estimate is near 37 S, so the term as pre-registered widens the drift-against-core disagreement
rather than resolving it. Before spending 30–34 hours on the full both-model run with 120–160 E
fields, establish whether that direction survives the weighting at all.

**What to do.** Run the pre-registered sensitivities on the interim pilot, on fields already on
disk: option A, option C, the term switched off, and the searcher variant (the Blaine Gibson
effect on Mozambique and Madagascar), against the pre-registered primary option B (city and
inner regional 1, outer regional 0.3, remote 0.05, relative to find coasts 0.1/0.5/1). Report
for each: the drift-only median and 90 per cent interval, the share of floating debris reaching
Australian coasts by source latitude, and the change in log evidence.

**The question to answer in one sentence.** Is the northward movement a property of the
non-recovery evidence, or a property of the remoteness weighting?

**Out of scope.** The full 120–160 E run. Any new ocean product. Any composition. Changing the
pre-registered option definitions — they are pre-registered and are to be run as written.

**Stop condition.** Stop and report if the direction reverses under any sensitivity, because
that changes what the paper must say and is Pete's decision, not the module's.

**Verbatim caveat wording.**
> Reach-limited pilot, 15–120 E, GLORYS12 only. Debris that would travel east of 120 E is not
> tracked, which is the population this term is about. Not to be composed until the full pilot
> runs.

---

## 3. PAPER_CITATIONS_MODULE — item 6

### Task — the Holland influence audit

This is owed from the 12 October note and has not been delivered. Pete regards Holland's 00:19
start-up term as questionable and wants its influence on the method audited, because it shaped
the original search.

**What to do.** List every place Holland's work enters this project's method or calibration.
The known entry points, which are a starting list and not a complete one: the 18:25–18:27 BFO
exclusion; the D4 and D5 treatments of the 00:19 bursts; the end-of-flight descent-rate bounds;
the Boeing 8-second window statistic. For each, give the evidence it rests on and **what changes
if it is removed**.

**Three facts already established that the audit must use rather than re-derive.** First, the
18:25:27 log-on is log-on 7 of the seven that *build* Holland's decay model; only its first
burst is set aside, and on signal-quality grounds (non-zero bit error rate, low carrier-to-noise
density), not because the transient does not apply. So the asymmetry is not "offset at 00:19,
none at 18:25". Second, the bench-test evidence behind the model is unpublished — his reference
[8], an internal study with no date, number or locator — while the seven-log-on calibration that
produces the 00:19 bounds is in the peer-reviewed article and is inspectable; the narrow claim
is the defensible one. Third, the ATSB did not use the 00:19 BFOs as a position likelihood at
all: they entered the search design through the corridor width, 25 NM either side of the 7th
arc, and no option in this project's sweep reproduces that use.

**Wording rule, mandatory.** Never "correction". Write "Holland transient bias added". Likewise
"R1200 BTO, empirical offset applied", never "corrected".

**Out of scope.** Any new analysis run, any change to a module's results, and any judgement on
whether Holland is right — the audit establishes what rests on him, not whether it is true.

**Acceptance.** A table of entry points with evidence and consequence-if-removed, posted as a
RECOMMENDATION in `coordination/PAPER.md`.

---

## 4. Not in these orders, and why

- **Item 4, the composition convention.** The ruling is the coordinating session's to write and
  Pete's to approve; the composition pass itself runs as a sub-agent, per Pete's standing
  ruling that the composer is not a Pete-facing thread. No module order needed.
- **Item 5, the fuel log-evidence decomposition.** Needs the engine to re-evaluate the fuel
  factor over a stored posterior, so it belongs with the next core session rather than a module.
- **Item 10, the targeted sampler.** Needs Pete's explicit GO and a core thread. See section 6.
- **Ocean transport.** Nothing in these three orders needs it. It becomes necessary only for
  the full 120–160 E drift pilot and for the Perth Canyon transmission-loss path, both of which
  are below the line.

---

## 5. Paste prompts

One new thread each, on the named profile. Paste the matching block as the first message.

### For END_OF_FLIGHT_MODULE

> Your work order is section 1 of `Claude Science Project Sep 29/threads/work-orders/work-order-2026-10-15.md`
> on branch `claude-science-sep29` (items 7 and 8:
> the dive-probability implementation fix and the round-3 laws as a labelled sensitivity). Read
> it in full first, including the standing facts at the top and the verbatim caveat wording.
> Then pull and read `coordination/END_OF_FLIGHT.md` before doing anything, and again before any
> commit. Work the tasks in the order given — Task A needs no run, Task B needs one sweep under
> the heavy lock. Do not start the sweep until Task A's table is posted. Keep going until
> nothing in the order is runnable, then name the blocker.

### For OCEAN_DRIFT_MODULE

> Your work order is section 2 of `Claude Science Project Sep 29/threads/work-orders/work-order-2026-10-15.md`
> on branch `claude-science-sep29` (item 9: the
> Australian-coast non-recovery sensitivities on the interim pilot, before the full run). Read
> it in full first, including the standing facts and the verbatim caveat wording. Then pull and
> read `coordination/OCEAN_DRIFT.md` before doing anything, and again before any commit. Run the
> pre-registered sensitivities as written; do not start the full 120–160 E run. Keep going until
> nothing in the order is runnable, then name the blocker.

### For PAPER_CITATIONS_MODULE

> Your work order is section 3 of `Claude Science Project Sep 29/threads/work-orders/work-order-2026-10-15.md`
> on branch `claude-science-sep29` (item 6: the
> Holland influence audit). Read it in full first, including the three established facts you
> must use rather than re-derive, and the mandatory wording rule. Then pull and read
> `coordination/PAPER.md` before doing anything, and again before any commit. Post the audit as
> a RECOMMENDATION there. No runs are needed. Keep going until nothing in the order is
> runnable, then name the blocker.

---

## 6. Item 10 — which thread

**Recommendation: a new core thread with a work order, not the existing one.**

The measured case for a new thread is strong. The existing core engine thread runs at 378 input
tokens per output token after 13 days and about USD 834; fresh short threads run 79–203. A clean
thread is worth roughly a factor of two on re-read, which at overage rates is the difference
between tens and low hundreds of dollars for the same work.

The case against — the one real risk — is that core owns `filter.rs`, `config.rs` and `main.rs`
and regression-gates them, and the byte-identity smoke gate depends on the engine's random-number
discipline, which is high-transfer knowledge a fresh thread does not have. That is manageable
because core request 9 is **already built and never used**, so the task is to wire and validate
an existing component rather than design one.

**The mitigation, which must be in the work order.** Name the regression gates explicitly: the
byte-identity check that seed 1 of the base configuration returns log evidence
−96.66146918417472 to every digit after any change to the step loop; `make scope`; the smoke
byte-identity gate against the current binary; and the requirement that the aimed proposal
recover its latents uniform on their full support under the sampling weight alone, which the
end-of-flight aimed proposals already demonstrate at a maximum deviation of 0.0030.

**Do not send it while a long run is live** — a prompt there can start core requests that
rebuild the binary and load the machine under a running job.
