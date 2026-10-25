# Pre-registration: absolute level check on known-energy explosions and the ARA San Juan event (raw IMS H10)

Written before any received level, TL, residual or matched-filter statistic on these raw records was computed.
Timestamp in prereg_timestamp.txt. Disclosure: the project already holds a digitised result for the San Juan
charge at H10N (level -14.4 dB FAIL, slope +2.8 dB/oct PARTIAL, shape PASS; stage 1b, KRAKEN and RAM TL on the
Vergoz-position path). That part is therefore NOT blind. Raw measurements, H10S, the FSST shots, the alternative
source model and the San Juan event are blind. Label: EXPLORATORY with a written-in-advance protocol.

## M. Measurement (all events, all elements with data)
M1 Response: full StationXML response removed (obspy remove_response, output in the response input unit, which must be Pa;
   pre-filter 0.5/1/110/120 Hz, water level none). Check: units string printed.
M2 Arrival search: 2-40 Hz zero-phase 4-pole Butterworth; 1-s moving RMS envelope; search window =
   [geodesic distance / 1.500 km/s - 60 s, geodesic distance / 1.460 km/s + 60 s] after origin. t_pk = envelope maximum.
   For the San Juan event the primary arrival is the largest envelope peak in that window (reflections arrive later).
M3 Signal window W = [t_pk - 30 s, t_pk + 30 s] (60 s, primary). Sensitivity: 20 s [t_pk-10, t_pk+10] and 120 s [t_pk-40, t_pk+80].
M4 Noise: 10 contiguous windows of the same length ending 60 s before the start of W. Noise band exposure = median of the 10;
   spread = 16-84 % of the 10.
M5 Band exposure: one-sided ESD from the FFT of the Tukey(0.1)-tapered window (taper energy loss corrected);
   E_b = integral of ESD over base-2 third-octave edges fc*2^(+-1/6). Signal exposure = E_b(W) - median noise E_b.
   Band SNR = E_b(W)/noise. Bands measured: 2.5-80 Hz nominal centres. Reported as Pa^2 s and as band-average ESD
   (dB re 1 uPa^2 s/Hz) = 10 log10(E_b/BW) + 120.
M6 Triad level = energy mean over elements with valid data; elements flagged when their band level departs from the triad
   median by > 6 dB in >= 3 bands (H10S1: known electronic noise, Nielsen 2021). Flagged elements are reported but excluded.
M7 Peak: instantaneous max |p| in W after 1-60 Hz band-pass (Vergoz Fig. 2 band) and after 4-40 Hz (F-35A convention);
   1-s RMS peak 4-40 Hz. dB re 1 uPa.
M8 Back-azimuth: plane-wave fit to element-pair delays from cross-correlation of the 4-40 Hz trace over [t_pk-10, t_pk+10];
   element positions from StationXML; least squares slowness; report back-azimuth and apparent speed.

## P. Prediction
P1 Paths: WGS84 geodesic, 0.5 km spacing, GEBCO_2026 3x3 median depth, WOA23 decade B5C2 (2015-2022) event month,
   monthly above 1500 m and seasonal below, TEOS-10, 25 km nodes (audit paths.py convention). Existing ocean-transport
   section reused for San Juan charge -> H10N and rebuilt with this builder as a cross-check.
P2 TL: module chain unchanged. K = KRAKEN adiabatic incoherent modes, profiles every 5 km, hard half-space (cp 1650 m/s,
   rho 1.9, 0.5 dB/lambda), Francois-Garrison, spherical correction, band centre. R = RAM (pyram, tl_recal_block9.ram_job:
   9 frequencies per third octave, dr 2 lambda, dz lambda/20, mean intensity over the last 500 m) plus F-G along the path
   plus spherical correction. Receiver depth = element-mean depth from StationXML.
P3 Source (declared, both reported, neither fitted):
   SA = Gaspin & Shuler (1971) construction re-implemented (audit gs_reconstruct.py, kappa 4, sin^2 negative phases) at the
        declared W and depth. SL(1 m) dB re 1 uPa^2 s/Hz = G&S band level (dB re 1 erg/cm^2/Hz at 100 yd) + 191.1 dB.
   SB = G&S Table 3 published third-octave levels scaled by explosion similitude from each reference column (1.8 lb at 60,
        300, 800 ft; 3 lb at 60, 500 ft): ESD(f; W, z) = ESD_ref(f s) + 20 log10(a s), a = (W/W_ref)^(1/3) (pressure at fixed
        range), s = (W/W_ref)^(1/3) ((z_ref+10.1 m)/(z+10.1 m))^(5/6) (time; G&S Z = depth + 33 ft). Primary: the reference
        column closest in reduced depth z/W^(1/3); all columns reported as the source spread.
   Both are far outside G&S's stated validity (charges up to a few lb, depth to ~1000 ft): declared extrapolation.
P4 Charges: San Juan charge 108 kg TNT (Vergoz) at 33 m (cepstrum), sensitivity 102 kg (Nielsen) and 38 m (planned);
   position Vergoz 45.666 S 59.240 W primary, Nielsen 45.6667 S 59.415 W sensitivity. FSST 2016 6,759 kg TNT and 2021
   18,000 kg TNT (Brown 2026 Table A.4 as digitised), positions and origin times USGS ComCat; charge depth NOT FOUND in a
   2016/2021 primary source: 61 m (200 ft, 2008 FSST notice, 73 FR 43129) used, sensitivity 30 and 100 m.

## S. Statistics and thresholds (criteria.md C1, as stage 1b)
r_b = measured - predicted band-average ESD (dB), bands 5-40 Hz with band SNR >= 3 dB.
LEVEL = median r_b (PASS <= 4, PARTIAL <= 7 dB, widened for the source term), SLOPE = OLS slope of r_b on log2 f
(PASS <= 1.5, PARTIAL <= 3 dB/oct), SHAPE = RMS of detrended r_b (PASS <= 3, PARTIAL <= 5 dB).
sigma_model reported per event/station/band and pooled: mean and SD of r_b by band across events; slope pooled.

## J. San Juan event matched filter (M1b, module prepare/weak_signal)
Statistic, template and thresholds exactly as the module's M1b; null distribution from the same element's record in
off-event windows on the same day (n >= 100 windows); p = (k+1)/(n+1), floor 1/(n+1); screen 0.3, mark 0.1, report 0.05.
Source energy estimate for the event: same chain, z_s 500 m and 900 m (Vergoz used 500 m; wreck ~920 m), source
spectrum as SA/SB charge-equivalent; reported as a TNT-equivalent through the charge ratio and as radiated energy.
Never fed back to any MH370 timing.
