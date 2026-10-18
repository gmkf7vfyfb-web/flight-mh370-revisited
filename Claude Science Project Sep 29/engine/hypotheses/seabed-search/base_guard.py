"""Refuse to score with a base that has fallen back to Phase 2 + Bluefin-21 (Pete, 13 Oct and 18 Oct 2026).

The base is FOUR campaigns: ATSB Phase 2, Bluefin-21, Ocean Infinity 2018 and Ocean Infinity 2025-26 (outboard band),
at the inferred geometry, labelled BASE_LABEL. Without Ocean Infinity is a labelled sensitivity only.

    import base_guard; base_guard.check()            # raises SystemExit on any mismatch
    python hypotheses/seabed-search/base_guard.py    # same check from the shell
"""
import pathlib
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
BASE_LABEL = "Ocean Infinity coverage inferred (grade C), included as best estimate"
SENSITIVITY_LABEL = "sensitivity: without Ocean Infinity (ATSB Phase 2 + Bluefin-21 only)"
# name -> (detection_probability, coverage_fraction); the values the base must carry, from the module's sources
BASE = {"phase2-2014-2017": (0.945, 1.0), "bluefin-2014": (0.9, 1.0),
        "ocean-infinity-2018": (0.9, 0.889), "ocean-infinity-2025": (0.9, 0.7808)}
NOT_EVIDENCE = ("next", "planned", "inboard", "contract", "proposed", "mapping", "bathymetr", "surface")


def campaigns(path=HERE / "run.toml"):
    doc = tomllib.loads(pathlib.Path(path).read_text())
    return doc["hypotheses"]["seabed-search"]["campaigns"]


def check(path=HERE / "run.toml"):
    got = {c["name"]: (float(c["detection_probability"]), float(c.get("coverage_fraction", 1.0))) for c in campaigns(path)}
    bad = [n for n in got for w in NOT_EVIDENCE if w in n.lower()]
    if bad:
        sys.exit(f"base_guard: {path} lists {bad}: planned, contract, mapping or surface areas are never non-detection evidence")
    if got != BASE:
        sys.exit(f"base_guard: {path} is not the ruled base.\n  want {BASE}\n  got  {got}\n"
                 "The base is Phase 2 + Bluefin-21 + Ocean Infinity 2018 + Ocean Infinity 2025-26 (Pete, 13 Oct 2026). "
                 "Use without-ocean-infinity.toml for the labelled sensitivity.")
    return BASE_LABEL


if __name__ == "__main__":
    print(check())
