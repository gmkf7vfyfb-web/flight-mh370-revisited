# Pre-registration amendment 1 (clean-sheet detector T1)

Date: 3 Nov 2026. Saved BEFORE any held-out outcome is scored. It changes the pre-registration of the same date (artifact c74a811f, version 56ba5691).
What was known when this was written: the noise thresholds and the first injection run (calibration data only). No held-out outcome has been compared with a prediction.

## A1. Injection levels extended
The one-per-day thresholds are 17-27 dB (30 s window). The first grid stopped at E/N0 = 36 dB (SNR about 21 dB for W = 30 s), so the P_D curves at Diego Garcia South and Wake were not measured. The injection run is repeated with E/N0 from -2 to 56 dB in 0.5 dB steps, same seeds, same blocks. The second run replaces the first. The first run is kept only as a check of the overlap range.

## A2. P_D model with a chance-alarm floor
The measured curves have a floor: noise alone sometimes alarms inside the search span. The model is
P_D = p0 + (1 - p0) Phi((SNR - snr50)/sigma).
p0 is measured directly from the noise-only maxima in the same spans. snr50 and sigma are fitted by maximum likelihood with p0 fixed. pd_curves.json gives snr50_db and sigma_db of the Phi part (the shared schema) and p0 as an extra key, pd_floor.
For held-out predictions: P_pred = p0 + (1 - p0) Phi((SNR_pred + bias - snr50)/sqrt(sigma^2 + s_prop^2 + s_src^2 + s_noise^2)).

## A3. IMOS loggers 3315 and 3275
These two loggers have no background records; only 5-6 recorded hours outside the exclusion span. That is too short for a one-per-day tail (expected alarms below 1). Primary: proxy thresholds and curves from the logger at the same site type (3315 uses 3376, Perth Canyon; 3275 uses 3274, Portland). Sensitivity: their own short null, labelled "lower bound on the threshold".

## A4. Airgun source band
The Tolstoy far-field grid has no 5 Hz band. The airgun received energy uses the 6.3-40 Hz third-octave bands (9 bands). The missing 5 Hz band can only add energy, so this choice can only lower the predicted SNR.

## A5. Noise level definition
noise_level_db in pd_curves.json is the level of the median 30 s window energy divided by 30 s (dB re 1 uPa^2). It is the quantity that the SNR definition uses. In 2015-2019 March data it is 0.6 dB (Cape Leeuwin) and 2.7 dB (Diego Garcia South) below the mean power.
