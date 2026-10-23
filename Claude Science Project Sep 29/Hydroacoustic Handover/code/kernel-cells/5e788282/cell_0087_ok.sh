cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
cat > prepare/metz_f35a/u1_channel.py <<'E'
"""U1 of prereg.py (7dc315f), descriptive: sound-channel axis depth and surface-to-axis contrast along the first 500 km of
the F-35A -> H11S path, at the H11S end (with the DIGITISED Metz Fig. 4 as check), and at the run J median-region
profile (37.5 S 89.5 E, WOA23 A5B4 March); plus the route-B broadband source exposure level. Writes u1_channel.json.
Usage: python u1_channel.py <step2_dir> <results_dir>
"""
import json, pathlib, sys
import numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import air9_tl_validation as A, step2_tl as S2
def ax(z, c):
    ok = np.isfinite(c); z, c = z[ok], c[ok]; i = int(np.argmin(c)); return dict(axis_depth_m=float(z[i]), c_axis=float(c[i]), c_surface=float(c[0]), contrast_m_s=float(c[0] - c[i]))
def main(step2, res):
    step2, res = pathlib.Path(step2), pathlib.Path(res)
    s = pd.read_csv(step2 / "paths/ssp_f35a-H11S.csv"); nodes = A.node_profiles(s); out = {"f35a_path_nodes": []}
    for k in sorted(nodes):
        r, z, c = nodes[k]
        if r <= 500 or k == max(nodes):
            out["f35a_path_nodes"].append(dict(node=int(k), range_km=float(r), **ax(z, c)))
    ref = S2.reference_profile(); out["runj_median_region_37p5S_89p5E_A5B4_Mar"] = ax(ref.depth_m.values, ref.c_m_s.values)
    f4 = pd.read_csv(res.parent / "digitised/metz2023/fig4_h11_soundspeed_DIGITISED.csv")
    out["metz_fig4_digitised"] = {t: ax(g.sort_values("depth_m").depth_m.values, g.sort_values("depth_m").sound_speed_m_s.values) for t, g in f4.groupby("triplet")}
    rb = pd.read_csv(res / "step2_routeB.csv"); g = rb[(rb.fc_hz > 0) & (rb.floor_db == 80) & (rb.src_depth_m == 10) & (rb.tl == "ram")]
    out["routeB_source_SEL_4_64_db_re_1uPa2s_1m"] = {el: float(10 * np.log10((h.se_rx_pa2s * 10 ** (h.tl_db / 10)).sum() / 1e-12)) for el, h in g.groupby("element")}
    json.dump(out, open(res / "u1_channel.json", "w"), indent=1); print(json.dumps(out, indent=0)[:3000])
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
E
python prepare/metz_f35a/u1_channel.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a/step2 results-data/metz_f35a 2>&1 | tr -d '\n' | head -c 3000