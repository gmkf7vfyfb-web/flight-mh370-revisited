# Hydroacoustic estimator: recommended method (proposal, 2 Nov 2026)

Status: proposal X18. On 3 Nov 2026 Pete approved its commit and its start (decisions P73, P74). Each compute run still needs his approval of its estimate (P39, P40).
Origin: session d1ea5f58 (2-3 Nov 2026), from Pete's four-point method of 2 Nov 2026 with four agent amendments.
Language: ASD-STE100 for work-specific text. Standard statistical terms are used as they are.

## Methodology points

1. Purpose. The hydroacoustic estimator compares recorded signals with predicted signals. It does not use the impact energy, attitude or position from the end-of-flight model. For each source location and source time, it gives the probability that each station detects a source of a given acoustic energy.
2. Source parameters. We describe the source with three parameters: the acoustic energy, the corner frequency of the source spectrum, and the source depth. The acoustic energy is the kinetic energy at impact multiplied by the coupling efficiency. Only this product sets the received level. Thus we do not sample kinetic energy and coupling efficiency separately.
3. Source spectrum. The spectrum is flat up to the corner frequency. Above the corner frequency, it decreases as the F-35A measurement shows (about frequency to the power -3.1). A decrease as frequency to the power -2 is a second case. We use three corner frequencies: 5 Hz (as the F-35A), 1 Hz and 0.2 Hz. A low corner frequency agrees with a long impact, for example a ditching.
4. Kinetic energy bounds. The upper bound is about 10 GJ. This is the kinetic energy of 174 t at the speed of sound at sea level. The steepest Boeing simulator dives give 9.0 to 9.5 GJ at the end of the record. Near this speed the dives are outside the simulator data, so we use this value as a bound only. The lower bound is about 0.4 GJ. This is 174 t at 70 m/s, a low-energy ditching.
5. Coupling efficiency. The coupling efficiency has a wide prior range from all published sources. We do not select one value. We report results against acoustic energy. Then we show the coupling efficiency that each result needs at the two kinetic energy bounds.
6. Source grid. First, we use five points on the 7th arc at 20, 25, 30, 35 and 40 S. Then we add points where the transmission loss changes quickly, for example near ridges. We also add points across the arc, to the limit of the glide distance. The source time has steps of 1 s across the impact-time window. This window starts at the 00:19 log-on. It ends at the latest impact time that the core and end-of-flight timing give.
7. Propagation path. For each source point and station, we make a section along the shortest path on the WGS84 ellipsoid. The section has the GEBCO 2026 sea-floor depth, the WOA23 March sound speed and the GlobSed sediment thickness.
8. Transmission loss. For each section, we calculate the transmission loss in each third-octave band from 5 to 40 Hz. We use a range-dependent parabolic-equation model (RAM). An adiabatic normal-mode model (KRAKEN) is a fast reference only. We also calculate the travel time and the time spread of the arrival.
9. Path class. We put each path in one of four classes: clear deep path; ridge near the sound-channel axis; long shallow section; blocked. The model error depends on the path class.
10. Propagation calibration. We calculate the same quantities for paths from known sources. These are the Blackman airgun shots of 2001, the SUS charges of 2003, the glass-sphere implosions, the ARA San Juan and the Ascension shots, and the F-35A impact at Wake Island. Earthquakes and the events that Royer located at many stations are also known sources.
11. Residual model. For each known-source path and band, we calculate the measured level minus the predicted level. We fit one model to these differences. It has a term for each path class, a slope with frequency, a term for each station and a random term.
12. Use of each calibration source. Sources with a known level calibrate the absolute level. Events recorded at two or more stations calibrate the level difference between stations, because the unknown source level cancels. Earthquakes and Royer's events calibrate travel time and bearing. A path class with no calibration source gets a wide error, and we state this.
13. Noise. For each station and band, we use the one noise model for 8 March 2014, with its uncertainty and its sources.
14. Detection probability. We add simulated arrivals to real noise records from the same season and of the same data form. We measure the detector output without a signal and with a signal, as a function of signal-to-noise ratio. The test includes the recording gaps of the IMOS loggers (307 s in each 15 min), their 8 Hz high-pass filter, and the time resolution of digitised traces.
15. Stations with published results only. For the OHASISBIO sites we hold published spectrograms and event picks, not recordings. For these sites we estimate the probability that the published analysis shows the signal. We state that this estimate is not calibrated on recordings.
16. Detectability maps. For each source point, station and source case, we calculate the acoustic energy that gives a detection probability of 50 %. We also show the coupling efficiency that this needs at the two kinetic energy bounds. A station that cannot detect any source in the prior range gives no information at that point. We report it and do not use it in the search.
17. Network search. For each source point, source time and source case, we predict the arrival time, the bearing (at arrays only) and the received level at each station, each with its error. At each station we calculate the ratio of two probabilities: the data with the predicted signal, and the data with noise and known sources only. We integrate this ratio over the errors in arrival time and level.
18. Combination of stations. Between stations we compare signal energy and envelope, not waveforms, because each path is different. We add the station log ratios to get one log Bayes factor. A station with data, a strong predicted signal and no signal gives evidence against that source. A station with no data gives no evidence. The acoustic energy is a free parameter. Thus the level differences between stations test the source position.
19. False-alarm rate. We run the same search on records with no MH370 signal: time-shifted records, other days in March, and other years. This gives the largest search result that occurs by chance across all trials. We report empirical p-values. We do not use a conservative threshold.
20. Known events. We compare each candidate with known events: earthquakes, ice, airgun surveys, ships and whales. We give the probability of each match. A match is a label, not a reason to delete a candidate.
21. Outputs. The estimator gives four outputs: (i) detectability maps for each station; (ii) the 95 % upper limit of acoustic energy for each source point, over the impact-time window; (iii) the list of candidates with p-values and known-event matches; (iv) the Bayes factor for each source point. The composer uses the Bayes factor only after the detection-probability test passes. Until then the estimator adds nothing to the posterior.
22. Value of information. Before the search on real data, we add synthetic detections at one, two and three stations. We measure how much each one changes the posterior. This shows how much effort each step deserves.
23. Link to end of flight. When the end-of-flight model is repaired, its impact samples become weights on the source grid. The propagation, detection and search results do not change.
24. Acoustic-gravity waves. Acoustic-gravity waves are a separate branch with their own model and errors. This method does not include them.

