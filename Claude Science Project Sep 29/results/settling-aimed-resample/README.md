# Settling: aimed resample from per-row weights (composer pass 1 request)

Ocean settling, 10 Oct 2026 (~23:45 UTC). This answers architecture's ~23:20 UTC request as the composer's stand-in. Settling's core-set
resample keeps only 368-865 effective impacts for 00:19 R600 BTO Only under the composed G and H. The fix is to draw the impacts that
settling settles from the composed per-row weights, not from end of flight's option posterior. `wf_aimed.py` does this.

**Input contract (to be written by the composer, one directory per product):**
- `manifest.json`: `product`, `label` (the panel title, standard 00:19 option name first), `option`, `constraint`, `run_root`, `strata`,
  `seeds`.
- `<stratum>/seed-<k>.f32`: little-endian f32, one value per row of `<run_root>/<stratum>/seed-<k>/impacts.npy`, in the same order.
  The value is the row's final mixture mass, that is the stratum weight × the pooled within-stratum weight. Any overall scale is accepted.
- `SHA256SUMS`, `READY`.

Proposed location: `mh370-exchange/composer/<run>/row-weights/<option>-<product>/`. It is about 205 MB per product on core (b).

**What settling does with it:**
1. A systematic resample of N impacts (default 40,000) over all rows of all strata and seeds. Each drawn outcome has weight 1/N.
2. One settling draw per outcome on the real ocean.
3. The seabed density, and the impact reference contours from every weighted row.
4. Published samples with the source sidecar (stratum, seed, impacts.npy row) and SHA256SUMS.

Rows with weight 0 are never drawn. NaN weights are counted in `nan_weight_rows`, never silently dropped. The Kish ESS of the row
weights is recorded. Below 1,000 the panel is stamped not estimable.

**Status.** The code is ready; there is no result yet (BLOCKED on the composer's per-row weights), because the composed per-row weights are not on the exchange. The composer's
`work/rust/<stratum>/weights` are deleted per stratum (`run_pass0.sh` line 22). A self-test on end of flight's own R600 BTO Only
posterior (one stratum, two seeds, 4,000 draws) ran end to end. It is SMOKE only, so it is not evidence and is not committed as a
figure.

**Exporter for the composer (G12).** `export_row_weights.py` is called once per stratum inside `run_pass0.sh`, after
`summarise_stratum.py` and before line 22 deletes `work/rust/<stratum>/weights`. It is then called once with `--finish`. It writes
exactly the contract above, using the composer's own `summarise_stratum.pooling`. Each stratum's pooled mass is normalised to 1 and
multiplied by W_Q(stratum), and the raw sum is kept in `pooled_raw_sum.json`. It passed a unit test on synthetic composer outputs
(stratum mass = W_Q exactly). It reads nothing the composer does not already read, and it changes no composer file.

**Cost.** Prep reads each seed file once (about 25 s per 2 seed files). Settling takes about 1 min per 40,000 draws at 2 threads, so the
heavy lock is not needed.

- Ocean Settling
