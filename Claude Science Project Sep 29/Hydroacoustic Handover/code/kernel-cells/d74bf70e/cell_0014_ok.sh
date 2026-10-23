cd "repo/Claude Science Project Sep 29/coordination"
cat >> architecture.md <<'EOF'

## 2026-10-08 — hydroacoustics, first entry: plan check before anything is built

Session opened today, in the thread Pete switched to this profile. Read this branch's
`threads/master-prompts/hydroacoustics.md` (27,457 B, which includes the 8 October impact-source
section), `ISO Sept 28 Status/threads/master-prompts/common.txt`, `ARCHITECTURE.md`, and both entries
in my inbox. Nothing is built and no branch is cut yet. **One hazard for other sessions:** the
artifact-store copy of `hydroacoustics.md` is 21,693 B and predates both the impact-source section and
`d054f21`. It is stale, and only the repo copy should be read.

### Inbox acknowledged

All five 7 October items and all four 8 October items are accepted as binding: predictive-only as a
mode returning zero until injection-recovery yields P_D against received level; Blackman as the engine
validation, with air8 at H01 as the negative control and the JD144 10:54:57.77 row checked against the
page image; the synthetic composer test before any detection method; 5.3σ / 4.4σ pre-registered, with
significance from time slides and burst-preserving surrogates; no Kadri-bundle markdown, ever. Three
durations kept distinct. No duration is inferred from a received signal and returned. Coupling
efficiency is a declared alternative with a prior and is spanned by the injection-recovery study. The
AGW and SOFAR branches split on tau against `f_c = c/4H` at each sample's own depth.

I am reading end of flight's naming as controlling: `energy_transfer_tau90_s` only, never
`dissipation_tau_s`. The energy budget opens on `kinetic_energy_j` and `vertical_kinetic_energy_j`,
which are an **upper bound** on what the water received and are never aliased to
`impact_energy_transferred_j`.

### Data inventory: what the brief says is held, against what I can find

- **On the branch:** `ucrl-tr-207323.pdf` and `.txt` (Blackman), `brown2026.pdf` (F-35A/H11),
  `duncan-fig3.png` and `duncan-fig5.png`, the CMST 2014-30 report, the IMOS metadata and calibration
  notes, `kadri2024.txt`, `kadri-S1.txt` and `kadri-poster.txt`. Also the prior session's
  IMOS detection-control and detection-probability outputs under
  `ISO Sept 28 Status/results/worktree-hydroacoustics/`, which I will review critically as prior work
  and not port.
- **Only in the withdrawn archive:** `observed-transient-candidates.csv`,
  `two-station-correlation-config.json`, `aligned-detection-config.json` and the raw-triad schema.
  `kadri-table1-transients.csv` alone is also in `ISO Sept 28 Status/inputs/recovered-v01`. I will read
  the configs for their parameters and rewrite them, never copy them, and I will not open the bundle's
  markdown at all.
- **On the Drive:** `blackman_receiver_observations.csv` (7,392 B), the `imos` and `imos-acoustic`
  folders, and `imos-analysis.log`.
- **Not found under the name the brief uses:** `Blackman_2004_extracted_data`, meaning the air1–air9
  shot lines, the 2003 A1–A11 events and the source-class table. Question 1 below.

### Proposed order

The brief's §7 sequence stands. I propose one change of scheduling, not of substance:

0. **Scaffold.** Cut `hypothesis/hydroacoustics` from `claude-science-sep29`. Create
   `hypotheses/hydroacoustics/` from `_template`, in predictive mode, declaring its observation IDs
   and its alternatives (η, and the branch), and returning zero. Port the three archived tests: zero
   range, energy ×4 giving pressure ×2, and the H01W/H08S scale. Rebuild the station coordinates
   from one documented source. Scope is checked by the core-request-11 working-branch convention.
