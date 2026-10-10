# Overnight 10-11 October 2026: sequence, pre-approvals and routing (Pete approved)

Written by Modular Architecture at Pete's request, before he went offline. **Pete's pasting of the
overnight instruction into a thread is his approval of this plan for that module.** Every module reads it in
full. It ends when Pete is back and says so.

## 1. Rules for the night

1. **Do not wait for Pete.**
   - Work the items in §3 for your module, in order.
   - When a choice comes up that would need him, use the overnight rule of 9 October:
     - record the question, the options and your recommendation in your inbox and in `architecture.md`;
     - take the recommended option, labelled **PROVISIONAL-OVERNIGHT**, and make it reversible;
     - carry on.
2. **Pre-approved means pre-approved.** The runs listed in §3 may start when their trigger fires, without
   asking. **No other large run may start**, and no listed run may be reshaped (particles, seeds,
   strata, stack). If a listed run fails a preflight or gate, stop it and record the reason, then go to
   your next item.
3. **Never, overnight:**
   - delete or move anyone's files or runs;
   - kill another module's job;
   - edit `config/davey2016.toml` or a frozen snapshot;
   - take any licence, publication or outreach action;
   - commit confidential material;
   - write credentials anywhere.
4. **The Mac is drift's.**
   - Outside the heavy lock, use at most 2 threads (`RAYON_NUM_THREADS=2`, `cargo -j 2`,
     `--test-threads 2`).
   - Anything heavier queues for `lockf -k /tmp/.mh370-heavy.lock` at 12 threads or fewer. Drift
     releases the lock between chunks, so a queued job runs at the next chunk boundary.
   - The load average was 46-71 on 18 cores at 03:10 UTC, so someone is over budget. Check your own
     jobs.
5. **deskstar (`ssh:deskstar`) is core's.** No other module submits to it overnight.
6. **Labels.** Every result carries its run, prior track, base config, platform, and the labels that
   apply: `uncorrected fuel`, `provisional sampler`, `PROVISIONAL-OVERNIGHT`, `SMOKE`. Every chart has a
   footnote beneath it.

## 2. How sessions stay awake and hear each other

- **Posting.** When you finish anything another module needs, append a short entry to **your own inbox,
  `architecture.md`, and every consumer inbox in the routing table below**. Then push. Pushing is the
  only signal.
- **Listening.** When nothing in §3 is runnable for you, start the watcher as a **background** cell.
  Then end your turn:

      sh "Claude Science Project Sep 29/threads/inbox-watch.sh" \
         "Claude Science Project Sep 29/coordination/<YOUR_INBOX>.md" [<absolute trigger file>] 8

  It wakes you when your inbox changes, when the trigger file appears, or after 8 h; restart it on a
  timeout. On waking: pull, read the new entries, act, post, and watch again.
- **Trigger files**, written by the producer when its outputs are complete and copied:
  - `/Users/pete/Downloads/mh370-exchange/core/next-run/READY`, written by core;
  - `/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/READY`, written by end of flight.

### Routing table

| Producer | What it posts | Post to (besides `architecture.md` and your own inbox) |
|---|---|---|
| core | large-run results, hand-offs, two-tank diagnostic | END_OF_FLIGHT, OCEAN_DRIFT, SEARCHED_AREAS, PLEIADES, OCEAN_SETTLING, HYDROACOUSTICS |
| end of flight | new impacts, the impact-time answer, H1/H2 evidence | SEARCHED_AREAS, PLEIADES, OCEAN_SETTLING, HYDROACOUSTICS, OCEAN_DRIFT |
| drift | production complete, merged surfaces | PLEIADES, SEARCHED_AREAS |
| settling | wreckage-field update | SEARCHED_AREAS, HYDROACOUSTICS, PLEIADES |
| searched areas / Pleiades / hydroacoustics | results on new impacts | the other two of these three, and END_OF_FLIGHT if a request |
| anyone | a core request | CORE_STAGES |

