# SEARCHED_AREAS inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture: start here

`threads/master-prompts/searched-areas.md` is authoritative and supersedes the ISO `.txt`.

**Four things before you design anything.**

1. **Average alternative settling draws; never multiply them.** They are alternative outcomes, not
   extra wreckage. There is a test for it in section 8 and it is the easiest error in the module.
2. **The residual PDF is a view in the composer, not a pipeline of yours.** You return one
   likelihood column. Never ingest a posterior that already contains it.
3. **Your first deliverable is a citation task.** Davey ch. 11 sets out the update and does not apply
   it; Stone et al. 2014 applied it to AF447. Both PDFs are in the artifact store. Get the printed pages
   into the ledger before anyone writes the novelty sentence.
4. **The surface search is drift's, not yours; bathymetric mapping excludes nothing.**

**Much is already built and approved** - the M3 migration at `b73541a`, the 0.01 deg bilinear coverage,
`ln L = 0` off searched ground. Port and reproduce before you change anything.

**Shared-ocean boundary applies:** bathymetry for terrain masking comes from the shared ocean-transport
owner. Raise what you need in `coordination/OCEAN_TRANSPORT.md`.

## 2026-10-08 - architecture: Davey ch. 11 alignment - read `results/davey-ch11-alignment.md`

Two required additions to your brief:

1. **The reduction test.** With rho = 0, a point target at the impact location and a single cumulative
   campaign, your likelihood must reproduce Davey's eq. 11.1, `[1 - P_D(x)]`, to numerical precision.
   That is what makes "we extend Davey" checkable.
2. **Report Davey's eq. 11.2, probability of success per candidate area, as an output** of every
   residual-PDF view. It is the quantity a search planner uses and it costs nothing.

## 2026-10-08 - architecture: overnight work plan

1. **The citation task**: Davey ref. [40] against the book's reference list; ch. 11 pp. 101-102 and Stone
   et al. 2014 into a project citation ledger at `results/citation-ledger.md`, by printed page.
2. **The detectable-target definition**, to `results/`, before code.
3. **Port the M3 module** onto `hypothesis/seabed-search` and reproduce the fixture numbers.
4. **The reduction test** to Davey eq. 11.1.
5. No downloads.

### Overnight rules for every module, 8-9 October (binding until Pete is back, ~08:30 MT)

- **CPU:** core's 16-hour run is live until about 08:30 MT. Build with `cargo ... -j 4` and run nothing
  heavier than 4 threads. If the core run is slowed, everything downstream waits on it.
- **Disk:** 38 GiB free and falling while core writes. **Download nothing** unless your entry below
  says you may, and then only within the stated cap. Never save a multi-GB file as an artifact. Never
  let free space fall below 25 GiB - check `df` before each file.
- **Nobody can answer you tonight.** If you hit a question only Pete or the architect can answer,
  write it in `coordination/architecture.md`, choose the more reversible option, label the work
  provisional, and keep going. Do not stop and wait.
- **Concurrent appends:** if a push conflicts on a coordination file, keep BOTH entries in
  chronological order. Never resolve by taking one side.
- **Finish the night with a dated entry in `coordination/architecture.md`**: what landed, with commit
  hashes; what is provisional and why; what you need in the morning.
