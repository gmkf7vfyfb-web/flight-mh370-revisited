rows=[dict(item='H01W-2 (Royer strip) max in +/-20 s window, dB re median',value=3.32,note='sd 1.29 dB over +/-300 s; 33% of 40-s windows have a higher max'),
 dict(item='SSEIR pulses >4 dB in +/-300 s',value=43,note='interval 9.4-10.9 s (1.56 s bins); autocorr 0.81 at 20.3 s; excess 5-40 Hz 9.5 dB, 10-15 Hz 8.7 dB'),
 dict(item='SWAMS3 pulses >4 dB in +/-300 s',value=52,note='autocorr 0.73 at 9.4 s, 0.80 at 20.3 s; excess 5-40 Hz 5.5 dB, 10-15 Hz 6.2 dB'),
 dict(item='H08S shot interval (h08s_template_shots.csv), s',value=9.98,note='IQR 9.83-10.10'),
 dict(item='Predicted SNR at F-35A coupling, median energy: H01W / 3376 / 3274, dB',value='5.7 / 2.0 / -8.3',note='candidates-A-F-summary.csv; provisional, propagation and coupling not calibrated'),
 dict(item='Member offsets from orange line (old fit): H01W / 3376 / 3274, s',value='+8.9 / -6.3 / -2.6',note='3376 member invalid (2-5 Hz)')]
pd.DataFrame(rows).to_csv('cand/candA_raw_panel_checks.csv',index=False); print('ok')