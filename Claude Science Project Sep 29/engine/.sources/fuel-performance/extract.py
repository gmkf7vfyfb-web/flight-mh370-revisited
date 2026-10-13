#!/usr/bin/env python3
"""Extract the raw 777-200ER / Trent 892 performance tables from Ulich's fuel model workbook.

Usage: .venv/bin/python .sources/fuel-performance/extract.py [WORKBOOK] [OUTPUT]
  WORKBOOK  default /jackbox/home/MH370-inputs/fuel/ulich-9M-MRO-fuel-model-v5.6-public.xlsm
  OUTPUT    default data/fuel-tables.json (git-ignored; never commit or redistribute it)

Source: Ulich, 9M-MRO fuel model V5.6, public Google Drive copy
(https://drive.google.com/file/d/1Wt9DOU0Z53W7NERzSsK2sxcyrojmN7Sq). Its tables are transcribed
from Boeing Flight Planning and Performance Manuals, some marked confidential, so the values are
used locally only. Only the raw weight x flight-level grids are taken; the workbook's own fuel
flow model, endurance model and event calibration are not.

Each cell keeps the source class that Ulich marks by cell colour (each sheet's legend):
  fppm-open          green: open-source Boeing FPPM table
  fppm-confidential  yellow: Boeing FPPM from a confidential source (FF footnote: +/-3 % per
                     10 C TAT above/below standard; KTAS +/-1 kt per 1 C)
  fppm-optimum       light blue: Boeing data, shaded at the optimum flight level
  vmo-limit          orange: 325 KCAS (Vmo - 5 kt) substituted where LRC would exceed it
  filler             grey: Ulich's fillers near the data frontier (not Boeing data)
  unlabelled         a colour with no legend entry on that sheet
  derived            no FPPM source marked (e.g. the MRC and CI 52 grids, LRC Mach from W/delta)
Consumers should drop `filler` cells, and treat `derived` as Ulich's reconstruction.
"""

import hashlib
import json
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = Path("/jackbox/home/MH370-inputs/fuel/ulich-9M-MRO-fuel-model-v5.6-public.xlsm")
OUTPUT = ROOT / "data/fuel-tables.json"

# key: (sheet, quantity, units). Fuel flows are per engine, both engines running unless INOP.
TABLES = {
    "lrc_mach": ("LRC Mach", "mach", "Mach"),
    "lrc_kias": ("LRC KIAS", "kias", "kt"),
    "lrc_ff": ("LRC FF", "fuel_flow", "kg/h per engine"),
    "m084_kias": ("M0.84 KIAS", "kias", "kt"),
    "m084_ff": ("M0.84 FF", "fuel_flow", "kg/h per engine"),
    "holding_kias": ("Holding KIAS", "kias", "kt"),
    "holding_mach": ("Holding Mach", "mach", "Mach"),
    "holding_ff": ("Holding FF", "fuel_flow", "kg/h per engine, includes +5 % for a racetrack pattern"),
    "mrc_mach": ("MRC Mach", "mach", "Mach"),
    "mrc_ff": ("MRC FF", "fuel_flow", "kg/h per engine"),
    "ci52_mach": ("CI=52 Mach", "mach", "Mach"),
    "ci52_ff": ("CI=52 FF", "fuel_flow", "kg/h per engine"),
    "lrc_inop_mach": ("LRC INOP Mach", "mach", "Mach"),
    "lrc_inop_ff": ("LRC INOP FF", "fuel_flow", "kg/h, one engine inoperative"),
    "holding_inop_mach": ("Holding INOP Mach", "mach", "Mach"),
    "holding_inop_ff": ("Holding INOP FF", "fuel_flow", "kg/h, one engine inoperative, includes +5 % racetrack"),
}


