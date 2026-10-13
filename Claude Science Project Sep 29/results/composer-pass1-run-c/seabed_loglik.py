"""Composer pass 1 (run C) stand-in glue: searched areas' point-target non-detection log-likelihood, applied directly.

A TRANSCRIPTION of engine/hypotheses/seabed-search/lib.rs (Raster::decode, Raster::coverage, miss_probability with
Dependence::Shared, point target) with hypotheses/seabed-search/run.toml (rho 0.05; phase2 q 0.945; bluefin-2014 q 0.9).
Needed because `mh370 evaluate` refuses the run C compact layout ("impacts.npy has an older column layout").
Validated against `mh370 evaluate` output of pass 0 on core (b) (see validate()). Delete when evaluate reads compact files.
"""
import pathlib, struct, sys
import numpy as np

COV = pathlib.Path(__file__).resolve().parent.parent / "repo/Claude Science Project Sep 29/engine/hypotheses/seabed-search/coverage"
RHO = 0.05
CAMPAIGNS = [("phase2", 0.945), ("bluefin-2014", 0.9)]


def decode(path):
    b = pathlib.Path(path).read_bytes()
    assert b[:8] == b"MH370COV" and struct.unpack_from("<I", b, 8)[0] == 1
    south, west, step = struct.unpack_from("<3d", b, 12)
    rows, cols, runs = struct.unpack_from("<3I", b, 36)
    r = np.frombuffer(b, np.uint8, 3 * runs, 48).reshape(runs, 3)
    vals = np.repeat(r[:, 0], r[:, 1].astype(np.int64) | (r[:, 2].astype(np.int64) << 8))
    assert vals.size == rows * cols and len(b) == 48 + 3 * runs
    return south, west, step, rows, cols, vals.reshape(rows, cols)


def coverage(R, lat, lon):
    south, west, step, rows, cols, v = R
    y = (lat - south) / step - 0.5; x = (lon - west) / step - 0.5
    ok = (y > -1.0) & (x > -1.0) & (y < rows) & (x < cols)
    y = np.where(ok, y, 0.0); x = np.where(ok, x, 0.0)
    r = np.floor(y); c = np.floor(x); fy = y - r; fx = x - c; r = r.astype(np.int64); c = c.astype(np.int64)
    def cell(rr, cc):
        inside = (rr >= 0) & (cc >= 0) & (rr < rows) & (cc < cols)
        return np.where(inside, v[np.clip(rr, 0, rows - 1), np.clip(cc, 0, cols - 1)] / 255.0, 0.0)
    out = (1 - fy) * ((1 - fx) * cell(r, c) + fx * cell(r, c + 1)) + fy * ((1 - fx) * cell(r + 1, c) + fx * cell(r + 1, c + 1))
    return np.where(ok, out, 0.0)


_R = None
def loglik(lat, lon):
    global _R
    if _R is None:
        _R = [(decode(COV / f"{n}.cov"), q) for n, q in CAMPAIGNS]
    lat = np.asarray(lat, float); lon = np.asarray(lon, float)
    fin = np.isfinite(lat) & np.isfinite(lon)
    la, lo = np.where(fin, lat, 0.0), np.where(fin, lon, 0.0)
    miss = np.ones_like(la)
    for R, q in _R:
        miss = miss * (1.0 - coverage(R, la, lo) * q)
    return np.where(fin, np.log(RHO + (1.0 - RHO) * miss), np.nan)


def validate(n=3199968):
    """Pass 0's `mh370 evaluate` output on core (b) next-free seed 1 against this transcription."""
    import json
    W = pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/1a8f3e86-6be3-4188-8e32-ace1e7d81e9f/work/evaluate")
    ref = np.load(W / "seabed-next-free-1.npy")
    sd = pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/next-free/seed-1")
    meta = json.loads((sd / "run.json").read_text()); c = meta["impact_columns"]
    X = np.load(sd / "impacts.npy", mmap_mode="r")
    lat = np.asarray(X[:, c.index("latitude_deg")]); lon = np.asarray(X[:, c.index("longitude_deg")])
    mine = loglik(lat, lon)
    both = np.isfinite(ref) & np.isfinite(mine)
    return {"rows": int(ref.size), "nan_agree": bool(np.array_equal(np.isnan(ref), np.isnan(mine))),
            "max_abs_diff": float(np.max(np.abs(ref[both] - mine[both]))), "rows_nonzero": int((ref[both] != 0).sum())}


if __name__ == "__main__":
    print(validate())
