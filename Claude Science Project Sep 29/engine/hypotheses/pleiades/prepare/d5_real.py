"""Two-epoch windage calibration on the REAL COSMO-SkyMed contacts and Pleiades targets. PROVISIONAL.

Runs every declared arm through twoepoch.analyse and writes one row per arm, plus the windage
posteriors (marginalised over pass time and per pass) for every arm:
  cosmo-contact-set  F1-F3 (reference, corroborated) / F1-F4 (extension)
  targets            rating-5 clusters at 3 km (reference) / rating-5 objects (18,001 assignments
                     with F1-F4) / rating 5 + 4 clusters at 3 km with rho4 in {0.25, 0.5, 1}
  cluster-weight     equal / count (prior weight of each target in the matching prior)
  error model        independent (reference) / shared
  spread             sigma_e 0.05 (reference) / 0.10 m/s; K log-uniform 30-1000 (reference)
  pi_match           0.5 (reference) / 0.9
Usage: python d5_real.py <module dir> <cosmo-tracks.csv> <outdir>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import twoepoch as te  # noqa: E402


def target_sets(module_dir: Path):
    cl = pd.read_csv(module_dir / "results/d2-clusters-3km.csv")
    obj = pd.read_csv(module_dir / "data/ga-rec2017-13-objects.csv")
    sets = {}
    for wform in ("equal", "count"):
        c5 = cl[cl.arm == "rating5"]
        sets[("rating5-clusters", wform)] = pd.DataFrame({"scene": c5.scenes, "lon": c5.mean_lon, "lat": c5.mean_lat, "w": c5[f"w_{wform}"]})
        for rho in (0.25, 0.5, 1.0):
            c = cl[(cl.arm == "rating45") & (cl.rho4 == rho)]
            sets[(f"rating45-clusters-rho4-{rho:g}", wform)] = pd.DataFrame({"scene": c.scenes, "lon": c.mean_lon, "lat": c.mean_lat, "w": c[f"w_{wform}"]})
    o5 = obj[obj.rating == 5]
    sets[("rating5-objects", "equal")] = pd.DataFrame({"scene": o5.scene, "lon": o5.longitude, "lat": o5.latitude, "w": 1.0 / len(o5)})
    return {k: v.reset_index(drop=True) for k, v in sets.items()}


def run(module_dir, tracks_csv, out):
    module_dir, out = Path(module_dir), Path(out)
    tr = te.Tracks.load(Path(tracks_csv))
    sets = target_sets(module_dir)
    arms = []
    ref = dict(contacts="F1-F3", targets="rating5-clusters", wform="equal", shared=False, sigma_e=0.05, pi=0.5)
    arms.append(dict(ref, label="reference"))
    arms.append(dict(ref, contacts="F1-F4", label="F1-F4"))
    arms.append(dict(ref, wform="count", label="cluster-weight count"))
    arms.append(dict(ref, shared=True, label="shared model error"))
    arms.append(dict(ref, sigma_e=0.10, label="sigma_e 0.10"))
    arms.append(dict(ref, pi=0.9, label="pi_match 0.9"))
    arms.append(dict(ref, contacts="F1-F4", pi=0.9, label="F1-F4, pi_match 0.9"))
    for rho in (0.25, 0.5, 1.0):
        arms.append(dict(ref, targets=f"rating45-clusters-rho4-{rho:g}", label=f"rating 4+5, rho4 {rho:g}"))
    arms.append(dict(ref, targets="rating5-objects", label="rating-5 objects"))
    arms.append(dict(ref, contacts="F1-F4", targets="rating5-objects", label="F1-F4 x rating-5 objects"))
    rows, posts = [], []
    for a in arms:
        contacts = ["F1", "F2", "F3"] + (["F4"] if a["contacts"] == "F1-F4" else [])
        targets = sets[(a["targets"], a["wform"])]
        cfg = te.Config(sigma_e_ms=a["sigma_e"], pi_match=a["pi"], shared_error=a["shared"], label=a["label"])
        R = te.analyse(tr, contacts, targets, cfg, keep_top=3)
        rows.append(dict(arm=a["label"], contacts=a["contacts"], targets=a["targets"], cluster_weight=a["wform"],
                         error="shared" if a["shared"] else "independent", sigma_e_ms=a["sigma_e"], pi_match=a["pi"],
                         n_targets=len(targets), n_assignments=R["n_assign"], expected_assignments=te.n_assignments(len(contacts), len(targets)),
                         c_mean_pct=100 * R["mean_c"], ci90_lo_pct=100 * R["ci90"][0], ci90_hi_pct=100 * R["ci90"][1],
                         ig_bits=R["ig_bits"], ig_bits_dawn=R["ig_bits_pass"][0], ig_bits_dusk=R["ig_bits_pass"][1],
                         ln_bf_free_vs_fixed=R["ln_bf_free_vs_fixed"], p_dawn=R["p_pass"][0], p_dusk=R["p_pass"][1],
                         p_any_match=R["p_any_match"], prior_any_match=1 - (1 - a["pi"]) ** len(contacts),
                         top_assignment=str(R["top"][0][0]), top_p=R["top"][0][1],
                         second_assignment=str(R["top"][1][0]), second_p=R["top"][1][1]))
        for which, q in [("marginal", R["post_c"]), ("dawn-20Mar", R["post_c_given_pass"][0]), ("dusk-21Mar", R["post_c_given_pass"][1])]:
            for c, p in zip(tr.c, q):
                posts.append(dict(arm=a["label"], which=which, c_wind=c, posterior=p))
    out.mkdir(parents=True, exist_ok=True)
    t = pd.DataFrame(rows)
    assert (t.n_assignments == t.expected_assignments).all()
    t.to_csv(out / "d5-real-arms.csv", index=False)
    pd.DataFrame(posts).to_csv(out / "d5-real-windage-posteriors.csv", index=False)
    return t, pd.DataFrame(posts)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