def source_class(cell, sheet):
    fill = cell.fill
    if fill is None or not fill.fill_type:
        return "derived"
    colour = fill.fgColor
    if colour.type == "rgb":
        return {"FF99FF99": "fppm-open", "FFFFFF00": "fppm-confidential"}.get(colour.rgb, "derived")
    if colour.type == "theme":
        tint = round(colour.tint, 2)
        if colour.theme == 2 and tint < 0:
            return "filler"
        if colour.theme == 9 and tint < 0:
            return "vmo-limit" if sheet == "LRC KIAS" else "unlabelled"
        if colour.theme == 8:
            return "fppm-optimum"
    return "derived"


def blocks(fl_cells):
    """Split a header row into side-by-side blocks: a new block starts where the FL axis restarts."""
    out = [[fl_cells[0]]]
    for c in fl_cells[1:]:
        (out[-1].append(c) if c.value > out[-1][-1].value else out.append([c]))
    return out


def grid(ws, quantity):
    """The weight x flight-level block under the 'Flight Level (FL)' label.

    Some sheets hold two blocks side by side under one header ("Holding INOP Mach": KIAS at
    B3:L12, Mach at M3:W12). Taking every numeric header cell concatenated them into one table
    with a repeated FL axis. Now the block whose values match the sheet's quantity is taken
    (Mach below 2, KIAS above), and a sheet with several blocks and no such rule is an error."""
    rows = list(ws.iter_rows(max_row=40))
    label = next(c for r in rows for c in r if isinstance(c.value, str) and c.value.startswith("Flight Level"))
    header = next(r for r in rows[label.row:] if sum(isinstance(c.value, (int, float)) for c in r) >= 3)
    fl_cells = [c for c in header if isinstance(c.value, (int, float))]
    found = blocks(fl_cells)
    if len(found) > 1:
        def top(block):
            vals = [r[c.column - 1].value for r in rows[header[0].row:header[0].row + 30] for c in block]
            return max((v for v in vals if isinstance(v, (int, float))), default=float("nan"))
        rule = {"mach": lambda b: top(b) < 2.0, "kias": lambda b: top(b) > 2.0}.get(quantity)
        chosen = [b for b in found if rule and rule(b)]
        if len(chosen) != 1:
            raise SystemExit(f"{ws.title}: {len(found)} blocks under one header and no unique {quantity} block")
        fl_cells = chosen[0]
    weight_col = found[0][0].column - 2  # 0-based index of the column left of the first FL (first block)
    body = []
    for r in rows[header[0].row:]:
        w = r[weight_col].value
        if not isinstance(w, (int, float)):
            break
        body.append(r)
    fls = [float(c.value) for c in fl_cells]
    weights = [float(r[weight_col].value) for r in body]
    values = [[None] * len(fls) for _ in body]
    classes = [[None] * len(fls) for _ in body]
    for i, r in enumerate(body):
        for j, h in enumerate(fl_cells):
            c = r[h.column - 1]
            if isinstance(c.value, (int, float)):
                values[i][j] = float(c.value)
                classes[i][j] = source_class(c, ws.title)
    return fls, weights, values, classes


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else WORKBOOK
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    wb = openpyxl.load_workbook(src, data_only=True)
    tables = {}
    for key, (sheet, quantity, units) in TABLES.items():
        fls, weights, values, classes = grid(wb[sheet], quantity)
        tables[key] = {"sheet": sheet, "quantity": quantity, "units": units, "flight_levels": fls,
                       "weights_t": weights, "values": values, "source_class": classes}
        n = sum(v is not None for row in values for v in row)
        count = {k: sum(c == k for row in classes for c in row) for k in sorted({c for row in classes for c in row} - {None})}
        print(f"{key:18s} FL{fls[0]:.0f}-{fls[-1]:.0f} x {weights[0]:.0f}-{weights[-1]:.0f} t: {n} cells {count}")
    doc = {
        "source": {"file": src.name, "sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
                   "note": "Boeing-derived; local use only, never redistribute"},
        "tables": tables,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
