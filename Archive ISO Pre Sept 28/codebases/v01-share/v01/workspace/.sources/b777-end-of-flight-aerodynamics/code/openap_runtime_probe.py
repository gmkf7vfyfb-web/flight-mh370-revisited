#!/usr/bin/env python3
"""Execute the pinned OpenAP package after its source is placed on PYTHONPATH."""

from __future__ import annotations

import json

from openap import Drag, Thrust, aero


HEIGHT_FT = 35_000
MACH = 0.84
MASS_KG = 208_525.63917525773


def main() -> None:
    tas_kt = float(aero.mach2tas(MACH, HEIGHT_FT * 0.3048) / 0.514444)
    engines = []
    for name, force_engine in [
        (None, False),
        ("Trent 895", False),
        ("Trent 892", False),
        ("Trent 892", True),
    ]:
        try:
            kwargs = {"force_engine": True} if force_engine else {}
            model = Thrust("B772", name, **kwargs)
            engines.append({
                "engine": name,
                "force_engine": force_engine,
                "status": "executed",
                "maximum_cruise_thrust_N": float(model.cruise(tas_kt, HEIGHT_FT)),
                "modeled_descent_idle_thrust_N": float(model.descent_idle(tas_kt, HEIGHT_FT)),
            })
        except Exception as error:  # The rejection text is part of this probe.
            engines.append({
                "engine": name,
                "force_engine": force_engine,
                "status": "rejected",
                "exception_type": type(error).__name__,
                "message": str(error),
            })
    print(json.dumps({
        "aircraft": "B772",
        "height_ft": HEIGHT_FT,
        "mach": MACH,
        "mass_kg": MASS_KG,
        "tas_kt": tas_kt,
        "clean_drag_N": float(Drag("B772").clean(MASS_KG, tas_kt, HEIGHT_FT)),
        "engines": engines,
        "warning": "A forced engine pairing is an API execution check, not an admitted model.",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
