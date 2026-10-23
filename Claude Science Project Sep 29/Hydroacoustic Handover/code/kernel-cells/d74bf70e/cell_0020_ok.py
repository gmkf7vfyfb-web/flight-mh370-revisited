common_ctx = """You are working for the Hydroacoustic Module of Pete Large's MH370 Bayesian reconstruction (reproduction/extension of Davey et al. 2016, aimed at Journal of Navigation).
Repo: github.com/gmkf7vfyfb-web/flight-mh370-revisited, branch claude-science-sep29 (~2.2 GB; clone with: git clone --filter=blob:none --no-checkout --single-branch -b claude-science-sep29 https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git repo, then sparse-checkout only the paths you need; declare the GitHub credential on the cell). Also run `git config --local core.excludesFile ""` in the clone.
Authoritative brief: 'Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md' (27,457 B on the branch; the artifact-store copy is STALE - do not use it). Read it before starting.
DO NOT commit or push anything - the lead hydroacoustics session integrates your outputs. Deliver everything as saved artifacts.
HARD PROVENANCE RULE: the Kadri bundle in 'Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/.../.sources/kadri-2024-hydroacoustics/' contains 23 markdown files including a private funding note with staff email addresses - never open, copy, quote or commit any .md file from it. CSV/JSON/PY there may be read for parameters only.
Digitised or re-extracted data is labelled as such with its extraction method; never presented as the underlying measurement. Never fabricate a value: if a number cannot be read, record it as missing with the reason."""

blackman = {
 "name": "Blackman",
 "context_summary": common_ctx,
 "task": """Re-extract the Blackman et al. (2004) LLNL report UCRL-TR-207323 tables into machine-readable CSVs, as ruled by the architecture session on 2026-10-08 (the earlier 'Blackman_2004_extracted_data' set is lost; only blackman_receiver_observations.csv survives on Google Drive, file id 1xCqnNIVYuH1iF2OIFEnNgbtAMHbzekkU, 7,392 B - fetch it via the google-drive connector and use it as a cross-check, not as truth).
Sources on the branch: 'ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.txt' and '.pdf'. Work from the text, and verify EVERY numeric row against rendered PDF page images (render with pymupdf / pypdfium2 and view them) - the text layer may be garbled.
Required outputs (save as artifacts):
1. blackman_shot_lines.csv - airgun lines air1..air9 (2001): Julian day, date, start/end time UTC, start/end lat/lon (decimal degrees, plus the as-printed DMS string), seafloor depth, shot interval, ranges to H01 and H08S (and H08N if given), and the source page number per row.
2. blackman_2003_events.csv - the 2003 A1..A11 events (and SUS charge site A11) with time, coordinates, source type, charge size/depth if given, page number.
3. blackman_source_classes.csv - the source-class characteristics (airgun array, cylinder and sphere sources, SUS) with levels/bands as printed.
4. blackman_transmission_loss.csv - every measured transmission-loss value or range the report gives per site/station/band (brief §3 cites ~120-133 dB at H01 over 10-60 Hz and 122-135 dB at H08S over 5-60 Hz for air9 - verify against the report and record what it actually says).
5. blackman_receiver_observations.csv - the conservative receiver-observations table: per source event and station, detected / not detected / not reported, with detection status NEVER inferred from silence (only explicit statements count; otherwise 'not reported'). Must include the air8 non-detection at H01. Diff against the Drive copy and list discrepancies.
6. jd144_check.txt plus a cropped page image PNG: the JD144 10:54:57.77 event is labelled A3 in the indexed text but its coordinates are essentially A4. Check against the original page image and give a verdict (which label is correct, and the evidence).
7. extraction_method.txt - method, tool versions, pages used, every judgement call, every unreadable value.
Also report: the station coordinates the report uses for H01 and H08 (as printed, with page).
Declare deviations at the top of your final response.""",
}

lit = {
 "name": "Literature",
 "context_summary": common_ctx,
 "task": """Deliver brief §10 item 2: (a) a literature review of the state of the art relevant to the hydroacoustics module, and (b) a critical review of the prior work on this case. Weight most heavily cases where subsequent ground truth became available.
Scope of (a), each with primary sources (DOIs; fetch full texts where open access and read them, do not rely on abstracts alone for load-bearing claims):
- Prior aircraft / vessel losses detected or searched for acoustically, and what ground truth later showed: e.g. ARA San Juan 2017 (CTBTO IMS detection, wreck found 2018), Kursk 2000, USS Scorpion 1968 (SOSUS), OceanGate Titan 2023, AF447 2009 search, the F-35A recorded at H11 (Brown et al. 2026, Icarus - on the branch at 'ISO Sept 28 Status/inputs/papers/hydroacoustics/brown2026.pdf'), and others you find. For each: source, energy, range, stations, detected or not, timing/location error vs ground truth.
- IMS hydroacoustic network calibration and long-range propagation modelling (Blackman 2004 UCRL-TR-207323 on the branch; de Groot-Hedlin; Heaney; Prior; normal-mode/PE methods at 1,000-8,500 km; bathymetric blockage).
- Acoustic energy coupling from an impacting body into the water column (water-entry acoustics, impact/explosion source levels, coupling efficiency eta estimates and their ranges).
- Acoustic-gravity wave theory and practice (Kadri, Stiassnie, Yamamoto, Eyov, Oliveira, Renzi and others; mode cutoff f_c = c/4H; detection claims and their verification).
- Detection statistics: look-elsewhere / trials factors, time-slide and burst-preserving surrogate nulls, injection-recovery for P_D.
Scope of (b): Kadri 2024 and S1 and his 2025 poster ('ISO Sept 28 Status/inputs/papers/hydroacoustics/kadri2024.txt', kadri-S1.txt, kadri-poster.txt); Duncan & Dall'Osto 2023 (figures 3 and 5 are on the branch as duncan-fig3.png, duncan-fig5.png; find the paper); Curtin CMST report 2014-30 (cmst-2014-30.txt); ATSB statements on the ~01:34 UTC HA01 event; and the PREVIOUS SESSION's own hydroacoustic work in 'ISO Sept 28 Status/results/worktree-hydroacoustics/' (read the json/pdf/png outputs) and the configs/summary JSON under the withdrawn archive's two-station-correlation outputs (not its .md). Assess each statistically: trials factor, null model, pre-registration, bearing-error distribution, whether the claimed significance survives.
Outputs (save as artifacts):
1. hydroacoustics-literature-review.md - structured, concise, sourced; each claim cited; ends with 'Implications for this module' as numbered items tied to brief sections.
2. hydroacoustics-prior-work-critique.md - per prior work: claim, evidence, statistical assessment, verdict, what to reproduce.
3. hydroacoustics-bibliography.csv - key, authors, year, title, venue, DOI/URL, open-access status, which section uses it, ground-truth case (y/n).
4. ground-truth-cases.csv - one row per acoustic-loss case with the quantitative fields above.
Respect copyright: paraphrase, quotes under 20 words. Declare deviations at the top of your final response.""",
}
descs = host.delegate([blackman, lit], wait=False)
fids = [d["frame_id"] for d in descs]
print(fids)
