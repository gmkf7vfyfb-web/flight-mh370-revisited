"""Every run's parameters and model choices beside Davey et al. (2016), differences marked.

The runner already records what a run actually used: `assumptions` (dynamics constants, prior,
measurement constants, sampler) and the merged `config`, both in `run.json`. What it does not
record is the published value each one is meant to reproduce. `report/davey_reference.json`
supplies that, with a book citation per row, and this module joins the two.

Three verdicts per row:

`same`      the run's value equals the published one (numeric comparison is relative, 1e-9).
`DIFFERS`   both values are shown. Some differences are deliberate and documented (ERA5 for
            ACCESS-G, IGRF-14 for NOAA, the sampler); others are the point of a sensitivity run
            (a widened Mach range); a few are defects worth fixing. The table does not judge
            which — it makes them all visible.
`n/a`       the quantity is not recorded at a single path in `run.json` (a per-epoch measurement
            sigma, say, or a structural choice). The reference row's note carries the comparison.

Usage:  python report/parameters.py runs/<name>            # prints the table
        python report/parameters.py runs/<name> --csv      # also writes <run>/parameters.csv
Imported by report/build_report.py, which renders the same rows as a page of every report.
"""

import argparse
import csv
import json
from pathlib import Path

REFERENCE = Path(__file__).resolve().parent / "davey_reference.json"
RELATIVE_TOLERANCE = 1e-9


def dig(doc, path):
    """Value at a dotted path, or KeyError-free None when any step is missing."""
    if not path:
        return None, False
    node = doc
    for step in path.split("."):
        if not isinstance(node, dict) or step not in node:
            return None, False
        node = node[step]
    return node, True


def equal(run_value, book_value):
    """Numeric comparison is relative; lists compare elementwise; everything else exactly."""
    if isinstance(book_value, (int, float)) and not isinstance(book_value, bool):
        if not isinstance(run_value, (int, float)) or isinstance(run_value, bool):
            return False
        scale = max(abs(book_value), abs(run_value), 1e-300)
        return abs(run_value - book_value) / scale <= RELATIVE_TOLERANCE
    if isinstance(book_value, list):
        return (isinstance(run_value, list) and len(run_value) == len(book_value)
                and all(equal(a, b) for a, b in zip(run_value, book_value)))
    return run_value == book_value


def show(value):
    if value is None:
        return "-"
    if isinstance(value, list):
        return "[" + ", ".join(show(v) for v in value) + "]"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def observation_sigmas(run_json: dict) -> dict[str, dict[float, int]]:
    """Measurement standard deviations actually used, per column, as {value: epoch count}.

    BTO and BFO sigmas are per epoch, not per run, so they live in the observations file rather
    than in the manifest. Reading them here is what keeps them in the table instead of leaving
    the column blank: it is the one place the assumed measurement error can be checked against
    the published one, and the R600 sigma is a known departure.
    """
    recorded = dig(run_json, "config.inputs.observations")[0]
    if not recorded:
        return {}
    path = (REFERENCE.parent.parent / recorded).resolve()
    if not path.is_file():
        return {}
    counts: dict[str, dict[float, int]] = {}
    with path.open() as f:
        for row in csv.DictReader(f):
            for column in ("bto_sd_us", "bfo_sd_hz"):
                text = (row.get(column) or "").strip()
                if text:
                    counts.setdefault(column, {})
                    counts[column][float(text)] = counts[column].get(float(text), 0) + 1
    return counts


def compare(run_json: dict, reference: dict | None = None) -> list[dict]:
    """One row per reference entry: the run's value, the book's, and a verdict."""
    reference = reference or json.loads(REFERENCE.read_text())
    sigmas = observation_sigmas(run_json)
    rows = []
    for entry in reference["rows"]:
        value, found = dig(run_json, entry["path"])
        spec = entry.get("from_observations")
        if spec:
            # "<column>:<value>" — report how many epochs carry that sigma in this run.
            column, wanted = spec.split(":")
            wanted = float(wanted)
            n = sigmas.get(column, {}).get(wanted, 0)
            value, found = (f"{wanted:g} at {n} epoch{'s' if n != 1 else ''}" if n else "not used"), True
        if entry.get("compare") == "declared":
            # Prose or identifier: comparing the strings is not a verdict, so the reference
            # asserts the relationship and the note explains it.
            verdict = "same" if entry["status"] == "same" else "DIFFERS"
        elif not found:
            verdict = "n/a"
        elif equal(value, entry["book"]):
            verdict = "same"
        else:
            verdict = "DIFFERS"
        rows.append({"area": entry["area"], "parameter": entry["label"], "unit": entry.get("unit", ""),
                     "this_run": show(value) if found else "", "davey": show(entry["book"]),
                     "verdict": verdict, "citation": entry["cite"], "note": entry.get("note", "")})
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run", type=Path, help="run directory, e.g. runs/davey2016")
    parser.add_argument("--csv", action="store_true", help="also write <run>/parameters.csv")
    args = parser.parse_args()

    run_json = json.loads((args.run / "run.json").read_text())
    rows = compare(run_json)
    width = max(len(r["parameter"]) for r in rows)
    area = None
    for r in rows:
        if r["area"] != area:
            area = r["area"]
            print(f"\n{area}")
        mark = {"same": " ", "DIFFERS": "*", "n/a": "?"}[r["verdict"]]
        print(f" {mark} {r['parameter']:<{width}}  this run: {r['this_run'] or '-':<28} "
              f"Davey: {r['davey']:<28} [{r['citation']}]")
    differs = [r for r in rows if r["verdict"] == "DIFFERS"]
    print(f"\n{len(rows)} parameters: {sum(r['verdict'] == 'same' for r in rows)} same, "
          f"{len(differs)} differ, {sum(r['verdict'] == 'n/a' for r in rows)} not comparable at a "
          f"single manifest path (see the note column).")
    for r in differs:
        print(f"  * {r['parameter']}: {r['this_run']} vs Davey {r['davey']}")
    if args.csv:
        write_csv(args.run / "parameters.csv", rows)
        print(f"\n{args.run / 'parameters.csv'}")


if __name__ == "__main__":
    main()
