
"""Access-band parameters per satellite, as used by the satellite-coverage module (parent session 20 Oct 2026).
geometry_params(row) takes one row of satellite-specs-expanded.csv."""
import numpy as np, pandas as pd
def geometry_params(s):
    h = float(s.altitude_km); is_sar = s.family in ("sar","recon_sar")
    sw = float(s.nominal_swath_km) if pd.notna(s.nominal_swath_km) else 10.0
    if is_sar:
        side = str(s.sar_look_side).lower()
        return dict(is_sar=True, imin=float(s.sar_incidence_min_deg), imax=float(s.sar_incidence_max_deg),
                    sides=["right"] if side.startswith("right") else ["left","right"], swath=sw, h=h)
    mo = float(s.max_off_nadir_deg) if pd.notna(s.max_off_nadir_deg) else 0.0
    return dict(is_sar=False, max_off_nadir=mo, swath=sw, h=h)
# near/far ground offsets for a pass at altitude h (km, use the propagated median altitude over the pass):
#   SAR:     near = satgeom.ground_offset_sar(h, imin), far = satgeom.ground_offset_sar(h, imax)
#   optical: near = 0, far = satgeom.ground_offset_optical(h, max_off_nadir) + swath/2
# then coincide.in_band(offset_km, g, near, far)
