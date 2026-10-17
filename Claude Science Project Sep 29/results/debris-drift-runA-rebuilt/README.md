# Run A debris-drift surfaces, rebuilt 16 Oct 2026 (no transport)

The run A per-node surfaces (GLORYS12V1 0.494 m + ERA5 and GlobCurrent my-p1d 0 m + ERA5 with product-relative windage; 710 nodes on the
41 x 38 grid lat0 -41.1667, lon0 83.9623, dlat 0.5, dlon 0.58563; bandwidths 25/50/100/200 km) existed only in the drift thread's session
workspace, which was swept. They were rebuilt by the architecture stand-in from the per-impact drift columns that survive on the Mac
(`mh370-exchange/debris-drift/run-i-dive/<stratum>/seed-1/drift-lnL.npy`, 16.0 M impacts, the four strata' seed 1, row-aligned with end of
flight's run-i-dive impacts, parent index checked equal row by row), by inverting the scorer's bilinear-in-likelihood interpolation cell by cell
(land corners renormalised out exactly as `score_impacts.lookup`). Committed node values were substituted where they exist
(`debris-drift-two-model-nodes-relwind.csv`, 367 nodes at 50 km; the architecture stand-in chunks 2-3, 151 GLORYS12 nodes, all bandwidths).

Verification: (1) rebuilt against committed values, median |d ln L| 5e-8, GlobCurrent 50 km max 8.4e-5 on 367 nodes, GLORYS12 all bandwidths
max 2.4e-5 on 151 nodes; (2) rescoring all 16.0 M impacts through the scorer's own reader (`surface_arrays` + `lookup`) reproduces every originally
scored value to max 1.7e-5 ln (float32 rounding), both models, all four bandwidths; 197 of 15.97 M GLORYS12 50 km impacts (two cells whose fit
failed) become 'not computed' and are never given a wrong value; (3) a synthetic held-out test (rebuild from 1 M impacts, score a fresh 1 M) gives
max error 2.9e-5 ln, with 0.33 % of fresh impacts outside rebuilt cells flagged not computed.
Columns: `ln_l`, `ln_l_h25`, `ln_l_h100`, `ln_l_h200` (NaN = unresolved or not constrained by any impact), `source_<bw>` (committed | rebuilt),
`support_<bw>` (largest likelihood share the node carries in any fitted cell). Split-half columns exist only where committed. Nodes absent from
`nodes.csv` read 'not computed' (state 0); nodes listed with NaN read 'unresolved' (state 3), inferred from impacts the original scorer flagged 2.
Script: the inversion is in the session that produced this note (architecture stand-in, frame 0082820d); method in `../drift-runj-2026-10-17/README.md`.
