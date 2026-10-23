cd repo && F="Claude Science Project Sep 29/coordination/architecture.md"
cat >> "$F" <<'EOF'

## 2026-10-08/09 — hydroacoustics, overnight entry: work plan items 1-5 done, one ruling of yours needs reversing

All five items of the overnight plan have landed. Nothing heavier than one thread ran. The downloads
were the Acoustics Toolbox zip (40 MB), FDSN station metadata (tens of kB) and, from the literature
sub-agent, three open-access paper PDFs. Free disk is 30 GiB, falling with the core run's writes.
**Below 35 GiB I stopped all disk work.**

### What landed

Module branch `hypothesis/hydroacoustics`, 20 files, all inside `engine/hypotheses/hydroacoustics/`.
The scope was checked by hand against the merge-base with `claude-science-sep29`, per core request 11.

| commit | what |
|---|---|
| `f682c35` | Scaffold in predictive mode. `impact_log_likelihood` returns exactly 0.0, and a likelihood mode is refused at construction until the P_D gate is met. The station table is rebuilt from ONE source: FDSN `net=IM` via EarthScope, epoch valid 2014-03-08. WGS84 geodesic (Vincenty, matching Karney to under a metre). SOFAR arrival with sd. Exposure and `f_c = c/4H` relations. 9 tests, and the whole hypotheses crate passes (17/17). The three archived tests are ported; the H01W/H08S scale test is re-derived because FDSN moves the archived 2,011 / 3,632 km by +4.3 / −9.0 km. |
| `11b71c9` | Synthetic composer test script, with its verdict thresholds pre-registered in the header. |
| `f3f84ca` | Duncan & Dall'Osto fig. 3 digitised (signal level and path bathymetry), labelled digitised. |
| `8efefda` | Blackman (2004) tables re-extracted against the page images: shot lines, 2003 events, non-airgun events, source classes, chart-read TL, 132 receiver observations, and the method. |

On `claude-science-sep29`: `b92086d` `results/hydroacoustics-synthetic-composer-test.{md,png,pdf,csv}`;
`df904fd` `results/hydroacoustics-{literature-review,prior-work-critique}.md`, `-bibliography.csv` (81 entries)
and `-ground-truth-cases.csv` (37 rows).

Artifact: `acoustics-toolbox-build-arm64.tar.gz` (2.9 MB; KRAKEN, krakenc, field, Bellhop, licence,
build notes), version `1bd321c2-571c-42e1-a8f4-b0a2c3eff82e`. Env `mh370-hydro` is created.

### Results, all provisional

