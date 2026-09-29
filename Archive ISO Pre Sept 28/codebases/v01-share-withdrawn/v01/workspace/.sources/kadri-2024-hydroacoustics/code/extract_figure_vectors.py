#!/usr/bin/env python3
"""Extract Kadri publication figures and exact Figure 9 PDF-vector traces.

The CSV traces are digitised publication objects, not CTBTO waveform samples.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "paper.pdf"
POSTER = ROOT / "paper" / "reference-poster.pdf"
DEST = ROOT / "data" / "kadri-figure-extraction"
FIGURES = DEST / "published-figures"
TRACES = DEST / "figure9-vector-traces"

ORANGE = (0.8510000109672546, 0.32499998807907104, 0.09799999743700027)
FIGURE9_PANELS = [
    {"panel": "a", "station": "H01W", "start_utc": "2014-03-08T00:27:00Z", "axes": [361.212, 61.067, 544.836, 126.376], "pressure_min_pa": -1.0, "pressure_max_pa": 1.0},
    {"panel": "b", "station": "H01W", "start_utc": "2014-03-08T00:37:00Z", "axes": [361.212, 165.567, 544.836, 230.876], "pressure_min_pa": -1.0, "pressure_max_pa": 1.0},
    {"panel": "c", "station": "H01W", "start_utc": "2014-03-08T00:47:00Z", "axes": [361.212, 268.197, 544.836, 333.506], "pressure_min_pa": -1.0, "pressure_max_pa": 1.0},
    {"panel": "d", "station": "H08S", "start_utc": "2014-03-08T01:00:00Z", "axes": [360.588, 372.067, 544.836, 437.376], "pressure_min_pa": -2.0, "pressure_max_pa": 2.0},
    {"panel": "e", "station": "H08S", "start_utc": "2014-03-08T01:10:00Z", "axes": [361.833, 479.047, 544.836, 544.356], "pressure_min_pa": -4.0, "pressure_max_pa": 4.0},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def close_colour(left, right, tolerance=2e-3) -> bool:
    return left is not None and all(abs(float(a) - float(b)) <= tolerance for a, b in zip(left, right))


def save_embedded(document, xref: int, name: str) -> dict:
    extracted = document.extract_image(xref)
    path = FIGURES / f"{name}.{extracted['ext']}"
    path.write_bytes(extracted["image"])
    return {
        "file": str(path.relative_to(DEST)),
        "method": "lossless embedded-image extraction",
        "xref": xref,
        "width_px": extracted["width"],
        "height_px": extracted["height"],
        "sha256": sha256(path),
    }


def save_render(document, page_index: int, clip, name: str, scale: float = 5.0) -> dict:
    page = document[page_index]
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=pymupdf.Rect(*clip), alpha=False)
    path = FIGURES / f"{name}.png"
    pixmap.save(path)
    return {
        "file": str(path.relative_to(DEST)),
        "method": "PDF vector/raster composite render",
        "page": page_index + 1,
        "clip_pdf_points": clip,
        "scale_px_per_pdf_point": scale,
        "width_px": pixmap.width,
        "height_px": pixmap.height,
        "sha256": sha256(path),
    }


def vector_points(page, axes) -> tuple[list[tuple[float, float]], list[int]]:
    x0, y0, x1, y1 = axes
    selected = []
    drawing_indices = []
    for index, drawing in enumerate(page.get_drawings()):
        rect = drawing["rect"]
        if not close_colour(drawing.get("color"), ORANGE):
            continue
        if rect.x1 < x0 or rect.x0 > x1 or rect.y1 < y0 or rect.y0 > y1:
            continue
        line_items = [item for item in drawing["items"] if item[0] == "l"]
        if len(line_items) < 100:
            continue
        drawing_indices.append(index)
        points = [(float(item[1].x), float(item[1].y)) for item in line_items]
        points.append((float(line_items[-1][2].x), float(line_items[-1][2].y)))
        selected.extend(points)
    selected.sort(key=lambda point: point[0])
    deduplicated = []
    for point in selected:
        if not deduplicated or point != deduplicated[-1]:
            deduplicated.append(point)
    return deduplicated, drawing_indices


def extract_figure9_traces(document) -> list[dict]:
    page = document[8]
    records = []
    for panel in FIGURE9_PANELS:
        x0, y0, x1, y1 = panel["axes"]
        points, drawing_indices = vector_points(page, panel["axes"])
        if len(points) < 1000:
            raise RuntimeError(f"too few vector points in Figure 9 panel {panel['panel']}: {len(points)}")
        start = datetime.fromisoformat(panel["start_utc"].replace("Z", "+00:00"))
        path = TRACES / f"kadri-2024-figure9-panel-{panel['panel']}-{panel['station']}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["plotted_time_s", "utc", "pressure_pa", "pdf_x_pt", "pdf_y_pt"])
            for x, y in points:
                plotted_time_s = 600.0 * (x - x0) / (x1 - x0)
                pressure = panel["pressure_max_pa"] - (y - y0) / (y1 - y0) * (
                    panel["pressure_max_pa"] - panel["pressure_min_pa"]
                )
                utc = start + timedelta(seconds=plotted_time_s)
                writer.writerow([
                    f"{plotted_time_s:.9f}",
                    utc.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                    f"{pressure:.9f}",
                    f"{x:.6f}",
                    f"{y:.6f}",
                ])
        seconds_per_point = 600.0 / (x1 - x0)
        pa_per_point = (panel["pressure_max_pa"] - panel["pressure_min_pa"]) / (y1 - y0)
        records.append({
            **panel,
            "file": str(path.relative_to(DEST)),
            "drawing_indices_zero_based": drawing_indices,
            "point_count": len(points),
            "sha256": sha256(path),
            "coordinate_quantisation_note": "PDF vector vertices exported directly; half the plotted 0.311 pt linewidth corresponds to the indicative coordinate uncertainties below",
            "indicative_half_linewidth_time_s": 0.5 * 0.311 * seconds_per_point,
            "indicative_half_linewidth_pressure_pa": 0.5 * 0.311 * pa_per_point,
        })
    return records


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TRACES.mkdir(parents=True, exist_ok=True)
    paper = pymupdf.open(PAPER)
    poster = pymupdf.open(POSTER)
    catalogue = []
    for figure, page, xref, description in [
        (4, 4, 81, "F-35A; Yemenia 626; Sriwijaya 182"),
        (5, 5, 98, "Air France 447; Transair 810; Lion Air 904"),
        (6, 6, 118, "AB Aviation 1103; AirAsia 8501; Asiana 991"),
        (8, 8, 196, "ARA San Juan calibration grenade at H03S/H04S/H10N"),
    ]:
        item = save_embedded(paper, xref, f"kadri-2024-figure{figure}")
        catalogue.append({"source": PAPER.name, "figure": figure, "page": page, "description": description, **item})
    for figure, page_index, clip, description in [
        (7, 6, [155.906, 50.500, 515.906, 424.927], "ARA San Juan explosion at H03S/H04S/H10N"),
        (9, 8, [71.505, 50.499, 554.173, 566.131], "MH370-window H01W/H08S panels"),
    ]:
        item = save_render(paper, page_index, clip, f"kadri-2024-figure{figure}")
        catalogue.append({"source": PAPER.name, "figure": figure, "page": page_index + 1, "description": description, **item})
    for page_index in (1, 2, 3, 4):
        page = poster[page_index]
        item = save_render(poster, page_index, list(page.rect), f"kadri-2025-poster-page{page_index + 1}", scale=3.0)
        catalogue.append({"source": POSTER.name, "figure": f"poster-page-{page_index + 1}", "page": page_index + 1, "description": "poster results/methods page", **item})

    trace_records = extract_figure9_traces(paper)
    metadata = {
        "status": "EXTRACTED_PUBLICATION_FIGURES_AND_DIGITISED_PLOT_VECTORS",
        "warning": "These are publication figures and plot vertices, not raw CTBTO waveforms. Processing, filtering, decimation, plotting and array-element selection cannot be reconstructed from the figures alone.",
        "sources": {
            PAPER.name: {"sha256": sha256(PAPER), "doi": "10.1038/s41598-024-60529-1"},
            POSTER.name: {"sha256": sha256(POSTER)},
        },
        "axis_calibration": "Figure 9 x axes and station/start times were OCR-checked against the rendered source at 5x. The plotted x range is 0–10 min. Pressure ticks are plotted as 10^6 microPa, converted to Pa; panels a–c span -1 to +1 Pa, d spans -2 to +2 Pa, and e spans -4 to +4 Pa.",
        "figure_catalogue": catalogue,
        "figure9_vector_traces": trace_records,
    }
    (DEST / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

