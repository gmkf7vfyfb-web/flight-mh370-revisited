# Hydroacoustics: agent proposals waiting for Pete

*Built 23 Oct 2026 in the hydro clean-up run. A proposal is not a rule. When Pete rules, move his words to `decisions.md` and mark the row here.*

| id | proposal | origin | status |
|---|---|---|---|
| X01 | Energy feasibility ladder: coupling at q99 energy vs the F-35A value; <=10x feasible, 10-100x strained, >100x not feasible, >1 impossible | Take 2 review (a35831fe), 22 Oct | open. The register uses only the physics limit (coupling > 1 impossible) and gives the numbers. |
| X02 | Adopt the Metz-derived F-35A value 2.26e-3 (z_s 10 m, tau >= 1.1 s, with its spread) as one point of the coupling prior | metz-f35a track, coordination/architecture.md 22 Oct | open; Pete ruled 23 Oct that coupling is a prior range and the F-35A value is one point in it |
| X03 | Coupling prior bounds (currently log-uniform 1e-6 to 1e-2, 41 points) | composition track 22 Oct (agent choice) | open; if changed, run-j-gated-v2 default column must be rebuilt (~86 min) |
| X04 | H08S airgun coincidence window 1.5 s (chance 3/10 for a 10 s shot cadence) | Take 2 review | open; used as a label only |
| X05 | Royer known-event tolerance: cross-ID tolerance; H01W arrows +/-20 s; pick bars +/-2 s | clean-up run 23 Oct | open |
| X06 | Validate detector and timing on real same-ocean arrivals (Royer events, CMST 01:34) before any MH370 claim (gap G-W1, defect D05) | Take 2 review item 3; proposal v6 | open; next work card |
| X07 | Search all held IMOS records, not only the pre-registered windows (defect D24) | Take 2 review finding 14 | open |
| X08 | San Juan real-arrival test of the matched filter | 22 Oct module thread | open; Pete chose to wait for it before the downstream re-run |
| X09 | Amplitude-aware match term in the likelihood (gap G11-1) | composition track 22 Oct | open |
| X10 | Pre-registered crash-panel timing test with bathymetry paths, T-phase paths, primary-report inputs, IMS station positions, digitised boxes for every panel (defect D13) | clean-up session 23 Oct | open; before any question goes to Kadri |
| X11 | Replace the predicted-loudness chart per candidate with: implied coupling from each member, and what the other stations should have recorded | Take 2 review 22 Oct | open |
| X12 | Rewrite the Kadri package text (REQUESTS E1/E4, cover note) after the register: H01W 00:52:04 is time-consistent with Royer icequake A; H08S 01:12:49 coincides with an airgun shot | clean-up run 23 Oct | open; v3 predictions table built, text not rewritten |
| X13 | Independent verifier agent on every result before it goes to Pete | proposal v3-v6 | approved as part of the clean-up plan (Pete, 23 Oct: "OK, do the overnight run as proposed") |
| X14 | Parallel tracks only for mechanical compute with fixed registry inputs and a coded acceptance test | proposal v3-v6 | open |
| X15 | "One track in sequence" for re-runs | agent offer, thread 676a6e64 msg 429; repeated in a35831fe | NOT a rule. Pete, 23 Oct: "I didn't make a rule about one sequential track". |
| X16 | Source-depth and pulse-duration sensitivity in the MH370 level chain (defect D25) | Take 2 review item 7 | open |
| X17 | Ask Pete for the IMOS 3315 and 3275 March 2014 background (Curtin) to replace the paired-logger stand-in (defect D06) | Take 2 review item 12 | open |
