cd leg; python - <<'E'
s=open('cond_pred.py').read()
s=s.replace('# peak excess (Pa) and max 1 s mean-square excess (Pa^2), digitised Fig 9c, 2-20 Hz\n SNR_OBS_3376','# peak excess (Pa) and max 1 s mean-square excess (Pa^2), digitised Fig 9c, 2-20 Hz\nSNR_OBS_3376')
open('cond_pred.py','w').write(s)
E
cd ..; python leg/cond_pred.py leg/scan leg/out > leg/out/cond_log.txt 2>&1; echo $?; grep -E "PerthCanyon_3376|H08S|Error" leg/out/cond_log.txt | head -60