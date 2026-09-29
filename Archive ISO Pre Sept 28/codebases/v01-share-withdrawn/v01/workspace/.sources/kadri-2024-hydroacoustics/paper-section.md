# Draft paper section — hydroacoustic evidence

Hydrophones are underwater pressure sensors. Arrays maintained for nuclear-test monitoring record low-frequency sound that can be trapped near the Sound Fixing and Ranging (SOFAR) channel and transported over ocean-basin distances. A three-element station can estimate bearing from inter-sensor arrival-time differences, while acoustic–gravity-wave dispersion may constrain travel time or range. A bearing from one station is nevertheless only a line of position. The ATSB's commissioned review found an initially interesting event to be probably geological and concluded that the available hydroacoustic analysis added no useful search information \citep{ATSB2017}. Kadri et al. subsequently developed an acoustic–gravity-wave inverse approach \citep{KadriEtAl2017}. Kadri's Figure 9 rectangle 1 and Table 1 caption identify an approximately 00:52 UTC, $57^\circ$ signal; rectangle 2 and Table 1 identify the preferred 00:54:30 UTC, $306.18^\circ$ candidate. The p. 9 prose appears to combine the second signal's bearing with the first signal's approximate time. No identifiable counterpart was reported at H08S, where 2--4 Pa airgun interference was present \citep{Kadri2024}.

We extracted the plotted pressure paths from Kadri's Figure 9 PDF as calibrated vectors and retained their provenance and hashes. These are representations of signals that had already passed the study's high-pass and 2--40 Hz filters, not raw CTBTO channels. They therefore cannot reproduce beamforming, bearing, coherence or calibrated detection performance. We screened an H01W feature at 00:47:01.7 UTC, but it lies only 1.7 s inside a separately drawn panel and is treated as edge-affected. At H08S, the screened 01:03:13.15 UTC time falls within a periodic train. A target-excluded phase fit to 59 complete cycles gives a period of 9.9279 s: the screened time is 174 ms after its periodic prediction and 50 ms after the observed envelope peak.

We modelled impact scale independently. One million deterministic draws per family and coupling prior used 174,369 kg—the actual 9M-MRO zero-fuel weight on the final loadsheet—as a fuel-exhaustion impact-mass surrogate, not a measured mass at 00:19 UTC. The families covered controlled ditching, the measured Flight 1549 contact rate, a log-uniform partially arrested bridge and a triangular density over Holland's conditional high-descent-rate bounds \citep{NTSB2010,Holland2018}. The F-35 example affects only one coupling prior, centred at $\eta=10^{-4}$ with one-decade log standard deviation and truncated to $10^{-8}$--$10^{-2}$; a log-uniform prior over the same bounds is the control. For aircraft mass $m$, normal impact speed $v_z$, effective source-to-SOFAR coupling $\eta$, TNT specific energy $q_{\rm TNT}$ and range $R$,

\[
E_n=\tfrac12 m v_z^2,\qquad
W_{\rm eff}=\frac{\eta E_n}{q_{\rm TNT}},\qquad
P(R)=52.4\times10^6
\left(\frac{R}{W_{\rm eff}^{1/3}}\right)^{-1.13}\ {\rm Pa}.
\]

The last expression is a simplified explosion-equivalent energy-to-pressure scaling law, not an aircraft-impact hydrodynamic solution \citep{BrownEtAl2026}. It omits horizontal motion, attitude, water-entry duration and breakup, path-specific bathymetry, propagation waveforms and station response. Under the F-35-centred coupling sensitivity prior, median pressure proxies span 0.025--0.786 Pa at H01W and 0.014--0.439 Pa at H08S; the unarrested family's 5--95% intervals are 0.189--2.883 Pa and 0.106--1.610 Pa respectively. These are conditional amplitude scales, not detection probabilities.