1. **Run the synthetic composer test (§7 step 2) alongside the Blackman validation (step 1), not
   after it.** The test needs only an arrival-time model with stated uncertainty — the group speed
   along the geodesic, with a declared σ_t — and an impact-sample set. Its verdict is the move in the
   impact PDF caused by a synthetic detection at one, two or three of H01, H08S and H08N, with O−C
   inside the uncertainty, compared against that uncertainty. It is days of work, needs no propagation
   engine, and the inbox says it reorders everything after it. Blackman, which needs the propagation
   stack, follows on as soon as question 4 is answered.
2. In parallel, as cheap work blocked by nothing: the literature review and the critical review of
   the prior work on this case (deliverable 2); digitising Duncan's figure 3 into a predicted-level
   prior, labelled as digitised with its method; and checking the JD144 row against the page image.

### Positions on brief §14

1. **Grid or samples.** I defer the decision itself until step 3 measures the arrival-variation rate,
   as the brief says. One framing should be settled now, though. Under rules 3 and 6, the likelihood
   is evaluated **per shared impact sample, always**. A source-position grid is admissible only as a
   cache of propagation quantities (transmission loss, travel time and blockage per station, per
   band), interpolated to each sample, and never as a likelihood smoothed over location. Confirm.
2. **Bathymetry.** I endorse settling's question 3: one surface, and one owner. My requirement
   differs from settling's in extent, and that should inform who owns it. Hydroacoustics needs depth
   **along great-circle paths of 1,600 to about 8,500 km** to H01, H08 and, for the F-35 source
   calibration, H11, not only at the impact point, because Duncan's figure 5 shows the seafloor rising
   above the channel axis along the path. A GEBCO-resolution surface suffices along path. AusSeabed is
   needed only near the source.
3. **A module returning zero until calibrated.** I propose that in predictive mode
   `impact_log_likelihood` returns exactly **0.0, not NaN**. No data used is a constant likelihood,
   which is exact, whereas NaN means "not computed" and the composer may treat it differently. The
   module would still be selectable, would carry `mode = "predictive"` in `hypothesis.toml`, and would
   be labelled in `summary.json` as contributing nothing. This is a composer requirement, so it needs
   your ruling for the composer thread.
4. **Environment.** This is a core request, per brief §12. The proposed stack is a dedicated conda
   environment for the analysis side only, so the engine's Python is untouched: scipy; obspy, for the
   IMS/IDC formats, filtering and response; geographiclib, for geodesics; netCDF4 or xarray, for the
   gridded ocean and bathymetry; and one propagation code. My candidates are KRAKEN normal modes
   (Acoustics Toolbox) for the SOFAR branch with RAM PE as the cross-check, and a modal AGW solver
   written within the module. TEOS-10 sound speed I take from shared ocean transport, per settling's
   question 5, which I also endorse.

### Questions

1. **Where is `Blackman_2004_extracted_data`?** If it is lost, I will re-extract it from
   `ucrl-tr-207323.txt` against the PDF page images, using the same conservative rule (detection status
   never inferred from silence), and record the method.
2. **Which impact samples may the synthetic composer test use?** The brief forbids quoting a smoke run,
   and no full-scale integrated hand-off exists yet. I propose one of two declared stand-ins:
   (a) the `runs/handoff-smoke` impacts, used for **geometry only**, with the verdict stated as a ratio
   to its own uncertainty and marked "provisional, to be rerun on the full hand-off"; or (b) a
   parametric 7th-arc PDF at the core median of −37.225° with the stated 50% interval. I prefer (a) for
   its realistic cross-arc structure. Rule which.
3. **Confirm the two zero-versus-NaN semantics** of §14.3: 0.0 for "module selected, no data used",
   and NaN only for a sample the module could not compute — for example, an unblocked path that is
   unresolvable.
4. **Rule on the environment request** of §14.4: a dedicated conda environment in this module's
   sessions, or something else.
5. **Branch name** `hypothesis/hydroacoustics`, cut from `claude-science-sep29`. Confirm.

No download over a few MB is planned before question 4 is answered. The IMS data are not held
publicly, and the IMOS set is on the Drive, so nothing here needs disk.

— hydroacoustics
EOF
tail -5 architecture.md; wc -c architecture.md