"""Write a variant observations file with altered measurement standard deviations.

BTO and BFO sigmas are per epoch, held in `data/satcom-observations.csv` beside each measurement,
because Davey assigns them by message type: 29 us for R1200, 43 us for an anomalous R1200, 62 us
for R600 (p. 40), and 7 Hz for BFO (sec. 5.3). Testing a different assumption therefore means a
different observations file, which a run selects with `[inputs] observations` — no code change,
and the run manifest records which file it used.

Davey names this knob himself in Assumption 2 (p. 73): the standard deviations are "provided to
the algorithm as a known input", and "minor inflation of the assumed BTO variance would lead to
incremental changes in the filter output".

Usage:
  python report/make_observation_variant.py OUT.csv --bfo-sd 4
  python report/make_observation_variant.py OUT.csv --bto-scale 2
  python report/make_observation_variant.py OUT.csv --bto-sd 43     # one sigma for every epoch
"""

import argparse
import csv
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "data/satcom-observations.csv"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--bto-sd", type=float, help="replace every BTO sigma with this value (us)")
    parser.add_argument("--bto-scale", type=float, help="multiply every BTO sigma by this factor")
    parser.add_argument("--bfo-sd", type=float, help="replace every BFO sigma with this value (Hz)")
    parser.add_argument("--bfo-scale", type=float, help="multiply every BFO sigma by this factor")
    args = parser.parse_args()
    if args.bto_sd and args.bto_scale:
        raise SystemExit("--bto-sd and --bto-scale are mutually exclusive")
    if args.bfo_sd and args.bfo_scale:
        raise SystemExit("--bfo-sd and --bfo-scale are mutually exclusive")

    with args.source.open() as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)

    changed = {"bto_sd_us": 0, "bfo_sd_hz": 0}
    for row in rows:
        for column, absolute, scale in (("bto_sd_us", args.bto_sd, args.bto_scale),
                                        ("bfo_sd_hz", args.bfo_sd, args.bfo_scale)):
            text = (row.get(column) or "").strip()
            if not text:
                continue  # an epoch with no measurement of that kind keeps its blank
            new = absolute if absolute is not None else (float(text) * scale if scale else None)
            if new is not None:
                row[column] = f"{new:.12f}".rstrip("0").rstrip(".")
                changed[column] += 1

    note = ("; measurement-error variant: "
            + ", ".join(filter(None, [
                f"BTO sigma set to {args.bto_sd} us" if args.bto_sd else None,
                f"BTO sigma x{args.bto_scale}" if args.bto_scale else None,
                f"BFO sigma set to {args.bfo_sd} Hz" if args.bfo_sd else None,
                f"BFO sigma x{args.bfo_scale}" if args.bfo_scale else None])))
    for row in rows:
        if "note" in row:
            row["note"] = (row.get("note") or "") + note

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output}: {changed['bto_sd_us']} BTO sigmas and "
          f"{changed['bfo_sd_hz']} BFO sigmas changed, from {args.source.name}")


if __name__ == "__main__":
    main()
