# Compute rules for heavy runs on the Mac

Date: 9 November 2026. Ruling by Pete. Applies to every agent, thread, track and sub-agent that runs code on
Pete's Mac (64 GB, 18 cores). Supersedes nothing; it restates the 4 November rule after a second crash.

## What happened

- 3-4 November 2026: the fast-route generator was launched 5-8 seeds in parallel (9-18 GB each). Three kernel
  panics from memory exhaustion (compressor at 100 % of its segment limit, 43-65 swap files).
- 8-9 November 2026, 02:26 UTC: the ocean-drift session launched eight copies of `offline/df_core_seeds.py`
  in parallel, about 7 GB each (56 GB in total). The machine went down again. The session had checked with
  `ps` and seen zero processes: `ps`, `pgrep`, `top` and `sysctl` are blocked inside the sandbox, so that
  count was meaningless and the launch was never verified.

## Rules

1. Use the processors fully. Do not run one job at a time out of caution. Run as many jobs in parallel as the
   free memory allows, and not one more.
2. Before any parallel launch, measure one job's peak memory. Then concurrency = floor((available memory -
   10 GB headroom) / peak per job), capped at the core count. Repeat the check before each further launch.
3. Use `tools/memguard.py` for this. It does the measurement, the arithmetic and a watchdog in one step:
   - `python tools/memguard.py status` - available memory and the launch budget now;
   - `python tools/memguard.py measure -- CMD ...` - peak RSS of one job;
   - `python tools/memguard.py run --args 1 2 3 ... -- CMD {} ...` - measures job 1 alone, then runs the
     rest at the computed concurrency, stops launching below 6 GB available and terminates its children
     if the kernel's free-memory figure falls below 8 %. Logs in `memguard-logs/<arg>.log`.
   A hand-written `for s in ...; do (python job.py $s &); done` loop is not acceptable for anything above
   about 1 GB per job.
4. Never verify a launch with `ps`, `pgrep` or `top` from inside the sandbox. They return nothing or fail.
   Verify from the job's own log and output files, or from memguard's log.
5. Memory inside the sandbox: `vm_stat` and `memory_pressure` work (memguard uses them). Treat
   free + inactive + purgeable pages as available. Other sessions, Word, browsers and the kernels
   themselves share the same 64 GB: assume about 10 GB is in use by others at any time.
6. Prefer one process that loads the shared arrays once and loops over seeds to N processes that each load
   the same arrays. The eight `df_core_seeds.py` copies each loaded the same hand-off files.
7. When Pete says "pause all processes", stop everything and start nothing until he says to resume.
8. Jobs that need more than the budget allows at useful parallelism go to deskstar or another remote
   target (`list_compute`), not to the Mac in series.

## Standing-rule block

The following block is prepended to every master prompt and coordination inbox, after the labels rule:

> **STANDING RULE ON MEMORY (Pete, 9 Nov 2026). Applies to every agent, thread, track and sub-agent.**
> Parallel launches on the Mac have crashed it twice (3-4 Nov, 8-9 Nov). Before launching more than one heavy job,
> measure one job's peak memory and set the number of parallel jobs to floor((available - 10 GB) / peak), capped at
> the core count; use `tools/memguard.py run` which does this and watches memory. `ps`/`pgrep`/`top` are blocked in
> the sandbox and show zero processes: never use them to verify a launch. Use the processors fully, but never
> overcommit memory. Details: `coordination/COMPUTE-RULES.md`.
