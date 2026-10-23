# Independent verification of the 23 Oct 2026 clean-up

*ASD-STE100 for work-specific text.* The verifier was a separate sub-agent (frame e5e68baf, profile OPERON, model claude-opus-5-5).
It had its own working folder and its own clones of the repo. It did not edit any file. The same model family made the clean-up, so the check is independent in context, not in model.

## Pass 1 (before fixes): `verifier_pass1_2026-10-23.json`

Checked 15 items. These reproduced from the raw files:
- registry sha256: 40 of 40 random files, and every file in the WORK and ART manifests;
- the Take 2 gate counts (35 and 1,111 rows below band; 63, 2,584 and 11,067 Scott Reef rows; 44 of 47 airgun coincidences);
- the land path (201 of 2,000 points; 0 for the four 37.1S paths); the Royer checks; the register flag counts and 10 re-derived rows;
- the energy grid and coupling multiples (within 0.3 %); 52 of 52 quotes of Pete; the 13 banners; INDEX against the registry; the live profile; 9 of 9 tests.

It found 8 errors (error register V-01 to V-08).
Declared limits: the land path was re-derived for 10 rows only; the IMOS transmission-loss quantiles were not recomputed; the total of 46 sessions was not checked.

## Pass 2 (after fixes): `verifier_pass2_recheck_2026-10-23.json`

Checked against module branch be85de9 and work branch f2a2b5c. Result: FIXED 6 (V-01, V-02, V-05, V-06, V-07, V-08), PARTLY 2 (V-03, V-04).
Regression: `check_registry.py --verify` gave 0 differences, 9 of 9 tests passed, and the register counts, banners, INDEX and live profile agree.
Declared limit: the pass 1 random hashes, land path, energy grid and row re-derivation were not repeated.

## After pass 2 (not re-verified by the verifier)

- V-04: the docstring now says "SNR at eta 2.1e-4 (Brown 2026 Arons-equivalent; not the F-35A value)". The meta key `eta_anchor` is now `eta_snr_column`, with a note. v3 was rebuilt.
- V-05: ERRATA item 4 now lists all three H08S shot-subtraction residual rows (01:07:37, 01:07:52 and 01:19:37). The unverified "near the H01W lag" is removed.
- V-01: the reason text for non-finite energy now also names "latitude outside the energy grid". No row has this reason.
- V-03: proposals X03 now states the truncation. Line 171 of the Metz note keeps its old text, because notes are not rewritten. INDEX lists it as a STALE line.
