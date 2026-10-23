cd leg; python - <<'E'
s=open('levels.py').read()
s=s.replace('''    n = {lg: float(10 * np.log10(sum(10 ** (nb[(nb.logger == lg) & (nb.band == b)].p50_1s.iloc[0] / 10) for b in ("5-10", "10-20", "20-40")))) for lg in (3376, 3315)}
    out = {"PerthCanyon_3376": n[3376], "PerthCanyon_3315": n[3315],''','''    n = {lg: float(10 * np.log10(sum(10 ** (nb[(nb.logger == lg) & (nb.band == b)].p50_1s.iloc[0] / 10) for b in ("5-10", "10-20", "20-40")))) for lg in (3376, 3315)}
    # the DETECTOR's background median (imos_detectors spl_med over role-B recordings, the SNR reference of the P_D curves) is
    # recovered from the committed candidates (spl_max_db - snr_db); 3315 is offset from it by the noise_bands difference
    c = pd.read_csv(HY + "results-data/kadri_northern/candidates.csv"); c = c[(c.station == "PerthCanyon_3376") & c.snr_db.notna()]
    m3376 = float(np.median(c.spl_max_db - c.snr_db)); n = {3376: m3376, 3315: m3376 + n[3315] - n[3376]}
    out = {"PerthCanyon_3376": n[3376], "PerthCanyon_3315": n[3315],''')
s=s.replace("Noise (background median 1 s 5-40 Hz SPL): 3376/3315 from imos1d noise_bands (power sum 5-10/10-20/20-40);","Noise (background median 1 s 5-40 Hz SPL): 3376 = the detector's own role-B median (spl_max - snr of committed candidates,\n  96.2 dB re 1 uPa^2); 3315 = 3376 + noise_bands difference;")
open('levels.py','w').write(s)
E
cd ..; python -c "
import sys; sys.path.insert(0,'leg'); import levels as L, numpy as np; N=L.noise(); print({k:round(v,2) for k,v in N.items()})
T=L.tl_tables(); C=L.pd_curves(); r=L.station_levels(np.array([2e9]),np.array([3.0]),np.array([1591.0]),'H01W',T,N,C)
for e,v in r.items(): print(e,{k:float(np.round(x[0],4)) for k,x in v.items()})"; cat leg/scan.log