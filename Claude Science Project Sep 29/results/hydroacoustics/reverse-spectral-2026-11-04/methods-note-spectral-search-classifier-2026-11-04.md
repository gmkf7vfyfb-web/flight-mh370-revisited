# Methods note: spectral-template search (S10) and source classifier

4 November 2026. This note supports Amendment 2 to the reverse-sensing methods specification. All references were checked against CrossRef (or DataCite for the AADC dataset) on 4 November 2026. Propagation is used for travel time only.

## 1. What the search does

S10 looks for a short broadband sound whose spectrum falls with frequency, at any level, in the raw IMOS logger records. It is a matched filter in the time-frequency plane. The power spectrogram is divided by the record's own noise spectrum. The result is projected onto a family of templates, each one a spectral shape times a time shape. The family covers a loose impact-like class (Pete's steer, 4 November 2026): slope from flat to -15 dB per octave, corner from 0.5 to 20 Hz, band cut-offs, multipath ripple, a fast onset and a time spread from under 1 s to about 60 s. The one measured aircraft-impact spectrum (Metz, Obana and Fukao 2022) is a labelled member of the family, not its centre.

## 2. Why this statistic

1. **Matched filter.** For a known shape in Gaussian noise, the projection onto the whitened template is the optimum detector. With the level free, the maximum over the level gives the positive projection divided by the template norm (a generalised likelihood ratio). The maximum over a template bank is the standard way to cover unknown parameters. The look-elsewhere effect of that maximum is handled by the null (section 4), not by a formula.
2. **Shape test.** A matched filter also responds to any energy that projects onto the template, for example a strong 20 Hz call. The chi-square test of Allen (2005) splits the template into sub-bands of equal expected power and checks that each sub-band holds its share of the signal. The test is adapted here to an incoherent power spectrogram. A noise-like signal raises the variance of each cell in proportion to its own power, and the variance term includes that effect (Amendment 2, A2.4). Without it, a strong signal of the right shape would fail the test.
3. **Re-weighted SNR.** The chi-square is combined with the SNR by the re-weighting of Babak et al. (2013), which is used in gravitational-wave searches. A good fit leaves the SNR unchanged. A poor fit lowers it smoothly.

## 3. Why these template ranges

1. **Source.** Metz et al. (2022) measured an F-35A impact at H11: flat to about 5 Hz, then f^-2.65 to f^-3.5. A 777-200ER is about ten times heavier. A longer impact moves the corner down, and a break-up can change the slope. So the family takes slopes 0-5 and corners 0.5-20 Hz.
2. **Path.** Sea-water absorption at 10-100 Hz is small (Ainslie and McColm 1998). Over 1,400-5,100 km it steepens the slope by only 0.2-0.6 in the exponent. Bottom interaction, slope conversion and mode stripping can change the slope and band more, but no propagation model is used here. The slope range above holds these effects.
3. **Observed long-range arrivals.** Off-window arrivals in the logger data (Royer 2016 events at Portland and Perth Canyon) last 6-14 s and slope -4 to -8 dB per octave over 8-100 Hz. Long-range sound arrivals of earthquakes are emergent and spread over seconds to tens of seconds (de Groot-Hedlin and Orcutt 1999; Okal 2001). The time family (rise 0.25-3 s, decay 0.5-30 s) covers this spread with a fast onset, as the steer requires.
4. **Broadband constraint.** The high cut-off is at least twice the low cut-off, so no template is narrower than one octave. The ripple depth is limited (r <= 0.6), so a template cannot become a harmonic series.

## 4. Nulls and p-values

The null is empirical and has the same maximisation as the data.
- Local p: against all frames of 280 background-day records (1-15 March 2014, same clock hours) or of about 95 same-day records outside the arrival windows.
- Station-global p: against 5,000 pseudo-windows with the same pieces as the real window.
- Method-global p: Šidák over five loggers.
Natural transients are kept in the null, which makes it conservative. The null is heavy-tailed: airgun trains, whale song and local sounds give large R values on background days.

## 5. Classifier

1. **Model.** A regularised multinomial logistic regression on 16 explainable features: spectral slope, centroid, bandwidth, flatness, tonality, sweep rate, harmonic or ripple structure, low-band fraction, duration, rise time, decay rate, repeat strength and interval, envelope kurtosis, record level and persistent lines. A second model uses only the six time-shape features, for the envelope-only Kadri traces.
2. **Open set.** A Gaussian class model with a shrunk shared covariance (Ledoit and Wolf 2004) rejects windows far from every class.
3. **Validation.** Leave-one-group-out cross-validation. The Brier score (Brier 1950) and the expected calibration error are used. Logistic regression usually gives well-calibrated probabilities (Niculescu-Mizil and Caruana 2005).
4. **Labels.** Labels come from the data held, with stated rules:
   - Catalogue timing plus signal criteria for earthquake arrivals (USGS catalogue, 28 February-16 March 2014). The class is provisional.
   - Tonal 14-32 Hz units for whale calls. The rule follows the published call bands of Antarctic and pygmy blue whales (Gavrilov, McCauley and Gedamke 2012; Gavrilov et al. 2011) and fin whales (Watkins et al. 1987).
   - Regular impulse trains for airgun shots (Caldwell and Dragoset 2000; Nieukirk et al. 2004).
   - Record level plus persistent lines for ships.
   - Synthetic injections of the loose family into real noise for the impact-like class.
