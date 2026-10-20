# BFO choices and the missing refined checkpoint

These findings come from recovered files, not recollection. Detailed evidence and source references are in `../output/davey_audit/REPRODUCIBILITY_NOTES.md`; its opening run-status statement predates the authorized reconstruction and is now historical.

## What changed in the later project

1. **Refined-v3 trajectory model:** fast Gaussian noise 1.5 Hz, with a slow correlated bias whose stationary SD is √(3.4²−1.5²) = 3.051 Hz and primary correlation time one hour. The retained sensitivity studies used 2 Hz fast noise and half-/two-hour slow-bias timescales. The reported latitude medians changed from 36.312°S to 37.306°S, 37.024°S and 36.785°S respectively. The model excluded 18:25 BFO, marginalized a received-power gain-survival/precompensation term, and used zero nominal wind plus stochastic wind error because the original ACCESS fields were unavailable. These are historical reported results, not newly reproduced runs.
2. **Integrated stage 1:** the endpoint summary reconstruction was augmented with altitude, descent and control-family variables. Its added vertical-rate likelihood was `log L = −0.5 × (0.009 × vertical_rate_fpm / sigma_Hz)²`. The original effective scale was 12 Hz, with 8/18 Hz sensitivities. This was not an estimate of fast receiver noise and did not refilter the entire trajectory.
3. **Later 0.995 Hz choice:** the recovered code estimated short-timescale noise from 78 successive BFO differences within the accident-flight call clusters, centered each cluster's differences, and used a denominator `2 × (78−2)`. It replaced the scale in that added vertical-rate likelihood with approximately 0.995 Hz. It did **not** rerun the complete radar-to-00:11 filter using that noise level or recover latent trajectory/bias correlations. The quoted 0.859–1.183 Hz interval uses an idealized Gaussian calculation; overlapping differences and integer quantization limit its interpretation.
4. **Later v11/v12 discussion:** the archive describes a fast-noise / slow-common-bias / persistent-channel-offset decomposition and 0.5/1/2-hour sensitivities, then a return to Davey's constant bias and 7 Hz noise for the baseline. A 1.475 Hz withheld-MH371 within-burst estimate is a different dataset and calculation from the 0.995 Hz accident-call result. Missing original scripts mean the narrative alone cannot establish which proposed robust alternatives were actually completed.

The present Davey reconstruction uses none of those tighter or correlated-noise refinements: it has a constant bias with 25 Hz prior SD and 7 Hz measurement noise, analytically updated along each trajectory.

## What was reconstructed when the checkpoint was missing

The original refined checkpoint would have held the weighted simulated trajectories and their joint states: position, speed, heading, wind, manoeuvre history, calibration/bias variables and their dependence on one another. It was not recovered.

The retained stage-1 code instead generates fresh latitude samples from four fitted Gaussian components:

| Mean latitude | SD | Probability |
|---|---:|---:|
| −37.4700° | 0.17552° | 0.074700 |
| −36.4584° | 0.66377° | 0.724363 |
| −34.2200° | 0.50504° | 0.137117 |
| −33.1100° | 1.01111° | 0.063819 |

Longitude is drawn around a quadratic latitude–longitude ridge with 0.085° scatter. Heading is newly drawn around 186.083° with 4° SD; Mach is drawn from a clipped normal centered on 0.78792 with SD 0.018. Further altitude, vertical-rate and control-family assumptions are then applied.

This recreates selected reported endpoint summaries, **not the original joint posterior**. Two ensembles can have the same latitude histogram but different speed/bias/trajectory correlations, and therefore respond differently to new evidence. More draws from the fitted mixture cannot restore that missing information. It cannot support removing the old received-power likelihood by simple reweighting or swapping in Davey's BFO assumptions exactly. The northern components of this reconstructed proposal are present by construction.

The recovered 120,000-row companion CSV contains 60,000 no-drift and 60,000 drift-weighted later samples. Only its no-drift subset is used as the labelled 00:11 comparator. Having that CSV does not recover the missing original refined filter checkpoint.

## Recovery provenance

The GitHub archive `gmkf7vfyfb-web/flight-mh370-revisited` ends at commit `e0115e817975d073bdf2b09a428fbce62aeda35c` dated August 14, before the later v12 discussion. The companion dataset revision is `084ee83a309b9d7010afeba041d7b160aa294c76`. Recovery manifests preserve file hashes. Their contents support reconstruction, but do not contain the original v12 executable.

A historical `sandbox:/mnt/data/...` link and a conversation saying a file was created do not make its bytes available in this desktop workspace. We cannot establish the particular deletion event or retention mechanism from the surviving evidence. What is established is the bounded recovery result: the original files were not available in the conversation attachments, searched local archives or recovered repository. This reconstruction therefore saves its own source, inputs, RNG state and checkpoints together.
