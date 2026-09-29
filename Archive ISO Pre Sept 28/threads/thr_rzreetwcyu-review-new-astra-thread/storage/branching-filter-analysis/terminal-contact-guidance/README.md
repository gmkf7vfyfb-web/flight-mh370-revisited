# Joint fuel and contact-relevant control guidance

This tests a numerical proposal correction on the existing terminal model. It keeps each fitted guide centre's lift targets and ordered target-change times that precede the final contact when fuel is guided jointly. The earlier guide overwrote that mask and retained only the first lift setting. Bank and post-contact controls retain their original broad proposal support. The full physical prior remains supported by the20%uniform component and its density correction is unchanged.

The two runs use2048draws per each of six saved broad00:11cruise sources, seeds37096011/12, with the same guide bank,0.1box half width,8nearest centres, two separate terminal polars,15–19UTCfuel interval and seven final-contact choices as the preceding equal-size guide comparison. This is numerical sensitivity work, not a new physical hypothesis or a validated posterior.

`execute_comparison.py` is the fixed run/check/report queue. `progress.json` identifies every actual configuration, input, executable and completed output; the measured resource files record each worker's wall/CPU time and peakRSS. A startup failure before any sampling was caused by an absent external timing utility. The explicit corrected resume uses per-child os.wait4 resource accounting and preserves the original failure in progress.json.

The isolated source change is recorded in source-change.patch against the canonical source hash and exact baseline source snapshot identified in source-identities.json. No experimental code is installed in the product while this comparison is being assessed. The new direct numerical fixture has4guided coordinates with0.2width each: mixture density0.2+0.8×625=500.2inside,0.2outside a guided coordinate; changing a bank or post-contact coordinate preserves the former density. The fixture and all3existing terminal-control invariants pass.

Each individual simulation can be reproduced using the frozen executable and its recorded JSON:

```bash
/path/to/terminal-contact-guidance/mh370 continue-cruise-to-impact --config /path/to/terminal-contact-guidance/terminal-seed-37096011.json --output /path/to/new-terminal-output
```

Final-contact conditioning and an independent dense-Gaussian/Legendre-quadrature check follow. The comparison retains both independent seeds and both physical models; no fixedCDFgap threshold, pooling of model families, search-location claim or default promotion follows merely from completion.

## Assessment

Not integrated: this pair did not establish a generally better proposal. Both-BFO latitude-CDF disagreement improved for the lower-drag model but worsened for the higher-drag model; the higher-drag warm-up case remained severely concentrated. The isolated alternative was removed after the completed tests. Source difference and exact baseline archive identities are retained for reproducibility. No new default or pooled posterior follows from these outputs.