5. **Use.** Class scores never remove a candidate on their own (asymmetry rule, A2.7.5).

## 6. What this method can and cannot show

- It can show a broadband transient with a falling spectrum at a logger, and give its onset, template parameters and class probabilities.
- It cannot separate an impact from a natural broadband long-range arrival by spectrum alone. In these data, catalogued Royer arrivals score impact-like probabilities up to 0.75. Catalogue timing must carry that separation.
- At station-global p <= 0.05, it detects 50 % of injected impact-like signals only above about +8 dB (10 s SNR) at Portland 3275. The other loggers do not reach 50 % by +12 dB. At local p <= 0.05, it detects 50 % at about -3 to 0 dB at Perth Canyon and Portland. Scott Reef is effectively blind, because local sounds set its threshold.

## References

- Ainslie, M.A., McColm, J.G. (1998). A simplified formula for viscous and chemical absorption in sea water. J. Acoust. Soc. Am. 103, 1671-1672. doi:10.1121/1.421258
- Allen, B. (2005). A chi-squared time-frequency discriminator for gravitational wave detection. Phys. Rev. D 71, 062001. doi:10.1103/PhysRevD.71.062001
- Babak, S., et al. (2013). Searching for gravitational waves from binary coalescence. Phys. Rev. D 87, 024033. doi:10.1103/PhysRevD.87.024033
- Brier, G.W. (1950). Verification of forecasts expressed in terms of probability. Mon. Weather Rev. 78, 1-3. doi:10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2
- Caldwell, J., Dragoset, W. (2000). A brief overview of seismic air-gun arrays. The Leading Edge 19, 898-902. doi:10.1190/1.1438744
- de Groot-Hedlin, C.D., Orcutt, J.A. (1999). Synthesis of earthquake-generated T-waves. Geophys. Res. Lett. 26, 1227-1230. doi:10.1029/1999GL900205
- Gavrilov, A.N., McCauley, R.D., Salgado-Kent, C., Tripovich, J., Burton, C. (2011). Vocal characteristics of pygmy blue whales and their change over time. J. Acoust. Soc. Am. 130, 3651-3660. doi:10.1121/1.3651817
- Gavrilov, A.N., McCauley, R.D., Gedamke, J. (2012). Steady inter and intra-annual decrease in the vocalization frequency of Antarctic blue whales. J. Acoust. Soc. Am. 131, 4476-4480. doi:10.1121/1.4707425
- Kadri, U. (2024). Underwater acoustic analysis reveals unique pressure signals associated with aircraft crashes in the sea. Sci. Rep. 14, 10102. doi:10.1038/s41598-024-60529-1
- Ledoit, O., Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. J. Multivar. Anal. 88, 365-411. doi:10.1016/S0047-259X(03)00096-4
- Metz, D., Obana, K., Fukao, Y. (2022). Remote hydroacoustic detection of an airplane crash. Pure Appl. Geophys. 180, 1343-1351. doi:10.1007/s00024-022-03117-6
- Miller, B.S., et al. (2021). An open access dataset for developing automated detectors of Antarctic baleen whale sounds and performance evaluation of two commonly used detectors. Sci. Rep. 11, 806. doi:10.1038/s41598-020-78995-8 (dataset: Australian Antarctic Data Centre, doi:10.26179/5e6056035c01b; not used, see deviations log item 9)
- Niculescu-Mizil, A., Caruana, R. (2005). Predicting good probabilities with supervised learning. Proc. 22nd Int. Conf. Machine Learning, 625-632. doi:10.1145/1102351.1102430
- Nieukirk, S.L., Stafford, K.M., Mellinger, D.K., Dziak, R.P., Fox, C.G. (2004). Low-frequency whale and seismic airgun sounds recorded in the mid-Atlantic Ocean. J. Acoust. Soc. Am. 115, 1832-1843. doi:10.1121/1.1675816
- Okal, E.A. (2001). T-phase stations for the International Monitoring System of the Comprehensive Nuclear-Test Ban Treaty: a global perspective. Seismol. Res. Lett. 72, 186-196. doi:10.1785/gssrl.72.2.186
- Watkins, W.A., Tyack, P., Moore, K.E., Bird, J.E. (1987). The 20-Hz signals of finback whales (Balaenoptera physalus). J. Acoust. Soc. Am. 82, 1901-1912. doi:10.1121/1.395685
- Data: USGS earthquake catalogue (FDSN event service), M >= 4, 28 Feb-16 Mar 2014, 75 S-20 N, 15-180 E, downloaded 4 Nov 2026 (215 events).
