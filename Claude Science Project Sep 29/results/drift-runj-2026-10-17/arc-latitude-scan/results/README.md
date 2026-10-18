# Arc-latitude dedicated drift run: results (18 Oct 2026)

Run: 66 points (26-32 S at 1 deg, 3e5 particles; 33-40 S at 0.5 deg, 1e6), each on the run J median impact track and 50 NM either side;
both ocean models; 8 chunks on deskstar, all EXIT=0, 528 of 528 node values scored, none unresolved. First attempt killed by the
deskstar restart at 22:55Z on 17 Oct; rerun 23:58Z-13:41Z.
Monte Carlo noise (split halves): median 0.15-0.28 log-likelihood units per point (first look: 1.3-1.5 per pilot node).
Cross-check: finds term at the 66 points against the run A surface: scatter 0.75 (GlobCurrent) / 1.12 (GLORYS12), correlation 0.6,
consistent with run A node noise.

Posterior on run J D0 (two-model mixture; mean-latitude shift north, median, share in 37-38 S, share north of 33 S):
- finds only: shift +1.07 deg (split-half difference 0.03), median -36.57, 37-38 S 30.6%, north of 33 S 11.0%
- C (low detection): shift +3.41 deg (split-half difference 0.22), median -34.83, 37-38 S 10.4%, north of 33 S 34.1%
- B (primary): shift +5.51 deg (split-half difference 0.37), median -31.21, 37-38 S 3.1%, north of 33 S 58.3%
- populated coast only: shift +3.46 deg (split-half difference 0.21), median -34.85, 37-38 S 10.5%, north of 33 S 34.8%
- flight path only: mean -36.717, median -37.13, 37-38 S 46.6%, north of 33 S 3.2%.

Against the first look (existing data): finds only +0.70 -> +1.07; option B +4.83 -> +5.51; option C +2.88 -> +3.41;
populated coast only +4.45 (reconstructed with the saturating law) -> +3.46 (measured). The reconstruction overstated populated-only by about 1 deg.
Option C and populated coast only give almost the same result. Mass north of 33 S rests on the thin northern part of run J; labelled sensitivity.
Files: arclat-likelihood-profile.csv, arclat-posterior-summary.csv, arclat-node-tables.zip, figure arc-latitude-dedicated-run.png/pdf.
