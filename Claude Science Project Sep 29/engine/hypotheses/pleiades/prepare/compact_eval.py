"""Run C compact impact format (end of flight, 10 Oct 2026 ~20:45 UTC) for this module.

End of flight writes run C as `<stratum>/seed-<k>/{impacts32.npy, parents32.npy, run.json, COLUMNS.txt}`: float32, times
as seconds after T0, `mode`/`alternative` moved to parents32, kinetic energies and `log_q_correction` dropped. Two
consequences for this module:

1. Reading columns (weights, 00:19 log-likelihoods, positions): use end of flight's own reader
   (`smoke/compact_impacts.load`, read-only), so the names and unix times are theirs. `seed_reader` hides the format.
2. `mh370 evaluate` (core, crates/mh370/src/impacts.rs) accepts float32, but requires run.json `impact_columns` to begin
   with the 21 `IMPACT_COLUMNS`. The compact layout does not, so evaluate refuses it ("older column layout").
   This is a core-owned check, so it is NOT changed here. Disclosed module-side stub instead: `eval_input` rebuilds a
   temporary float64 file with exactly the 21 core columns from the compact one, in this module's own run tree, for
   evaluate to read. Rebuilt columns are:
   - `mode`/`alternative`: joined from parents32 by `parent`;
   - `kinetic_energy_j` = 1/2 m |v|^2 and `vertical_kinetic_energy_j` = 1/2 m v_up^2: end of flight's stated identities;
   - `unix_s`/`takeover_unix_s` = t + T0;
   - `log_q_correction` = 0, because compact `weight` already carries the within-parent correction (end of flight).
   The seabed-search and Pléiades impact modules read position only (Pléiades releases at a fixed 00:20 UTC), so none
   of the rebuilt columns enters a likelihood. The temporary file is deleted after evaluate has run.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EOF_SMOKE = HERE.parents[1] / "end-of-flight" / "smoke"
IMPACT_COLUMNS = ["weight", "parent", "mode", "alternative", "family", "unix_s", "latitude_deg", "longitude_deg",
                  "velocity_east_mps", "velocity_north_mps", "velocity_up_mps", "flight_path_angle_deg", "mass_kg",
                  "kinetic_energy_j", "vertical_kinetic_energy_j", "takeover_unix_s", "takeover_latitude_deg",
                  "takeover_longitude_deg", "takeover_altitude_ft", "arc_distance_nm", "log_q_correction"]


def _eof_compact():
    import sys
    if str(EOF_SMOKE) not in sys.path:
        sys.path.insert(0, str(EOF_SMOKE))   # displacement_hist imports compact_impacts by name
    spec = importlib.util.spec_from_file_location("eof_compact_impacts", EOF_SMOKE / "compact_impacts.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def is_compact(sd):
    return (Path(sd) / "impacts32.npy").exists()


def seed_dirs(root):
    return sorted(d for d in Path(root).glob("seed-*") if (d / "impacts.npy").exists() or (d / "impacts32.npy").exists())


def seed_reader(sd):
    """(column names, g, n_rows) for either format; g(name) -> float64 array, unix times restored."""
    sd = Path(sd)
    if is_compact(sd):
        meta, g = _eof_compact().load(sd)
        return list(meta["impact_columns"]), g, int(np.load(sd / "impacts32.npy", mmap_mode="r").shape[0])
    cols = [l.split("\t")[-1] for l in (sd / "COLUMNS.txt").read_text().splitlines() if l.strip()]
    A = np.load(sd / "impacts.npy", mmap_mode="r")
    idx = {c: i for i, c in enumerate(cols)}
    return cols, (lambda n: np.asarray(A[:, idx[n]], np.float64)), int(A.shape[0])


def eval_input(sd, tmp):
    """Path of an impacts file `mh370 evaluate` accepts. Full format: the file itself. Compact: a rebuilt temporary
    float64 file with the 21 core columns under <tmp>/<seed>/ (caller deletes it after evaluate)."""
    sd = Path(sd)
    if not is_compact(sd):
        return sd / "impacts.npy"
    _, g, n = seed_reader(sd)
    P = np.load(sd / "parents32.npy", mmap_mode="r")
    pcol = json.loads((sd / "run.json").read_text())["compact"]["parents_columns"]
    par = g("parent").astype(np.int64)
    lut_mode = np.full(int(P[:, pcol.index("parent")].max()) + 1, np.nan); lut_alt = lut_mode.copy()
    pp = np.asarray(P[:, pcol.index("parent")], np.int64)
    lut_mode[pp] = P[:, pcol.index("mode")]; lut_alt[pp] = P[:, pcol.index("alternative")]
    out = Path(tmp) / sd.name; out.mkdir(parents=True, exist_ok=True)
    X = np.lib.format.open_memmap(out / "impacts.npy", mode="w+", dtype=np.float64, shape=(n, len(IMPACT_COLUMNS)))
    m, ve, vn, vu = g("mass_kg"), g("velocity_east_mps"), g("velocity_north_mps"), g("velocity_up_mps")
    built = {"mode": lut_mode[par], "alternative": lut_alt[par], "kinetic_energy_j": 0.5 * m * (ve ** 2 + vn ** 2 + vu ** 2),
             "vertical_kinetic_energy_j": 0.5 * m * vu ** 2, "log_q_correction": np.zeros(n)}
    for j, c in enumerate(IMPACT_COLUMNS):
        X[:, j] = built[c] if c in built else g(c)
    X.flush(); del X
    meta = json.loads((sd / "run.json").read_text())
    meta["impact_columns"] = IMPACT_COLUMNS
    meta["pleiades_eval_input"] = {"rebuilt_from": str(sd / "impacts32.npy"), "rebuilt_columns": sorted(built),
                                   "note": "module-side stub for mh370 evaluate; see compact_eval.py"}
    (out / "run.json").write_text(json.dumps(meta, indent=1))
    return out / "impacts.npy"
