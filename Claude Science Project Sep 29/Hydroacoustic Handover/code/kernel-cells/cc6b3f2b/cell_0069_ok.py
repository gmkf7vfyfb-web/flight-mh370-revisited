
output = {
 "block": "8 — weak-signal method trials (brief Refresh v2 §7)",
 "status": "done",
 "summary": ("Pre-registered (78c7e88) and ran ten detectors on three test sets. (a) Synthetic impact pulses (one-pole source x KRAKEN coherent broadband channel, "
             "1,800-3,000 km) injected into 14 days of real IMOS background: dispersion-aware matched filters reach P_D = 0.5 at SNR ~7 dB (alpha 0.01 per 60 s window) "
             "at Perth Canyon 3376 against 13-16 dB for STA/LTA and 27-28 dB for band energy; at alpha 0.001 only the matched filters reach 0.5 (envelope 16-19 dB). "
             "Model-matched best case (pulses share the template model). Spectral kurtosis = STA/LTA; cepstral, synchrosqueezing, Bayesian change-point and stochastic "
             "resonance failed and are kept as negative results. (b) Digitised Kadri Fig. 9 panels: only the envelope matched filter reaches p = 0.05 inside an author's "
             "box (text time 00:52:03, label mark); caption time 00:54:30 best p = 0.11; the four poster panel-(a) boxes p >= 0.08; all carried as screen-level rows; "
             "H08S kurtosis rows are airgun null-mismatch artefacts. (c) H08S shot suppression: template subtraction -5.8/-4.7 dB residual energy, -7.6/-5.3 dB with "
             "cadence gating; chance coincidence cut 3-5x; injected arrival 4 dB below the median shot peak still recovered. No detection claimed; PREDICTIVE, NOT CALIBRATED; C1, C2."),
 "commits": ["78c7e88 (hypothesis/hydroacoustics) pre-registration", "c2b4548 (hypothesis/hydroacoustics) code, digitised Kadri data copy, result tables",
             "622dc6f (claude-science-sep29) results note + 3 charts (PNG+PDF) + coordination/architecture.md entry"],
 "results_notes": ["Claude Science Project Sep 29/results/hydroacoustics-weak-signal-methods.md"],
 "exchange_paths": ["/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/"],
 "key_numbers": ("3376, alpha 0.01, SNR_50 (dB): MF waveform 6.5/7.2/7.0 and MF envelope 6.9/7.8/8.0 (tau 0.1/1/10 s) vs STA/LTA 13.4/15.3/15.7, band energy 28.3/27.5/28.0, "
                 "spectral kurtosis 12.8/14.7/15.0; alpha 0.001: MF envelope 16.4/18.9/18.6, MF waveform n/r, 24.4, 25.2; baselines not reached by 30 dB. 3274: MF envelope 2.3 dB vs STA/LTA 11.2. "
                 "3250: only MFs reach 0.5 (24-26 dB). Null: 5,376 windows (3376), 1,344 (3274, 3250). Kadri boxes: text time MF-envelope p 0.052; caption time best p 0.11; panel (a) boxes p >= 0.08. "
                 "H08S: 64/52 shots at 9.95/10.00 s; residual -5.8/-4.7 dB (c1), -7.6/-5.3 dB (c1+c2); 36 surviving z>=3 peaks, 9 in the Kadri lag windows; recovery at -4 dB 0.88/0.50 vs chance 0.12/0.00."),
 "gaps": ["G-W1: no non-model-matched ground-truth test (San Juan / F-35A / Blackman waveforms need block 1); matched-filter gain is an upper bound",
          "G-W2: panel null emulated from one IMOS site; mismatched for the shot-dominated H08S panels",
          "G-W3: no null for the H08S suppression residual (needs raw triad data or adjacent survey hours)",
          "G-W4: secondary-target nulls at file stride 4 (alpha 0.001 at the resolution floor)",
          "G-W5: stochastic-resonance background rate 0.92/s, pre-registered target 1/s not reached on the fixed grid",
          "G-W6: two-station stacking idealised (equal SNR, known lag)"],
 "next": "Close G-W1 with block 1 digitised waveforms (real long-range arrival, known source); build per-receiver template banks from the bathymetry-following KRAKEN paths at receiver depth; add M1b as the primary screen statistic in blocks 5/7; apply (c1)+(c2) before the H08S screen.",
 "blocker": "none for this block"
}
r = host.submit_output(output,
    completion_bullets=["Pre-registered and committed weak-signal trial design before any statistic (78c7e88)",
                        "Ran 10 detectors on real IMOS background with synthetic KRAKEN-dispersed pulses: matched filters ~7 dB SNR_50 vs 13-16 dB STA/LTA (model-matched upper bound)",
                        "Scanned digitised Kadri panels and suppressed H08S airgun shots; candidates labelled, none claimed",
                        "Committed note, three charts, code, tables and coordination entry (c2b4548, 622dc6f)"],
    deviations=["Ground-truth cases named in the brief (San Juan, F-35A, Blackman shots) not run: no digitised waveforms available overnight (block 1 deliverable); synthetic pulses used as the work order specified",
                "Secondary targets 3274 and 3250 at file stride 4 (336 of 1,344 files) and 60 instead of 120 injections per cell (pre-registered)",
                "SNR grid extended 15-30 dB after the first run (amendment 1, disclosed; pre-registered results stand)",
                "All detectors run at 100 Hz, so the STA/LTA baseline is a 100 Hz variant of the module's D1 (declared)",
                "Stochastic-resonance background rate 0.92/s instead of the pre-registered 1/s target (fixed parameter grid)",
                "Panel null is an emulated plot-decimation of IMOS 3376 background, not H01W/H08S noise"])
print(r)
