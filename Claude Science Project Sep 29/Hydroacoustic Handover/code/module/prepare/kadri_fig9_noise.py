"""PRE-REGISTRATION (committed before any colour or amplitude is read from the figure): audit F10 season check and
Pete's priority 5 (11 Oct 2026, 11:25 -0600) - IMS noise on 8 March 2014 from a published figure.

SOURCE. Kadri (2024) Sci. Rep. 14:10102, Fig. 9 (PMC11065988 web figure 41598_2024_60529_Fig9_HTML.jpg, as held in
  the module session lit/k24fig/): spectrograms (dB re 1 uPa^2/Hz, colour bars about 65-110 dB) and pressure time
  series for H01W (a-c: 00:27, 00:37, 00:47 UTC + 10 min) and H08S (d-e: 01:00, 01:10 UTC + 10 min), 8 March 2014.
  Kadri's processing (p. 11): traces high-passed at 5 Hz; spectrogram parameters as printed in the paper.
QUANTITY. Per third-octave band 5-40 Hz (H01W) and 5-40 Hz (H08S, its panel shows 0-60 Hz): the LINEAR mean PSD over
  the panel's time span, from the spectrogram colours mapped through the panel's own colour bar (nearest colour in
  RGB over the bar's pixel column; the bar's end labels and ticks give the dB scale). JPEG: colours further than 40
  RGB units from every bar colour are dropped (counted). H01W uses panel (b) "No signal observed" (primary) and the
  parts of (a) and (c) outside Kadri's boxes (sensitivity). H08S uses (d) and (e), whole span (they are dominated by
  periodic impulses: the impulse duty fraction is reported from the time series, column extremes > 3 x the panel's
  median column extreme). Labelled DIGITISED; reading uncertainty declared +/- 2 dB (colour-bar quantisation and JPEG).
COMPARISON. Delta_b = PSD_Kadri,b - module noise (Blackman App. B route R median, results-data/blackman_noise/
  blackman_noise_summary.json, May-June 2003). Rule fixed now: median |Delta| <= 3 dB -> Blackman noise retained
  (the amendment-4 +/-3 dB already carries it); 3 < |Delta| <= 6 -> Delta added as a labelled sensitivity;
  > 6 -> the March 2014 reading replaces Blackman for that station (its +/- 2 dB declared), with a module amendment.
  The H08S impulses are reported as a separate finding (a detection-probability matter, not a PSD offset).
LABELS: predictive; not a likelihood; DIGITISED from a published raster.
"""
