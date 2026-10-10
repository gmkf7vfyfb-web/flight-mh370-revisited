"""Compact impact format for run C (architecture ~14:30 -0600 10 Oct, Pete): float32, only the columns consumers read,
parent-level fields once per parent. Columns: compact-columns.json (core + optional; the dropped list is recorded).

Times are stored as seconds after T0 = 2014-03-08 00:00:00 UTC (float32 cannot hold unix seconds: 1.39e9 s resolves only
to 128 s; offsets of ~1e4 s resolve to about 1 ms). The reader restores unix seconds under the ORIGINAL names, so
load(...) is a drop-in for code that reads impacts.npy by column name.

    python compact_impacts.py write RUN_DIR SEED_DIR OUT_SEED_DIR [--no-optional]   # full -> compact, verified
    python compact_impacts.py check OUT_SEED_DIR                                      # integrity (SHA256SUMS)
In code:  meta, g = load(seed_dir)   # g(name) -> float64 array, original column names
"""
import hashlib, json, pathlib, sys
import numpy as np

T0 = 1394236800.0
HERE = pathlib.Path(__file__).resolve().parent
SPEC = json.loads((HERE / "compact-columns.json").read_text())
TIME = {"unix_s": "t_impact_s", "takeover_unix_s": "t_takeover_s", "latent:realised_flameout_unix_s": "t_realised_flameout_s",
        "latent:onset_unix_s": "t_onset_s"}
INV = {v: k for k, v in TIME.items()}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()


def write(run, sd, out, optional=True):
    run, sd, out = pathlib.Path(run), pathlib.Path(sd), pathlib.Path(out)
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r")
    names = SPEC["core"] + (SPEC["optional"] if optional else [])
    derived = list(SPEC.get("derived", {}))
    out.mkdir(parents=True, exist_ok=True)
    Y = np.lib.format.open_memmap(out / "impacts32.npy", mode="w+", dtype=np.float32, shape=(X.shape[0], len(names) + len(derived)))
    step = 500_000; worst = {}
    for a in range(0, X.shape[0], step):
        B = np.array(X[a:a + step])
        for j, n in enumerate(names):
            v = B[:, cols[n]] - (T0 if n in TIME else 0.0)
            Y[a:a + step, j] = v.astype(np.float32)
            back = Y[a:a + step, j].astype(np.float64) + (T0 if n in TIME else 0.0)
            ok = np.isfinite(B[:, cols[n]])
            assert np.array_equal(ok, np.isfinite(back)), n          # NaN/inf pattern preserved exactly
            if ok.any():
                rel = np.abs(back[ok] - B[ok, cols[n]]) / np.maximum(np.abs(B[ok, cols[n]]), 1e-30)
                ab = np.abs(back[ok] - B[ok, cols[n]])
                worst[n] = max(worst.get(n, 0.0), float(ab.max() if n in TIME else rel.max()))
        if derived:
            fam = family_labels(B[:, cols["latent:onset_mechanism"]], B[:, cols["latent:control_realised"]])
            for j, n in enumerate(derived):
                Y[a:a + step, len(names) + j] = fam[n].astype(np.float32)
    Y.flush(); del Y
    if "loglik:none" in cols and "loglik:none" not in names:   # dropped because identically 0: prove it
        for a in range(0, X.shape[0], step):
            assert not np.any(np.asarray(X[a:a + step, cols["loglik:none"]])), "loglik:none is not identically 0"
    par = np.array(X[:, cols["parent"]], np.int64); w = np.array(X[:, cols["weight"]])
    P = np.zeros((int(par.max()) + 1, 4), np.float32); P[:, 0] = np.arange(P.shape[0])
    P[:, 1] = np.bincount(par, weights=w, minlength=P.shape[0])
    first = np.unique(par, return_index=True)[1]
    P[par[first], 2] = np.array(X[first, cols["mode"]]); P[par[first], 3] = np.array(X[first, cols["alternative"]])
    np.save(out / "parents32.npy", P)
    cm = dict(meta); cm["impact_columns"] = [TIME.get(n, n) for n in names] + derived
    cm["compact"] = {"format": "float32 v1", "derived_columns": SPEC.get("derived", {}), "T0_unix_s": T0, "time_columns": INV, "source_columns": meta["impact_columns"],
                     "dropped": [c for c in meta["impact_columns"] if c not in names + ["mode", "alternative"]],
                     "parents_columns": ["parent", "weight_handoff", "mode", "alternative"],
                     "max_abs_error_time_s_or_max_rel_error": worst, "rows": int(X.shape[0])}
    (out / "run.json").write_text(json.dumps(cm, indent=1))
    (out / "COLUMNS.txt").write_text("\n".join(cm["impact_columns"]) + "\n")
    (out / "SHA256SUMS").write_text("".join(f"{sha(out / f)}  {f}\n" for f in ("impacts32.npy", "parents32.npy", "run.json", "COLUMNS.txt")))
    return cm