For H08S we compared adaptive-template and low-rank subtraction using leave-one-shot-and-neighbours-out controls. The method selected without reference to the target reduces its empirical rank from the 97.5th to the 94.1st percentile, while defensible settings span the 80.5th--99.2nd percentiles. Observed-centred masks of $\pm100$ and $\pm150$ ms discard 1.93% and 2.99% of samples and remove 18.8% and 28.6% of phase-folded excess energy, but both mask the screened time. Blind masks centred on the target-excluded prediction leave it unmasked at both widths. This difference is not resolvable from the plotted trace: both widths are below its indicative $\pm0.51$ s line-thickness timing uncertainty.

We then searched 5,289 seventh-arc/±100 NM source cells and 41 propagation offsets. With the control-selected rank-8 subtraction the maximum standardised-energy correlation was only $r=0.109$, below the complete-scan IAAFT null q95 of 0.160 ($p=0.964$); all ten leaders remained on residual periodic H08S structure. In a complementary raw-pulse test, panels d and e each supplied 59 fitted cycles. Only one panel-d cycle and no panel-e cycle exceeded its within-panel Tukey upper fence. Pairing pulse-tail rank with H01W energy produced a maximum Fisher score of 18.121, but complete marked-pulse permutation and H01W time-slide controls gave $p=0.948$ and $p=1.000$. Source cells can therefore produce visually attractive alignments, but none is rare under these publication-trace nulls.

Hydroacoustics therefore enters the baseline only as a forward prediction. For impact particle $x$, model family $m$ and station $j$,

\[
\mu_j(f\mid x,m,\theta,\phi)=
H_{j,m}(f\mid x,\theta)S_m(f\mid x,\phi)
e^{-2\pi i f\tau_{j,m}(x,\theta)},
\]

where $S_m$ is the impact source, $H_{j,m}$ the path/array response and $\tau_{j,m}$ the propagation delay. The current spoke reports arrival and signal-scale intervals but accepts no observed trace. If raw triad channels, processing metadata, contemporaneous noise and a pre-declared detector become available, a selected association may instead be represented by the injection-calibrated Bayes factor

\[
B_{\rm hyd}(x)=\frac{p(T_{\rm obs}\mid x,H_1)}{p(T_{\rm obs}\mid H_0)},
\]

with the complete position, time, propagation and template search repeated under both hypotheses. Until then, neither a candidate association nor non-detection receives a likelihood \citep{Farrell1997}.

## Recommended figures

1. `outputs/impact-pressure-by-station.pdf` — primary impact-scale result.
2. `outputs/candidate-bearing-and-timing-overview.pdf` — source-timing resolution, bearings, two-station timing controls, seventh arc and integrated PDF.
3. `outputs/subsecond-periodic-mask-comparison.pdf` — $\pm100/\pm150$ ms result.
4. `outputs/leave-one-shot-out-controls.pdf` — empirical held-out control ranks.
5. `outputs/airgun-filter-mask-tradeoffs.pdf` — filter and information-loss sensitivity.

## Citation identities

- `ATSB2017`: Australian Transport Safety Bureau, *The Operational Search for MH370*, AE-2014-054, pp. 114--116.
- `KadriEtAl2017`: Kadri et al., “Rewinding the waves: tracking underwater signals to their source”, *Scientific Reports* 7, 13949.
- `Kadri2024`: Kadri, “Underwater acoustic analysis reveals unique pressure signals associated with aircraft crashes in the sea: revisiting MH370”, *Scientific Reports* 14, 10102.
- `NTSB2010`: National Transportation Safety Board, *Loss of Thrust in Both Engines After Encountering a Flock of Birds and Subsequent Ditching on the Hudson River*, AAR-10/03.
- `Holland2018`: Holland, *The Use of BFO to Determine the Descent Rate of MH370 at the 7th Arc*, version 3.
- `BrownEtAl2026`: Brown et al., “A Search for Hydroacoustic Signals from Bolides”, arXiv:2604.12723.
- `Farrell1997`: Farrell, *HydroCAM User's Guide*, Lawrence Livermore National Laboratory.