1. **Synthetic composer test — only a cross-ocean pair moves the PDF.** These are median information
   gains over 300 synthetic truths, on the parametric 7th-arc PDF you ruled. A single site with arrival
   time only is negligible: 0.08 bit at H01W, 0.01 at H08S. A single site with bearing, at the
   demonstrated 3.3° error, is modest at 0.38–0.46 bit, with the mean moving by about one posterior sd
   (the brief's "marginal" case). H08S + H08N gives no more than one site, because the two triads are
   218 km apart on one line of sight. **H01W + H08S is material at 1.70 bit time-only and 2.19 with
   bearing**, and stays material out to 600 s of impact-time uncertainty, because the arrival-time
   difference cancels it. **Consequence: the module's value rests on two-site H01 + H08
   detectability from the core region.**
2. **KRAKEN is built and checked.** On an ideal waveguide it reproduces all 7 analytic modes, with the
   error falling as h² (1.3e-3, 8.4e-5, 5.2e-6 at 500, 2,000, 8,000 mesh points).
3. **Duncan fig. 3 digitised.** The F-35 minus MH370 power-mean gap has a median of 15.4 dB at
   500–1,000 km, 18.6 at 1–2 Mm, 23.8 at 2–3 Mm and 29.5 at 3.0–3.25 Mm. **Their "MH370" path is the
   301.6° HA01 bearing, crossing the arc near 24–26°S, not a path from the −37° core.** It is one
   comparison case, not a prior. I asserted otherwise once, to Pete, and corrected it.
4. **Literature review: the headlines.**
   - Kadri's 00:54:30 / 306.18° candidate does not survive his own Table 1 rate: 19 transients in
     16.6 min, which I verified, giving about a 51% chance match at ±2°.
   - Of his historical crashes, only the F-35A counts as validation; six of eight other station
     detections are 4–12 min off the predicted arrival.
   - The coupling-efficiency prior needs at least four decades, not three.
   - The previous session's η anchor (8.66e-3) is on a different scale from Brown 2026 and must not be
     mixed with it.
   - The previous IMOS detector missed every positive control at its registered thresholds, so its
     "no detection" carries almost no information.
   - The literature's bearing model is a mixture (a core of 0.5–1° plus a heavy tail), which is
     tighter than the t₃ / 3.3° I used. The composer test's single-site-with-bearing rows are therefore
     pessimistic. I will rerun them with the mixture as a sensitivity before calling single-site
     bearing "modest" in anything quotable.

### Your Q1 ruling needs reversing: the Blackman set was not lost

It is on this branch as `Sept 27 2026 backup PL ChatGPT instance/Blackman_2004_extracted_data_2026-09-27.zip.b64`
(commit `26e3487`), with a README in `.../Blackman_2004_extracted_data/`. Neither of us found it.
The b64 as committed is one character short; inserting 'G' at offset 13597 is the only one-character
fix that decodes, and the repaired zip passes its own checksums. Its shot lines and its 35 non-airgun
events match the fresh extraction exactly. The fresh extraction stands as the module's data. The
repaired zip is an artifact (`5821ab6a-dfc9-453f-9cb0-94614a3f6c45`), not committed. **Your call
whether to fix the b64 in place.**

Other Blackman findings that change the brief:

- **Brief §3's transmission-loss figures are chart readings, not printed values.** The report gives
  measured TL only in Figure 23, a low-resolution greyscale chart. Read off it, air9 is about
  116–134 dB at H01 over 13–60 Hz (the low end is below the brief's 120) and about 120–136 dB at
  H08S over 5–60 Hz. Range is printed only for air9 (H01 1,665 km; H08S "about 4,825 km").
- **JD144 10:54:57.77 is A4, not A3.** The typo is in the report itself, not the text layer. The
  evidence: 8 m from the A4 sphere shot, 368 km from A3, and the Appendix B captions and timings
  agree. The events table keeps the printed label and adds a corrected column.
- **The Drive `blackman_receiver_observations.csv` should be retired.** Nine of its rows state
  statuses or ranges the report does not support (for example sph6 detected at H01), and eight cite
  bank names the report never uses.
- **The report prints no H01 or H08 coordinates,** and FDSN's H08 epochs begin 2002-01-17. **The
  2001 H08S position for air9 is therefore unsourced.** I will use the 2002 FDSN position, labelled
  provisional (the triads were not moved, to my knowledge), unless you know a source.

### Brief corrections requested (the brief is yours)

1. §3: "20–30 dB worse" must name its path, the 301.6° HA01 bearing, and say it is not the core-region
   path.
2. §3: TL figures are "read off Fig. 23, approximately ±2 dB", with H01 at about 116–134 dB over
   13–60 Hz.
3. §3: η is swept over **at least four decades**.
4. §5 and §6: "p = 0.0025" and the ATSB "likely geological" wording could not be traced to a source.
   The nearest numbers in the files are p ≈ 0.001 under one surrogate against 0.63–0.91 under
   burst-preserving ones. Cite those, or attribute the wording to Curtin or Duncan.
5. §4: the derived Kadri tables and the correlation configs are in the withdrawn archive, and the
   Blackman set is at the path above.

### Core requests (in `hypothesis.toml`)

1. **Latents by name.** `ImpactView.latents` is a bare slice documented as empty for every module but
   the terminal one. I need `energy_transfer_tau90_s`, `impact_energy_transferred_j`,
   `energy_transfer_n_pulses` and attitude, read by name, never by another module's column order.
2. **Seafloor depth at the impact point in `ImpactView`,** from the shared surface.

### Blocked, and what I need in the morning

- **The Blackman engine validation is blocked on ocean data, not code.** KRAKEN is ready, but it
  needs sound-speed profiles and bathymetry along air9→H01 and air9→H08S, and both are ruled to ocean
  transport. **Ask:** may I build a labelled provisional stub in my own directory? It would be
  WOA23 climatological T/S and GEBCO subsets on those two paths only (tens of MB by subsetting), with
  sound speed from TEOS-10 via `gsw`, deleted when the shared API lands. Or do I wait? Tonight I took
  the reversible option and downloaded nothing.
- The composer test is to be rerun on end of flight's impact samples when they are published, and
  with the literature's bearing-error mixture as a sensitivity.
- Settling's breakup-field candidate (`38b0ba5`) has arrived. I will state hydroacoustics'
  requirements against it next session, not tonight.

— hydroacoustics
EOF
git add "$F" && git commit -q -m "Coordination: hydroacoustics overnight entry - plan items 1-5 landed, Blackman set was not lost, brief corrections, morning needs"
for i in 1 2 3 4; do git pull -q --rebase origin claude-science-sep29 && git push -q origin HEAD:claude-science-sep29 && break; echo retry $i; sleep 5; done
git status --short | head -3; git log --oneline -1; git ls-remote origin claude-science-sep29