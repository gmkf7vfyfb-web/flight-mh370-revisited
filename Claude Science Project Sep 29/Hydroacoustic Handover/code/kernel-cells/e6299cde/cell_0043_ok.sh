cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('coincidence.py').read()
s=s.replace('''Usage: python coincidence.py <out_dir>   Outputs: pairs.csv, coincidence_summary.csv"""''','''AMENDMENT 1 (disclosed, after the first run): the pre-registered time slides (k x 300 s) move a receiver's rows out
of its held data (307 s IMOS records every 15 min; 10 min panels), so the slide null is schedule-biased and reaches
its floor trivially. A HELD-SPAN PERMUTATION null is added and sets p: 2,000 draws in which each receiver's candidate
times are redrawn uniformly inside the spans actually searched (its records / panels), counts per receiver kept;
p_perm = (#draws with N >= N_obs + 1)/2001; expected_by_chance = the mean. The slide numbers are kept beside it.
Usage: python coincidence.py <out_dir>   Outputs: pairs.csv, coincidence_summary.csv"""''')
s=s.replace('''def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    C = pd.concat([pd.read_csv(out.parent / "imos" / "imos_windows.csv"), pd.read_csv(out.parent / "panels" / "panel_windows.csv")], ignore_index=True)
    C = C[C.p < R.SCREEN_P].copy(); C["receiver"] = C.receiver.astype(str)''','''N_PERM = 2000


def held_spans(Wall):
    """Searched spans per receiver from the scored windows: [window_start, window_start + 55 s] merged."""
    sp = {}
    for rx, g in Wall.groupby("receiver"):
        st = np.sort(np.unique((g.t_unix - (g.t_unix % 1)).values))  # placeholder, replaced below
        ws = g.apply(lambda r: R.hms_to_unix(r.window_start_utc + ".0"), axis=1).values
        iv = sorted(set((float(w), float(w) + R.WINDOW_S) for w in ws))
        merged = []
        for a, b in iv:
            if merged and a <= merged[-1][1] + 1e-6: merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else: merged.append((a, b))
        sp[str(rx)] = merged
    return sp


def draw_times(rng, spans, n):
    L = np.array([b - a for a, b in spans]); c = np.cumsum(L) / L.sum()
    u = rng.random(n); k = np.searchsorted(c, u); off = rng.random(n) * L[k]
    return np.array([spans[i][0] for i in k]) + off


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    Wall = pd.concat([pd.read_csv(out.parent / "imos" / "imos_windows.csv"), pd.read_csv(out.parent / "panels" / "panel_windows.csv")], ignore_index=True)
    Wall["receiver"] = Wall.receiver.astype(str)
    spans = held_spans(Wall)
    rng = np.random.default_rng(R.SEED)
    C = Wall[Wall.p < R.SCREEN_P].copy()''')
s=s.replace('''            p_slide = (np.sum(slide >= n_obs) + 1) / (len(shifts) + 1) if n_obs > 0 else 1.0''','''            p_slide = (np.sum(slide >= n_obs) + 1) / (len(shifts) + 1) if n_obs > 0 else 1.0
            perm = np.array([count_pairs(draw_times(rng, spans[a], len(A)), draw_times(rng, spans[b], len(B)), lo, hi)[0] for _ in range(N_PERM)]) if n_obs > 0 else np.zeros(1)
            p_perm = (np.sum(perm >= n_obs) + 1) / (N_PERM + 1) if n_obs > 0 else 1.0''')
s=s.replace('''kadri_a=ra.kadri_label, kadri_b=rb.kadri_label, n_pairs_obs=n_obs, p_slide=p_slide, caveats=R.CAVEATS))''','''kadri_a=ra.kadri_label, kadri_b=rb.kadri_label, n_pairs_obs=n_obs, p_perm=p_perm, p_slide=p_slide, caveats=R.CAVEATS))''')
s=s.replace('''            rows.append(dict(rx_a=a, rx_b=b, family=fam, n_a=len(A), n_b=len(B), lag_lo_s=round(lo), lag_hi_s=round(hi), n_pairs_obs=n_obs,
                             expected_by_chance=float(slide.mean()), slide_max=int(slide.max()), p_slide=p_slide, strongest_pair_max_p=best, caveats=R.CAVEATS))''','''            rows.append(dict(rx_a=a, rx_b=b, family=fam, n_a=len(A), n_b=len(B), lag_lo_s=round(lo), lag_hi_s=round(hi), n_pairs_obs=n_obs,
                             expected_by_chance=float(perm.mean()), p_perm=p_perm, slide_mean=float(slide.mean()), slide_max=int(slide.max()), p_slide=p_slide,
                             strongest_pair_max_p=best, caveats=R.CAVEATS))''')
s=s.replace('''    print(S.to_string(index=False))
    if len(P): print(P.head(12)[["rx_a", "rx_b", "family", "t_a", "det_a", "p_a", "t_b", "det_b", "p_b", "lag_s", "max_p", "p_slide", "kadri_a"]].to_string(index=False))''','''    print(S[["rx_a", "rx_b", "family", "n_a", "n_b", "n_pairs_obs", "expected_by_chance", "p_perm", "p_slide", "strongest_pair_max_p"]].to_string(index=False))
    if len(P): print(P[P.family == "primary_M1b"].head(10)[["rx_a", "rx_b", "t_a", "det_a", "p_a", "t_b", "det_b", "p_b", "lag_s", "max_p", "p_perm", "kadri_a"]].to_string(index=False))''')
open('coincidence.py','w').write(s)
EOF
python coincidence.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/coincidence 2>&1 | tail -50