## First compute estimate (planning values; check before approval)
| Step | Compute | Where | Development |
|---|---|---|---|
| Value-of-information test on synthetic detections | under 10 min | outside the heavy lock, 2 threads | 3-4 h |
| Source bounds note (energy, corner, depth, coupling range) | none | - | 3-4 h |
| Sparse sections and transmission loss: 5 arc points x 14 receiver paths = 70 paths | KRAKEN about 20 CPU-min; RAM about 26-45 CPU-h (2-4 h at 12 threads) | heavy lock, 12 threads | 2-3 h |
| Residual model by path class (84 known-source paths already done; Royer multi-station events added) | fit: minutes; Royer paths with RAM: about 20-40 CPU-h if added | heavy lock | 6-10 h |
| Detection probability for each station and data form (extend the existing injection test) | 2-6 CPU-h | outside the heavy lock | 6-8 h |
| Detectability maps (sparse grid) | minutes | outside the heavy lock | 2 h |
| Network search and chance distribution on the data held (400-1,000 null runs) | 1-4 CPU-h | outside the heavy lock | 8-12 h |
| Denser grid, only where the maps show information | decided after the maps; the full arc grid with RAM was estimated at about 657 CPU-h | heavy lock | - |

Basis of the RAM estimate: the 27 Oct estimate of about 657 CPU-h for the whole-arc grid, about 0.37-0.64 CPU-h per path, depending on the path count of that grid (1,032 to 1,760 paths).
