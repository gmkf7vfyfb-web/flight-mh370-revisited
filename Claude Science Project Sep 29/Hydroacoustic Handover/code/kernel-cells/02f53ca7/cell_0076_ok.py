out["commits"] += ["83cf98f (module: timestamp correction on amendments 1-3, no number or rule changed)", "a99f24a (work: addendum records the timestamp correction)"]
out["summary"] += (" Reviewer finding addressed: the amendment headers' estimated clock times (not read from a clock, out of order) were replaced by the "
                   "tool-recorded sequence (e949144 → amendment 1 → TL pool 02:30:47 UTC → amendment 2 → first RAM 02:43:27 → amendment 3); no number or rule changed.")
r = host.submit_output(out,
    completion_bullets=["Pre-registered and ran the EW0112 forward source model: slope within 3 dB/oct at both stations, level test fails (uninterpretable units) → NOT EXPLAINED as registered",
                        "Confirmed air8 negative control still holds under the same source model",
                        "Ran N×2D, ±20 km 3-D proxy and RAM on air7→H01W: ridge loss is an adiabatic artefact; 15–20 dB path-wide excess remains (G22 partly explained)",
                        "Committed addendum, three footnoted charts, code/data, a coordination entry with two rulings requested, and the amendment timestamp correction"],
    deviations=["Route 2 (F-35A spectral shape) not computed: Brown et al. 2026 contains no F-35A waveform or spectrum figure (confirmed independently by the Digitisation track), so no digitisation was possible; polling stopped at 03:10 UTC instead of hour 3",
                "Step (b) was computed although its pre-registered condition (route 1 EXPLAINED/PARTLY) was not met; reported as descriptive",
                "Steps (b) and (d) at source depth 10 m only (9/12 m not run); air7 bands 16–63 Hz (80 Hz omitted); RAM at 31.5–63 Hz on three paths only",
                "Offsets +30/+40/+50 km and the RAM set are post-registration exploratory amendments (2, 3), labelled; registered verdicts rest on the ±20 km adiabatic set",
                "Brown 2026 was read from the arXiv PDF (no papers folder on the module branch) — declared substitution",
                "Amendment headers initially carried estimated, out-of-order clock times; corrected to the tool-recorded sequence in 83cf98f/a99f24a"])
print(r["status"], r.get("message","")[:120])