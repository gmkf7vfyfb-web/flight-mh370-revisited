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
