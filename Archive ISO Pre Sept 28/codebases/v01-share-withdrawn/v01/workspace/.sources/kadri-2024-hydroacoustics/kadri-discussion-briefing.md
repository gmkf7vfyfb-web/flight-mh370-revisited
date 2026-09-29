# Preliminary hydroacoustic work for discussion with Dr Kadri

This work asks two separate questions: what pressure scale might different Boeing 777 water-impact conditions couple into the ocean, and whether any feature visible in Kadri's published H01W/H08S plots can presently be associated with such an impact.

The simplified impact-to-SOFAR sensitivity experiment uses one million deterministic draws for each of four explicitly separate vertical-contact-speed families and two source-to-SOFAR coupling priors. It uses 174,369 kg—the actual 9M-MRO zero-fuel weight on the final loadsheet—as a fuel-exhaustion impact-mass surrogate, not a measured mass at 00:19 UTC. The F-35 example only centres one coupling prior at order 10^-4; the log-uniform control spans 10^-8 to 10^-2. Under the centred prior, median peak-pressure proxies range from 0.025 to 0.786 Pa at H01W and 0.014 to 0.439 Pa at H08S. These are not detection probabilities and do not identify a plotted transient.

The present candidate assessment is deliberately conservative. Kadri's Figure 9 rectangle 1/Table 1 caption identify an approximately 00:52 UTC, 57-degree signal; rectangle 2/Table 1 identify the preferred 00:54:30 UTC, 306.18-degree candidate. The p. 9 prose appears to conflate their time and bearing. Neither the 00:49:58 nor 00:53:31 Table 1 time exceeds our publication-panel q99 screen within ±2, ±5 or ±10 seconds. The 01:03:13.15 H08S screening time is elevated in the plotted trace but lies within a 9.9279-second periodic airgun train. Leave-one-shot-out subtraction leaves its residual between the 80.5th and 99.2nd percentile depending on defensible method choice; the control-selected result is 94.1st percentile.

At ±100 and ±150 ms, masks centred on the blind periodic prediction leave the screened time, whereas masks centred on observed shot peaks remove it. Both tests operate below the publication line's indicative ±0.51-second timing thickness, so the plotted waveform cannot adjudicate between them.

We have now run two complete acquisition controls across 5,289 source cells and 41 propagation offsets (−5 to +5 s). First, the control-selected rank-8 subtraction gives maximum energy correlation r = 0.109, below the 250-scan IAAFT null q95 of 0.160 (scan-adjusted p = 0.964); every leading match still lands on residual H08S periodic structure. Secondly, without subtracting the train, panels d and e each provide 59 pulse cycles. Only one panel-d cycle and no panel-e cycle exceeds its Tukey upper fence. A marked-pulse/H01W joint search can align upper-tail cycles to source cells, but its complete-scan permutation p-value is 0.948 and its H01W time-slide p-value is 1.000. Thus the visually interesting pairings are expected somewhere in this broad search under the measured interference null.

Current conclusion: the integrated estimator should use hydroacoustics as a predictive-only spoke at present. It can forecast arrival windows and broad signal-scale intervals for each physical impact particle, but the publication traces receive zero evidential weight. A future conditional event-association likelihood would require raw H01W and H08S triad channels, station response and timing metadata, Kadri's complete candidate catalogue and selection rule, exact processing parameters, contemporaneous off-source noise, and airgun timing or direction information. The full position/time/template search must be repeated on null windows and injected signals so that false alarms and selection are corrected together.

Questions for discussion are: whether the raw multi-channel arrays and adjacent background can be accessed; whether the 00:49:58 and 00:53:31 Table 1 entries have retained waveforms, bearings and detection statistics; how the Figure 9 candidates were selected; whether the search can cover arrivals corresponding to impacts through approximately 00:50 UTC; and whether Dr Kadri could apply coherent triplet processing or supply path Green functions for a pre-registered impact-template bank.

## Figures to share

1. [Conditional impact pressure by station](outputs/impact-pressure-by-station.png)
2. [Consolidated bearings and timing controls](outputs/candidate-bearing-and-timing-overview.png)
3. [Airgun-cycle energy population](outputs/airgun-cycle-energy-distribution.png)
4. [Filtered full-grid acquisition](outputs/filtered-acquisition-response-overview.png)
5. [Pulse-conditioned full-grid acquisition](outputs/pulse-conditioned-acquisition-overview.png)
6. [Sub-second periodic-mask comparison](outputs/subsecond-periodic-mask-comparison.png)
7. [Leave-one-shot-out controls](outputs/leave-one-shot-out-controls.png)
8. [Filter/mask trade-offs](outputs/airgun-filter-mask-tradeoffs.png)
9. [Impact-family transfer density](outputs/impact-family-transfer-density.png)
