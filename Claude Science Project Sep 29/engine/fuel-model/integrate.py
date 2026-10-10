"""Constant-state burn integration shared by the calibration and the cross-check."""

import math


def fly(ff, fuel_kg, zfw_kg, fl, mach, hours=None, dt_h=1 / 60, disa=0.0, tmax_h=24):
    """Integrate burn at constant FL and Mach.

    `ff(fl, w_t, mach, disa) -> (kg/h, flags)`. With `hours`, returns (fuel left, hours, flags);
    to exhaustion (hours=None) returns (0, hours to exhaustion, flags). Flow is evaluated at the
    mid-step weight (second-order; validate.py uses the start-of-step weight).
    """
    t, flags = 0.0, set()
    while True:
        if hours is not None and t >= hours - 1e-12:
            return fuel_kg, t, flags
        step = dt_h if hours is None else min(dt_h, hours - t)
        f0, fl0 = ff(fl, (zfw_kg + fuel_kg) / 1000, mach, disa)
        if f0 is None or t > tmax_h:
            return None, t, flags | {"unpriceable"}
        w_mid = (zfw_kg + fuel_kg - 0.5 * f0 * step) / 1000
        f, fl1 = ff(fl, w_mid, mach, disa)
        if f is None:
            f, fl1 = f0, fl0
        flags |= {k for k, v in fl1.items() if v is True}
        burn = f * step
        if hours is None and burn >= fuel_kg:
            return 0.0, t + step * fuel_kg / burn, flags
        fuel_kg -= burn
        t += step
