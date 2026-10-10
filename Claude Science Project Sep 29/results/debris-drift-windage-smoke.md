# Debris drift: GlobCurrent windage smoke test (audit F1), 10 Oct 2026 ~22:15 UTC

**Interim, 92 of 367 nodes, not evidence.** Figure: `debris-drift-windage-smoke.png` (artifact 77b66a86).

**What was tested.** The GlobCurrent surface current already contains part of the wind drift. The production run
added the full object windage on top, as for GLORYS12 (audit F1). Here GlobCurrent chunk 0 (92 nodes) was re-run with
every drawn wind fraction reduced by 0.60 % and, separately, by 0.75 % of the 10 m wind speed. Everything else was
unchanged. Each arm is compared with the GLORYS12 production run on the same nodes.

| Measure (GlobCurrent − GLORYS12, log-likelihood) | as first run | −0.60 % | −0.75 % |
|---|---|---|---|
| Standard deviation of the difference, all 92 nodes | 3.33 | 1.94 | 1.88 |
| Standard deviation north of 30 S (32 nodes); audit threshold about 3.1 | 3.28 | 1.66 | 1.44 |
| Mean difference north of 25 S (9 nodes) | −5.78 | −2.19 | −1.57 |
| Mean difference south of 37 S (21 nodes) | +3.56 | +0.86 | −0.40 |
| Median by 4° band, south to north | +3.3, +1.7, +0.2, −0.9, −3.6 | +0.2, +0.5, 0.0, −0.7, −1.4 | −0.6, −0.5, −0.8, −0.7, −0.6 |
| Node correlation | −0.09 | +0.26 | +0.38 |
| Nodes within 2σ of combined split-half noise | 71 | 87 | 87 |
| GlobCurrent split-half noise | 0.63 | 0.96 | 1.11 |

**Results.**
1. **Both arms pass** the audit criterion. The northern deficit falls from −5.8 to −2.2 / −1.6 (9 nodes only, so
   weakly determined).
2. **At −0.75 % the latitude trend between the two models is gone.** The difference is flat at about −0.6 in every
   band. A flat offset does not move a position estimate. This contradicts the audit's provisional expectation of a
   real southern GlobCurrent excess of +0.8 to +2.8; at −0.60 % a smaller excess (+0.9) remains.
3. **Lower windage raises the Monte Carlo noise** of GlobCurrent (0.63 → 1.11), because fewer particles reach the
   rare finds. The re-run should keep 10^5 particles per node.
4. The arms took 6,288 s and 9,147 s at 12 threads. Lower windage gives longer drift times, plus machine load.
   A four-chunk re-run is about 8-10 h.

**Choosing the offset.** The offset must come from evidence independent of the debris. Choosing whichever value makes
the two models agree best would condition the drift term on itself. Two independent estimates exist:
- 0.74 % from the gridded difference of the two currents, 2014-2017 [audit];
- 0.61 % from the undrogued-drifter fits (1.36 % − 0.75 %) [audit].

The audit's regional range is 0.41-0.80 %.

**Run provenance.** Smoke runs `debris-drift-smoke-f1-globcurrent-060` and `-075` (configs
`smoke-f1-globcurrent-{060,075}.toml`; binary e455c56105a5a951; hypothesis/debris-drift 5ba6557); GLORYS12 and
GlobCurrent production as in `debris-drift-production-complete.md`; track 289.7 (reference-289); Darwin arm64 macOS 27.2.
