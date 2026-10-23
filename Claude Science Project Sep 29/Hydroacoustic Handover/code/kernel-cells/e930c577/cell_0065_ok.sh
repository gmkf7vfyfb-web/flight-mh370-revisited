cd leg; python - <<'E'
s=open('scan_runj_L.py').read()
s=s.replace("(dx <= 450e3) | (dh <= 450e3)","(dx <= 400e3) | (dh <= 400e3)")
s=s.replace("np.savez(o, **keep)","keep = {k: (v.astype(np.float32) if (isinstance(v, np.ndarray) and v.dtype == np.float64 and v.ndim == 1 and k not in ('t_impact', 't_flameout', 'base', 'C1', 'C2s', 'C2u') and not k.startswith('ld_')) else v) for k, v in keep.items()}\n    np.savez_compressed(o, **keep)")
s=s.replace("within 450 km of the arc crossing","within 400 km of the arc crossing")
open('scan_runj_L.py','w').write(s)
E
rm -f scan/run-j-free__seed-1.npz; grep -n "savez\|400e3" scan_runj_L.py; df -h . | tail -1