cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
p='digitise_waveform_rasters.py'; s=open(p).read()
s=s.replace('''def summarise(t, env, win, dt_px):
    out = ~((t >= win[0]) & (t <= win[1])); noise = float(np.percentile(np.abs(env[out]), 99)) if out.any() else np.nan''',
'''def arrivals(t, a, noise, sep=20.0, k=4.0):
    """Times of local maxima of |envelope| above k x noise, at least sep seconds apart (strongest first)."""
    idx = [i for i in np.argsort(a)[::-1] if a[i] > k * noise]; keep = []
    for i in idx:
        if all(abs(t[i] - t[j]) >= sep for j in keep): keep.append(i)
        if len(keep) >= 6: break
    return ";".join(f"{t[i]:.1f}s:{a[i] / a.max():.2f}" for i in sorted(keep))

def summarise(t, env, win, dt_px, floor=0.0):
    out = ~((t >= win[0]) & (t <= win[1])); noise = float(np.percentile(np.abs(env[out]), 99)) if out.any() else np.nan
    noise = max(noise, floor)''')
s=s.replace('''    return dict(peak=float(a[ipk]), t_peak_s=float(t[ipk]), t_onset_s=on, noise_p99=noise, snr=float(a[ipk] / noise) if noise else None)''',
'''    return dict(peak=float(a[ipk]), t_peak_s=float(t[ipk]), t_onset_s=on, noise_p99=noise, snr=float(a[ipk] / noise) if noise else None,
                arrivals_t_s_rel=arrivals(t, a, noise))''')
s=s.replace("s = summarise(x, env, win, dt); s.update(name=name, source=img[2:]","s = summarise(x, env, win, dt, floor=px); s.update(name=name, source=img[2:]")
s=s.replace("bt = (int(t_ + k * h + 3), int(t_ + (k + 1) * h - 3))","bt = (int(t_ + k * h + (12 if k == 0 else 3)), int(t_ + (k + 1) * h - (12 if k == 2 else 3)))   # skip tick marks at the box edges")
s=s.replace('''("nielsen2021_fig3_charge_H10N", (71, 811, 573, 1413), "2017-12-01T21:02:55Z", (120, 700)),''','''("nielsen2021_fig3_charge_H10N", (71, 811, 573, 1413), "2017-12-01T21:02:55Z", (500, 700)),''')
s=s.replace('''("nielsen2021_fig3_charge_H10S", (712, 811, 1213, 1413), "2017-12-01T21:02:55Z", (40, 600)),''','''("nielsen2021_fig3_charge_H10S", (712, 811, 1213, 1413), "2017-12-01T21:02:55Z", (420, 600)),''')
for a_,b_ in [("(269, 270, 1291, 400)","(269, 278, 1291, 398)"),("(269, 647, 1291, 776)","(269, 655, 1291, 776)"),("(269, 1104, 1291, 1232)","(269, 1110, 1291, 1229)"),("(269, 1480, 1291, 1610)","(269, 1488, 1291, 1607)")]:
    s=s.replace(a_,b_)
open(p,'w').write(s)
EOF
python digitise_waveform_rasters.py /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/0f0b1c26-b241-4b3b-9f87-53c4386c8175/src/pmc24 ../results-data/digitised/ground-truth-cases/figures ../results-data/digitised/cmst-2014/figures ../results-data/digitised/waveform-rasters > /tmp/wr.txt 2>&1; python -c "
import pandas as pd; d=pd.read_csv('../results-data/digitised/waveform-rasters/waveform_raster_summary.csv'); pd.set_option('display.width',250)
print(d[['name','unit','peak','snr','t_onset_utc','t_peak_utc','arrivals_t_s_rel']].to_string())"