## 3. Sequence and pre-approved work

### Core (deskstar)

1. **Large run `a5839adc` (approved, running).** On landing:
   - Post the results: 00:19 and 00:11 medians and PDFs by stratum, P(family), the mixture, log Z, the
     split-half check, and the **two-tank diagnostic** (weight with the right engine dry before 00:11, by
     mode and stratum).
   - Copy the hand-offs (m2241, m0011), the impacts' parents and `tanks.npy` to
     `mh370-exchange/core/next-run/`, then write `READY`.
2. **If the diagnostic is 5% of weight or more,** start C-7(a): single-engine drift-down and speed before
   00:11.
   - Write the design note, then code it config-gated, with tests and a deskstar smoke at ladder scale.
   - **No large run with (a)** until Pete has read the diagnostic.
   - The one-engine ceiling and speed schedule come from the fuel session; architecture is commissioning
     them tonight.
3. **Pre-approved on deskstar after the large run:** the full-scale Davey-only baseline. That is
   `davey2016-inmarsat`, seeds 1-4, 7M per seed, at the same scale as reference-289, with no extensions.
   It is the paper's without-fuel comparison.
4. **Code only, each with tests and smokes, no large runs:**
   - request 10, the look-ahead at m2241 and m0011, which end of flight needs: only 800-900 effective
     parents per seed survive 22:41;
   - F6, F12 (float64 exhaustion time), F13 and F19;
   - requests 15, 4 and 12.

### End of flight (Mac)

1. **Now:**
   - answer architecture's impact-time question (`END_OF_FLIGHT.md` ~03:20 UTC);
   - analyse the 6-DOF fit case by case, at 2 threads.
2. **Pre-approved, on trigger `core/next-run/READY`:** the full sweep on the new hand-offs.
   - Run every 00:19 option in Pete's priority order: held out, R600 only, Holland H1, Holland H2, then
     `inflated`.
   - Use the two-tank exhaustion times and the descent idle floor.
   - Queue it under `lockf` at 12 threads; it runs between drift chunks.
   - Copy the impacts to `mh370-exchange/end-of-flight/next-run/`, write `READY` and post.
3. Then:
   - (ii), the survivor diagnosis;
   - H1 against H2 evidence;
   - the single-engine phase in the 6-DOF simulator, from the right engine's flame-out (design and
     smoke only).
4. **Not overnight:** a re-fit of the simulator under the lock. It waits until drift finishes.

### Drift (Mac, holds the lock by chunks)

1. Continue production: GLORYS12 chunks, then GlobCurrent chunks. Post a timing line per chunk to
   OCEAN_DRIFT.
2. When both models are complete:
   - merge them;
   - report split-half and the resolved fraction;
   - post.
3. On trigger `end-of-flight/next-run/READY`, score the drift likelihood on the new impacts. This is
   cheap and outside the lock.

### Searched areas, Pleiades, settling (Mac)

- **Pre-approved, on trigger `end-of-flight/next-run/READY`:** re-run your standard result on the new
  impacts at your usual scale. Use 4 threads or fewer, or queue under the lock if heavier.
  - Report across the 00:19 options, never as one number.
  - Searched areas, Pleiades and settling use the same impact set.
- **Until then:** work the methods draft and the citation ledger.

### Hydroacoustics (Mac)

- Wait for end of flight's ruling on impact times before 00:19:37 and after 01:15.
- Then re-derive your search windows from the new impacts on trigger `end-of-flight/next-run/READY`.
- **Until then:** work the methods draft and the citation ledger. Do not run KRAKEN batches above 2
  threads.

### Architecture

- Watch `architecture.md` and the two triggers.
- Review each landing against its acceptance gate. Post go/hold messages to the consumers' inboxes.
- Commission the fuel session for the one-engine ceiling and speed schedule.
- Keep a single morning summary for Pete in `architecture.md`: **"MORNING SUMMARY 11 Oct"**.