def family_labels(onset_mechanism, control_realised):
    """Pete's end-to-end hypothesis families (architecture 14:55 -0600 10 Oct). Codes: compact-columns.json `derived`.
    onset_mechanism: 0 anticipatory, 1 fuel cue, 2 flame-out-associated (taxonomy Initiation::ALL).
    control_realised: 0 ditching attempt, 1 maintained-then-lost, 2 no intervention, 3 upset then (demonstrated) recovery
    (taxonomy Control::ALL; an undemonstrated recovery is already reported as 1)."""
    om = np.asarray(onset_mechanism); cr = np.asarray(control_realised)
    onset = np.where(om == 2, 0.0, np.where((om == 0) | (om == 1), 1.0, np.nan))
    control = np.select([cr == 2, cr == 1, (cr == 0) | (cr == 3)], [0.0, 1.0, 2.0], np.nan)
    fam = np.where(onset == 1, 3.0, np.select([control == 0, control == 2, control == 1], [1.0, 2.0, 4.0], np.nan))
    fam = np.where(np.isnan(onset), np.nan, fam)
    return {"onset_code": onset, "control_code": control, "family_code": fam}


def load(sd):
    """(meta with ORIGINAL column names, g) for a compact seed dir; g(name) returns float64 with unix times restored."""
    sd = pathlib.Path(sd); meta = json.loads((sd / "run.json").read_text())
    Y = np.load(sd / "impacts32.npy", mmap_mode="r"); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    def g(name):
        if name in TIME: return np.asarray(Y[:, cols[TIME[name]]], np.float64) + T0
        if name == "loglik:none" and name not in cols: return np.zeros(Y.shape[0])   # dropped: identically 0 (checked at write)
        return np.asarray(Y[:, cols[name]], np.float64)
    m = dict(meta); m["impact_columns"] = [INV.get(c, c) for c in meta["impact_columns"]]
    if "loglik:none" in meta.get("compact", {}).get("dropped", []):
        k = next((i for i, c in enumerate(m["impact_columns"]) if c.startswith("loglik:")), len(m["impact_columns"]))
        m["impact_columns"] = m["impact_columns"][:k] + ["loglik:none"] + m["impact_columns"][k:]
    return m, g


if __name__ == "__main__":
    if sys.argv[1] == "write":
        cm = write(sys.argv[2], sys.argv[3], sys.argv[4], optional="--no-optional" not in sys.argv)
        print(json.dumps({k: v for k, v in cm["compact"]["max_abs_error_time_s_or_max_rel_error"].items() if k in TIME or k in ("weight", "latitude_deg", "loglik:r600/no-offset")}, indent=0))
    elif sys.argv[1] == "check":
        d = pathlib.Path(sys.argv[2])
        for line in (d / "SHA256SUMS").read_text().splitlines():
            h, f = line.split(); assert sha(d / f) == h, f
        print("ok")
