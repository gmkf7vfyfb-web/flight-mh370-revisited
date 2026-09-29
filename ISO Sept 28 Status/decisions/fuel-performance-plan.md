---
name: fuel-performance-plan
description: Pete-approved plan for core fuel/performance state (starts after phase 1 core/stages merges)
metadata:
  node_type: memory
  type: project
  originSessionId: c924a4ee-d933-4d28-bd74-6dd738e4c3d8
  modified: 2026-09-28T18:37:57.475Z
---

Relayed by thr_4pbhvf3sxi on 2026-09-25 as approved by Pete. Starts after phase 1 (see [[thread-coordination]]).

- **Fuel state** in crates/flight: remaining fuel, burn rate, and exhaustion time/position.
  - Neutral: it never removes paths, so the Davey base stays byte-identical.
  - Total fuel only; there is no public left/right tank split.
- **Starting-fuel prior:** the ACARS anchor, 43,800 kg at 17:06:43 (Malaysian SIR Table 1.9A), plus the uncertainty in the 17:07–18:01/18:22 burn.
  - Exclude the legacy 18:22 fuel, the 0.45 t s.d. and any 00:17:30 exhaustion calibration. All are circular with the 00:19 events.
- **Fuel-flow tables:** from /jackbox/home/MH370-inputs/fuel/ulich-9M-MRO-fuel-model-v5.6-public.xlsm.
  - Take only the raw tables (LRC, M0.84, holding, MRC, CI 52, engine-out). Never use the endurance sheet.
  - The tables are marked Boeing-confidential: extract them into an ignored data file, never commit or redistribute them.
  - Record provenance in README. Tests use synthetic tables.
- **Validation** (public, not fitted to arc 1 or later):
  - SIR App 1.6E Table 3: 10,276 kg burned from 17:06:43 to arc 1, leaving 33,524 kg.
  - Table 4: endurances of 4.2–6.8 h from arc 1 for 22 altitude/speed pairs.
  - Source text: /jackbox/home/MH370-inputs/end-of-flight/report-text/boeing_performance_appendix_1_6E.txt.
  - Do not reuse the old OpenAP/ICAO/BFFM2 proxy; it over-burned Table 3 by 41%.
- **Prep done (commits 474c3e0, f17f977):** .sources/fuel-performance/extract.py writes the ignored data/fuel-tables.json; validate.py computes per-item implied factors.
- **Approved uncertainty model** (architecture review, 2026-09-25):
  - Fuel-flow factor ~ N(1.009, 0.018), from the 11 in-range items.
  - Plus an extrapolation term of about 3% per 0.01 Mach above 0.85, a comparable term below the holding schedule, and no coverage below FL060.
  - Sign convention: implied factor = model flow / required flow, so divide the model flow by it. The doc comment must say so.
  - Per trajectory, record the fraction of burn computed by extrapolation and widen the uncertainty accordingly. Never extrapolate silently. Descents are unpowered, so FL060 doesn't matter.
  - The doc comment lists the cell classes used (fppm-*, plus derived MRC/CI52 identified separately); fillers are never used.
- **Architecture notes for the element plan (2026-09-28):**
  - Temperature correction: the FPPM footnote reads "3% per 10 °C above/below standard TAT". At a given Mach, TAT = SAT·(1 + 0.2 M²) (recovery factor ≈ 1), so TAT − TAT_std = (1 + 0.2 M²)·(SAT − SAT_ISA), about 1.13 times the ISA deviation at M0.82. The two are not equal. Apply 3% per 10 °C to that TAT deviation, and cite the footnote in the doc comment.
  - Speed prior: do not make "M0.57–0.68 at FL350, 216 t" a pass condition (CL ≈ 0.88 there; a 1.3 g buffet margin is marginal). Take the envelope from the tables plus a documented public buffet margin, then report where the early groundspeeds fall. If they need a lower altitude, that is a finding, not a reason to widen the envelope.
  - The density inside the envelope is its own labelled prior choice. Show uniform-flyable against Davey's 0.73–0.84, with fuel on in both.
  - Quadrature: show once that results are stable to the node count (3 vs 5).
  - MH371: label it BTO-only; add BFO only with satellite+EAFC terms from an external source, never fitted to MH371.
- **End of flight (thr_kaycpkjz9k) needs, per trajectory:** the predicted exhaustion of total fuel (second flame-out), or the fuel state implying it, plus mass. It keeps the left/right imbalance and engine-order gap as its own parameters.
- **status.md headline when fuel lands:** 1.8% (1 s.d.) is about ±6–7 min over ~6 h from arc 1.
- **Independent check:** MH371 ACARS (/jackbox/home/MH370-inputs/acars/, sheet ACARS) has 5-minute gross weight and fuel on board.
- **The 00:19:29 log-on is used once**, by the end-of-flight stage (thr_kaycpkjz9k), which takes the flame-out time from our fuel state.

**Why:** the wide-Mach sensitivity revived the shoulder with slow paths. Endurance is the missing constraint that Davey's 0.73 Mach floor stood in for.
**How to apply:** after fuel lands, rerun the wide-Mach sensitivity with a fuel likelihood.
