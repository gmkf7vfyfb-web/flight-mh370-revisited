"""Tests for the internal fuel model files (run: python fuel-model/test_internal.py from engine/)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import internal  # noqa: E402
import tables  # noqa: E402

ENGINE = HERE.parent


def test_grid_inop_matches_lrc_inop_ff(path=ENGINE / "data/external/fuel-model/internal-v1.1.json", tol=0.02):
    """grid_inop is the one live engine's flow: within 2 % of lrc_inop_ff at every tabulated state."""
    d = json.loads(Path(path).read_text())
    g = internal.GridModel(d["grid_inop"])
    t = tables.Tables(ENGINE / "data/fuel-tables.json", inop=True)
    lm, lf = t.grids["lrc_inop_mach"], t.grids["lrc_inop_ff"]
    r = []
    for i, w in enumerate(lm.ws):
        if not (g.ws[0] <= w <= g.ws[-1]):
            continue
        for j, fl in enumerate(lm.fls):
            m, f = lm.v[i, j], lf.v[i, j]
            if np.isnan(m) or np.isnan(f) or not (g.ms[0] <= m <= g.ms[-1]):
                continue
            v = g.ff_shape(fl, w, m)[0]
            assert v is not None, (fl, w, m)
            r.append(v / f)
    r = np.array(r)
    assert len(r) > 100 and np.all(np.abs(r - 1) <= tol), (len(r), r.min(), r.max())
    return len(r), float(r.min()), float(r.max())


def test_twin_grid_unchanged(v1=ENGINE / "data/external/fuel-model/internal-v1.json",
                             v11=ENGINE / "data/external/fuel-model/internal-v1.1.json"):
    a, b = json.loads(Path(v1).read_text()), json.loads(Path(v11).read_text())
    assert a["grid"]["flow_kg_h"] == b["grid"]["flow_kg_h"] and a["grid"]["flags"] == b["grid"]["flags"]
    assert a["model"]["kappa"] == b["model"]["kappa"]
    assert a["grid_inop"]["flags"] == b["grid_inop"]["flags"]


if __name__ == "__main__":
    print("grid_inop vs lrc_inop_ff:", test_grid_inop_matches_lrc_inop_ff())
    test_twin_grid_unchanged(); print("twin grid, kappa and INOP flags identical to v1: OK")
