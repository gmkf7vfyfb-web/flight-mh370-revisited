"""Composer pass 0: seabed PDF = a composed impact PDF carried through settling's per-impact seabed samples, by reweighting.

PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable.

Settling's outcomes are impacts resampled from a source option (set A: none__other; set C option 0: r600-bto__other), each
with one wreckage draw. summarise_stratum.py stored, per outcome impact row, the importance weight
    iw = pooled composed weight of the product / (1/4 x the seed's source-option weight).
The seabed PDF of the product is the element-mass-weighted settled positions, weighted by iw x outcome multiplicity.
No new settling draws; settling's elements are read in place. Afloat elements have no seabed position (share reported).

Usage: python seabed.py <work dir> <settling work dir> <out json>
"""
import json, pathlib, sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import summarise_stratum as S
import report as RP

PRODUCTS = {"heldout": ("A", 0), "r600": ("C", 0)}


def main(work, swork, outp):
    work, swork = pathlib.Path(work), pathlib.Path(swork)
    D = RP.load(work); res = {"label": RP.LABEL, "products": {}}
    for tag, (T, j) in PRODUCTS.items():
        for key in ("P1", "G", "Ga", "H", "Ha"):
            pid = f"{tag}-{key}"; maps = {}; info = {}
            for st in RP.STRATA:
                fd = swork / st.replace("next-", "") / "field"
                el = fd / f"{T}_elements.f64"
                if not el.exists():
                    raise SystemExit(f"settling elements not present: {el}")
                nT = (fd / f"{T}_impacts.f64").stat().st_size // (14 * 8)
                iw = np.full(nT, np.nan)
                for k in (1, 2, 3, 4):
                    rows = D[st]["npz"][f"{pid}|seabed_rows_seed{k}"]; iw[rows] = D[st]["npz"][f"{pid}|seabed_iw_seed{k}"]
                z = np.load(fd / f"{T}_draws.npz"); mult = np.bincount(z[f"rows_{j}"], minlength=nT).astype(float)
                ow = np.where(np.isfinite(iw), iw, 0.0) * mult
                E = np.memmap(el, dtype="<f8", mode="r").reshape(-1, 8)
                r = E[:, 0].astype(np.int64); fate = E[:, 4]; mass = E[:, 7]
                wel = ow[r] * mass; settled = fate == 0
                c = S.equal_area_cell(E[:, 5], E[:, 6]); ok = settled & (c >= 0)
                m = np.bincount(c[ok], weights=wel[ok], minlength=S.NY * S.NX)
                tot = wel[np.isfinite(wel)].sum()
                maps[st] = m / tot
                sel = mult > 0
                info[RP.SNAME[st]] = {"outcome_ess": float(ow.sum() ** 2 / (ow ** 2).sum()), "outcomes": int(mult.sum()),
                                      "unmatched_outcome_rows": int((~np.isfinite(iw) & sel).sum()),
                                      "afloat_or_not_computed_mass_share": float(1 - wel[ok].sum() / tot)}
            w = RP.weights(D, tag, key, "reweighted-0019")
            mix = sum(w[s] * maps[s] for s in RP.STRATA); p = mix / mix.sum()
            res["products"][pid] = {"per_stratum": info, "hdr50_area_km2": float(RP.hdr_mask(p, 0.5).sum() * S.CELL_KM2),
                                    "hdr90_area_km2": float(RP.hdr_mask(p, 0.9).sum() * S.CELL_KM2), "map_mode": RP.smoothed_mode(p)}
            np.save(work / "summary" / f"seabed-{pid}.npy", p)
            print(pid, res["products"][pid]["hdr90_area_km2"], flush=True)
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
