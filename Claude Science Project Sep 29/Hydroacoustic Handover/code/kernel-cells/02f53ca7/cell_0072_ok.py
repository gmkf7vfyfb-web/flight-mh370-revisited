out = {
 "block": "9 — TL recalibration (Refresh v2 §9 a, b, d)",
 "status": "done",
 "summary": ("Route 1 (EW0112 near-source source spectrum, forward model S0+AF−TL on shared sections, pipeline check 0.0 dB vs audit M1): "
             "slope −2.3±1.7 dB/oct H01W (PARTIAL), +0.5±1.3 H08S (PASS), shape 3.1/3.9 (PARTIAL), 78% of the 45-point geometry grid passes slope at both stations; "
             "common-mode slope after the source −1.2±1.8 dB/oct (was ~−9). LEVEL fails at every SL_B 230–240 (−11 to −16 dB) → verdict NOT EXPLAINED under the "
             "pre-registered rule; post hoc and labelled: the level test mixes a peak level with a spectrum level and is uninterpretable (new gap G23). C1 unchanged. "
             "Not blind (post hoc result of 11 Oct known); training case only. Route 2 (F-35A): NOT AVAILABLE — Brown 2026 arXiv has no F-35A waveform/spectrum "
             "(Digitisation track found the same, 9854c72); needs Metz et al. 2023 (closed). (b) air8 under the same source: H01W −39.0 dB FOLLOWS, H08S −1.2 dB "
             "CONSISTENT, still holds (descriptive; registered condition not met). (d) air7→H01W: adiabatic excess over observed air7≈air9, median 31.5–63 Hz: geodesic +56.8, "
             "N×2D +55.3, least-loss ±20 km +36.5 → NOT REPRODUCED; exploratory +40/+50 km still +25; RAM coupled modes +19.1/+15.7/+18.1 dB (geodesic/+20/+50): the ridge "
             "is an adiabatic artefact (35–55 dB overstated), a path-wide 15–20 dB excess remains in both models (likely noise-selected ceiling in Fig. 23 and/or near-source "
             "loss at air7). G22 partly explained, still open; proposed status line and two rulings posted in coordination/architecture.md."),
 "commits": ["e949144 (module: pre-registration)", "150da8d (module: implementation + results-data)", "48d28b7 (module: amendment 3 RAM + final charts script)",
             "c51c0c5 (work: addendum + 3 charts)", "2a332a7 (work: RAM update, route 2 final, coordination entry)"],
 "results_notes": ["Claude Science Project Sep 29/results/hydroacoustics-blackman-validation.md (addendum 22 Oct 2026)",
                   "results/hydroacoustics-air9-ew0112-predicted-vs-measured.png/.pdf", "results/hydroacoustics-air9-ew0112-residual-vs-frequency.png/.pdf",
                   "results/hydroacoustics-air7-corridor-sensitivity.png/.pdf", "coordination/architecture.md entry 2026-10-22 03:20Z"],
 "exchange_paths": ["/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal/ (sections + logs, 15 MB; scratch deleted)",
                    "module branch results-data/tl_recal_block9/ (7.5 MB: tl_runs, route1_*, air8_recal, air7_corridor, air7_ram*, nx2d_air7-H01W)"],
 "key_numbers": ("Route 1 nominal: H01W slope −2.3±1.7 dB/oct, level −11.5 dB, shape 3.1; H08S slope +0.5±1.3, level −15.9, shape 3.9; grid 35/45 pass slope; "
                 "common mode slope −1.2±1.8 (before ≈ −9); station difference slope 2.2±0.3 (PARTIAL). air8: ΔRL H01W −39.0, H08S −1.2 dB. air7: KRAKEN excess 56.8/55.3/36.5 dB "
                 "(geodesic/N×2D/±20 km), +50 km 25.1; RAM 19.1/15.7/18.1 dB; RAM−KRAKEN on geodesic −27 to −56 dB, on air9 −5.4 to +0.4. Wall: KRAKEN 131 runs 2.5 min (3 proc), "
                 "N×2D 119 runs 7.6 min (1 proc), RAM 16 runs ~50 min (3–4 proc)."),
 "gaps": ["G22 partly explained (ridge = adiabatic artefact), still open for a path-wide 15–20 dB excess; proposed status line posted",
          "G23 (new, declared): route 1 level test uninterpretable — needs a unit-consistent measured received level (Blackman processing or Kadri archive)",
          "Route 2 not available: no F-35A spectrum in Brown 2026; Metz et al. 2023 not held",
          "C1 unchanged (slope misfit); C2 unchanged (η not calibrated); independent-site confirmation of the EW0112 source model still NOT TESTABLE",
          "z_s 10 m only for steps (b) and (d); offsets beyond ±20 km and RAM are exploratory amendments 2–3, not part of the registered verdicts"],
 "next": "Nothing further runnable in block 9. Awaiting rulings: (1) re-register route 1 with slope+shape only; (2) adopt RAM in place of adiabatic KRAKEN on sill-crossing MH370 paths.",
 "blocker": "none for this block"
}
r = host.submit_output(out,
    completion_bullets=["Pre-registered and ran the EW0112 forward source model: slope within 3 dB/oct at both stations, level test fails (uninterpretable units) → NOT EXPLAINED as registered",
                        "Confirmed air8 negative control still holds under the same source model",
                        "Ran N×2D, ±20 km 3-D proxy and RAM on air7→H01W: ridge loss is an adiabatic artefact; 15–20 dB path-wide excess remains (G22 partly explained)",
                        "Committed addendum, three footnoted charts, code/data and a coordination entry with two rulings requested"],
    deviations=["Route 2 (F-35A spectral shape) not computed: Brown et al. 2026 contains no F-35A waveform or spectrum figure (confirmed independently by the Digitisation track), so no digitisation was possible; polling stopped at 03:10 UTC instead of hour 3",
                "Step (b) was computed although its pre-registered condition (route 1 EXPLAINED/PARTLY) was not met; reported as descriptive",
                "Steps (b) and (d) at source depth 10 m only (9/12 m not run); air7 bands 16–63 Hz (80 Hz omitted); RAM at 31.5–63 Hz on three paths only",
                "Offsets +30/+40/+50 km and the RAM set are post-registration exploratory amendments (2, 3), labelled; registered verdicts rest on the ±20 km adiabatic set",
                "Brown 2026 was read from the arXiv PDF (no papers folder on the module branch) — declared substitution"])
print(r)