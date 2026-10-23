cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
python - <<'EOF'
s=open("run_h08s.py").read()
old_z = s[s.find("def zlog(e):"):s.find("def db(a, b):")]
new_z = '''def zlin(e, ref):
    """z of the envelope against the noise floor: median and MAD of the RAW envelope in the shot-free gaps (ref)."""
    med = np.median(ref); mad = 1.4826 * np.median(np.abs(ref - med))
    return (e - med) / max(mad, 1e-12)


def cand_peaks(tg, e, ref, mask=None, z=3.0):
    zz = zlin(e, ref)
    if mask is not None:
        zz = np.where(mask, zz, -np.inf)
    pk, _ = signal.find_peaks(zz, distance=int(3 * FS), height=z)
    return tg[pk], zz[pk]


'''
s = s.replace(old_z, new_z)
s = s.replace('''        for stage, ee, mask in (("raw", e, None), ("c1", resp, None), ("c1+c2", resp, gm)):
            tt, zz = cand_peaks(tg, ee, mask)''', '''        ref = e[shotfree]
        for stage, ee, mask in (("raw", e, None), ("c1", resp, None), ("c1+c2", resp, gm)):
            tt, zz = cand_peaks(tg, ee, ref, mask)''')
s = s.replace('''                hit_raw = any(abs(cand_peaks(tg, e2)[0] - tpeak) <= 2.0)
                hit_c1 = any(abs(cand_peaks(tg, resp2)[0] - tpeak) <= 2.0)
                hit_c12 = any(abs(cand_peaks(tg, resp2, gm)[0] - tpeak) <= 2.0)
                inj.append(dict(panel=pnl, level_db=float(lev), onset_s=on, hit_raw=hit_raw, hit_c1=hit_c1, hit_c1c2=hit_c12, peak_gated=bool(not gm[min(int((tpeak - tg[0]) * FS), len(gm) - 1)])))''',
'''                hit_raw = any(abs(cand_peaks(tg, e2, ref)[0] - tpeak) <= 2.0)
                hit_c1 = any(abs(cand_peaks(tg, resp2, ref)[0] - tpeak) <= 2.0)
                hit_c12 = any(abs(cand_peaks(tg, resp2, ref, gm)[0] - tpeak) <= 2.0)
                # control: the same rule at the same time with NO injection (chance coincidence with shots / residual peaks)
                ctl_raw = any(abs(cand_peaks(tg, e, ref)[0] - tpeak) <= 2.0)
                ctl_c1 = any(abs(cand_peaks(tg, resp, ref)[0] - tpeak) <= 2.0)
                ctl_c12 = any(abs(cand_peaks(tg, resp, ref, gm)[0] - tpeak) <= 2.0)
                inj.append(dict(panel=pnl, level_db=float(lev), onset_s=on, hit_raw=hit_raw, hit_c1=hit_c1, hit_c1c2=hit_c12, ctl_raw=ctl_raw, ctl_c1=ctl_c1, ctl_c1c2=ctl_c12, peak_gated=bool(not gm[min(int((tpeak - tg[0]) * FS), len(gm) - 1)])))''')
s = s.replace('[["hit_raw", "hit_c1", "hit_c1c2", "peak_gated"]]', '[["hit_raw", "hit_c1", "hit_c1c2", "ctl_raw", "ctl_c1", "ctl_c1c2", "peak_gated"]]')
open("run_h08s.py","w").write(s)
EOF
grep -n "zlog" run_h08s.py; echo "ok"