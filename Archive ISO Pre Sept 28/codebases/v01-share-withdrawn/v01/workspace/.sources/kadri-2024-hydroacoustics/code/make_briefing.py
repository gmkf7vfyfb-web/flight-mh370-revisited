#!/usr/bin/env python3
"""Assemble the concise Kadri discussion pack from reproducible plot outputs."""

from __future__ import annotations

import hashlib
import json
import re
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pymupdf
from matplotlib.backends.backend_pdf import PdfPages


HERE = Path(__file__).resolve().parents[1]
OUTPUT = HERE / "outputs"
BRIEFING_PATH = HERE / "kadri-discussion-briefing.md"
FIGURES = [
    "impact-pressure-by-station.png",
    "impact-family-transfer-density.png",
    "candidate-bearing-and-timing-overview.png",
    "subsecond-periodic-mask-comparison.png",
    "leave-one-shot-out-controls.png",
    "airgun-filter-mask-tradeoffs.png",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def page_with_image(pdf: PdfPages, filename: str, title: str, note: str) -> None:
    figure = plt.figure(figsize=(11.69, 8.27))
    axis = figure.add_axes([0.025, 0.075, 0.95, 0.84])
    axis.imshow(plt.imread(OUTPUT / filename))
    axis.axis("off")
    figure.suptitle(title, fontsize=15.2, y=0.965)
    figure.text(0.5, 0.025, note, ha="center", fontsize=8.4)
    pdf.savefig(figure)
    plt.close(figure)


def main() -> None:
    source = BRIEFING_PATH.read_text(encoding="utf-8")
    body = source.split("## Figures to share", 1)[0]
    paragraphs = [
        re.sub(r"\s+", " ", paragraph.strip())
        for paragraph in body.split("\n\n")[1:]
        if paragraph.strip()
    ]
    output_path = OUTPUT / "kadri-discussion-briefing.pdf"
    with PdfPages(
        output_path,
        metadata={"CreationDate": None, "ModDate": None, "Title": "Preliminary MH370 hydroacoustic work"},
    ) as pdf:
        figure = plt.figure(figsize=(8.27, 11.69))
        figure.text(0.07, 0.955, "Preliminary MH370 hydroacoustic work", fontsize=18.0, weight="bold")
        figure.text(0.07, 0.928, "Material for discussion with Dr Usama Kadri — 24 August 2026", fontsize=10.0, color="#555555")
        y = 0.885
        for paragraph in paragraphs:
            wrapped = textwrap.wrap(paragraph, width=102)
            figure.text(0.07, y, "\n".join(wrapped), fontsize=9.4, va="top", linespacing=1.22)
            y -= 0.021 * len(wrapped) + 0.018
        axis = figure.add_axes([0.06, 0.055, 0.88, 0.36])
        axis.imshow(plt.imread(OUTPUT / "impact-pressure-by-station.png"))
        axis.axis("off")
        figure.text(
            0.5, 0.025,
            "All results are preliminary and conditional; individual vector PDF figures remain the publication masters.",
            ha="center", fontsize=8.1,
        )
        pdf.savefig(figure)
        plt.close(figure)

        page_with_image(
            pdf, "impact-family-transfer-density.png",
            "Impact-to-SOFAR Monte Carlo sensitivity",
            "Families and coupling priors are explicit model alternatives; the curves are not an impact or detection posterior.",
        )
        page_with_image(
            pdf, "candidate-bearing-and-timing-overview.png",
            "Candidate bearings, arrival-difference bands and integrated spatial PDF",
            "Source signals and independently screened timing controls are separate categories; compatibility mass is not event probability.",
        )
        page_with_image(
            pdf, "subsecond-periodic-mask-comparison.png",
            "Diego Garcia ±100/±150 ms mask sensitivity",
            "The apparent result changes with mask centring, and both widths are below publication-rendering timing precision.",
        )

        figure = plt.figure(figsize=(8.27, 11.69))
        for bounds, filename, title in [
            ([0.04, 0.52, 0.92, 0.40], "leave-one-shot-out-controls.png", "Held-out airgun-cycle controls"),
            ([0.04, 0.055, 0.92, 0.40], "airgun-filter-mask-tradeoffs.png", "Filter and information-loss sensitivity"),
        ]:
            axis = figure.add_axes(bounds)
            axis.imshow(plt.imread(OUTPUT / filename))
            axis.axis("off")
            axis.set_title(title, fontsize=12.2, pad=5)
        figure.suptitle("Diego Garcia periodic-interference controls", fontsize=15.5, y=0.975)
        figure.text(
            0.5, 0.022,
            "An elevated residual is not a source classifier; raw triad channels are required for a defensible detector.",
            ha="center", fontsize=8.3,
        )
        pdf.savefig(figure)
        plt.close(figure)

    page_paths = []
    with pymupdf.open(output_path) as document:
        for page_number, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(dpi=180, alpha=False)
            page_path = OUTPUT / f"kadri-discussion-briefing-page-{page_number}.png"
            pixmap.save(page_path)
            page_paths.append(page_path)

    manifest = {
        "status": "REPRODUCIBLE_BRIEFING_FROM_SOURCE_TEXT_AND_PLOT_OUTPUTS",
        "inputs": {
            str(BRIEFING_PATH.relative_to(HERE)): sha256(BRIEFING_PATH),
            **{name: sha256(OUTPUT / name) for name in FIGURES},
        },
        "code": {str(Path(__file__).relative_to(HERE)): sha256(Path(__file__))},
        "output": {
            output_path.name: sha256(output_path),
            **{path.name: sha256(path) for path in page_paths},
        },
    }
    (OUTPUT / "briefing-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    for path in page_paths:
        print(path)


if __name__ == "__main__":
    main()
