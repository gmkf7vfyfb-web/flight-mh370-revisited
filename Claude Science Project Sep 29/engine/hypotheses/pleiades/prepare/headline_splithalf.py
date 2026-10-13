"""Split-half for the headline settings on the correlated-error surfaces (module version of the adopted stand-in's
headline_rho_splithalf_standin.py, with surface tags: "" = as run, "-gcrel" = GlobCurrent product-relative windage, drift audit F1).

    python headline_splithalf.py <impacts root> <branch root> <surface dir> <family-evidence json> <out csv> <option> [...]
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import headline_rho_splithalf_standin as hs  # noqa: E402
import headline_rho_standin as h  # noqa: E402


def rho_L(surf, rho, model, tag=""):
    m = dict(l.split(" = ", 1) for l in (Path(surf) / f"joint-surface-rho{rho:g}{tag}.toml").read_text().splitlines())
    J = np.fromfile(Path(surf) / f"joint-surface-rho{rho:g}{tag}.f32", "<f4").reshape(2, int(m["nlat"]), int(m["nlon"])).astype(float)
    E = np.nan_to_num(np.exp(J))
    return E[model] if model != "mean" else 0.5 * (E[0] + E[1])


VARIANTS = [("rho0.25 both models, GlobCurrent product-relative", 0.25, "mean", "-gcrel"),
            ("rho0 both models, GlobCurrent product-relative", 0.0, "mean", "-gcrel"),
            ("rho0.5 both models, GlobCurrent product-relative", 0.5, "mean", "-gcrel"),
            ("rho0.25 GLORYS12", 0.25, 0, "")]
h.VARIANTS = [(k, r, (m, t)) for k, r, m, t in VARIANTS]
hs.rho_L = lambda surf, r, mt: rho_L(surf, r, mt[0], mt[1])
hs.VARIANTS = h.VARIANTS

if __name__ == "__main__":
    hs.main(*sys.argv[1:6], sys.argv[6:])
