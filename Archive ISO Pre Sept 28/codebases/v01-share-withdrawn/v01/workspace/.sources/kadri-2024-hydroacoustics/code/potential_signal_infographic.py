#!/usr/bin/env python3
"""Create a traceable summary infographic of hydroacoustic signals of interest."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import textwrap
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
ARC_PATH = DATA / "seventh_arc_fl400.geojson"
PDF_PATH = DATA / "posterior_grids.npz"
PDF_KEY = "reference_power_marginalization__core"
CATALOGUE_PATH = OUTPUT / "noted-event-impact-time-catalogue.csv"
H08_WINDOWS_PATH = OUTPUT / "table-event-conditional-h08s-windows.csv"
PULSE_PATH = OUTPUT / "pulse-conditioned-acquisition-top10.csv"
OSCAR_AUDIT_PATH = OUTPUT / "oscar-near-0030-feature-audit.csv"
OSCAR_METRICS_PATH = OUTPUT / "oscar-boundary-audit-metrics.csv"
SOURCE_TARGETS_PATH = DATA / "acoustic-alignment-source-targets.csv"
BEARING_INTERSECTIONS_PATH = OUTPUT / "conditional-bearing-intersections.csv"
SUMMARY_CSV = OUTPUT / "potential-signals-summary.csv"
PNG_PATH = OUTPUT / "potential-signals-summary-infographic.png"
PDF_OUTPUT_PATH = OUTPUT / "potential-signals-summary-infographic.pdf"
MANIFEST_PATH = OUTPUT / "potential-signals-summary-infographic-manifest.json"

EARTH_RADIUS_KM = 6371.0088
H01W = (-34.892, 114.141)
PDF_METADATA = {"CreationDate": None, "ModDate": None}


@dataclass
class SignalRow:
    key: str
    label: str
    category: str
    cl_arrival: str
    dg_arrival: str
    impact_start_utc: str
    impact_end_utc: str
    arc_latitude: str
    integrated_pdf_hpd: str
    trace_assessment: str
    critical_limitation: str
    colour: str
    source_point_latitude_deg: float | None = None
    source_point_longitude_deg_e: float | None = None
    integrated_pdf_hpd_fraction: float | None = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def hhmmss(value: str, fractional: bool = False) -> str:
    parsed = parse_utc(value)
    if fractional:
        return parsed.strftime("%H:%M:%S.%f")[:-3]
    return parsed.strftime("%H:%M:%S")


def densify_polyline(coordinates: np.ndarray, maximum_step_deg: float = 0.002) -> np.ndarray:
    parts = []
    for start, end in zip(coordinates[:-1], coordinates[1:]):
        count = max(1, int(math.ceil(float(np.max(np.abs(end - start))) / maximum_step_deg)))
        fraction = np.arange(count, dtype=float) / count
        parts.append(start[None, :] + fraction[:, None] * (end - start)[None, :])
    parts.append(coordinates[-1:])
    return np.vstack(parts)


def haversine_km(
    latitude_deg: np.ndarray | float,
    longitude_deg: np.ndarray | float,
    origin: tuple[float, float],
) -> np.ndarray:
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg)
    origin_latitude, origin_longitude = np.radians(origin)
    value = (
        np.sin((latitude - origin_latitude) / 2.0) ** 2
        + np.cos(origin_latitude)
        * np.cos(latitude)
        * np.sin((longitude - origin_longitude) / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(value, 0.0, 1.0)))


def initial_bearing_deg(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    origin: tuple[float, float],
) -> np.ndarray:
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg)
    origin_latitude, origin_longitude = np.radians(origin)
    dlon = longitude - origin_longitude
    y = np.sin(dlon) * np.cos(latitude)
    x = (
        np.cos(origin_latitude) * np.sin(latitude)
        - np.sin(origin_latitude) * np.cos(latitude) * np.cos(dlon)
    )
    return np.degrees(np.arctan2(y, x)) % 360.0


def angular_difference_deg(first: np.ndarray, second: float) -> np.ndarray:
    return (first - second + 180.0) % 360.0 - 180.0


class SpatialContext:
    def __init__(self) -> None:
        arc_payload = json.loads(ARC_PATH.read_text(encoding="utf-8"))
        original_arc = np.asarray(
            arc_payload["features"][0]["geometry"]["coordinates"], dtype=float
        )
        self.arc = densify_polyline(original_arc)
        self.arc_bearing = initial_bearing_deg(self.arc[:, 1], self.arc[:, 0], H01W)
        with np.load(PDF_PATH) as payload:
            self.latitude = payload["latitude_deg"].copy()
            self.longitude = payload["longitude_deg_E"].copy()
            area = payload["cell_area_km2"].copy()
            probability = payload[PDF_KEY].copy()
        density = probability / area
        order = np.argsort(density.ravel())[::-1]
        cumulative = np.cumsum(probability.ravel()[order])
        self.hpd_fraction = np.empty_like(cumulative)
        self.hpd_fraction[order] = cumulative
        self.hpd_fraction = self.hpd_fraction.reshape(probability.shape)

    def bearing_arc_intersection(self, bearing_deg: float) -> tuple[float, float] | None:
        difference = np.abs(angular_difference_deg(self.arc_bearing, bearing_deg))
        index = int(np.argmin(difference))
        if difference[index] > 0.5:
            return None
        return float(self.arc[index, 1]), float(self.arc[index, 0])

    def nearest_arc(self, latitude_deg: float, longitude_deg_e: float) -> tuple[float, float]:
        distance = haversine_km(
            self.arc[:, 1], self.arc[:, 0], (latitude_deg, longitude_deg_e)
        )
        index = int(np.argmin(distance))
        return float(self.arc[index, 1]), float(distance[index])

    def hpd_at(self, latitude_deg: float, longitude_deg_e: float) -> float:
        latitude_index = int(np.argmin(np.abs(self.latitude - latitude_deg)))
        longitude_index = int(np.argmin(np.abs(self.longitude - longitude_deg_e)))
        return float(self.hpd_fraction[latitude_index, longitude_index])


def hpd_label(fraction: float | None) -> str:
    if fraction is None:
        return "Not localised"
    if fraction >= 0.999:
        return "Outside 99% HPD"
    return f"{100.0 * fraction:.0f}% HPD"


def build_rows() -> list[SignalRow]:
    spatial = SpatialContext()
    catalogue = {row["event_id"]: row for row in read_csv(CATALOGUE_PATH)}
    h08_windows = read_csv(H08_WINDOWS_PATH)
    broad_windows = {
        row["event_id"]: row for row in h08_windows if row["bearing_control"] == "broad_control"
    }
    pulse_rows = {int(row["rank"]): row for row in read_csv(PULSE_PATH)}
    oscar_audit = read_csv(OSCAR_AUDIT_PATH)
    oscar_metrics = {row["metric"]: row["value"] for row in read_csv(OSCAR_METRICS_PATH)}
    targets = {row["target_id"]: row for row in read_csv(SOURCE_TARGETS_PATH)}
    bearing_intersections = read_csv(BEARING_INTERSECTIONS_PATH)

    def event_impact(event_id: str) -> tuple[str, str]:
        event = catalogue[event_id]
        return hhmmss(event["implied_impact_q2p5_utc"]), hhmmss(
            event["implied_impact_q97p5_utc"]
        )

    def bearing_context(bearing: float) -> tuple[str, float | None, float | None, float | None]:
        intersection = spatial.bearing_arc_intersection(bearing)
        if intersection is None:
            return "No southern intersection", None, None, None
        latitude, longitude = intersection
        hpd = spatial.hpd_at(latitude, longitude)
        return f"{abs(latitude):.2f}°S · on arc", latitude, longitude, hpd

    def source_context(latitude: float, longitude: float) -> tuple[str, float]:
        arc_latitude, offset_km = spatial.nearest_arc(latitude, longitude)
        return f"{abs(arc_latitude):.2f}°S · {offset_km:.0f} km off", spatial.hpd_at(
            latitude, longitude
        )

    rows: list[SignalRow] = []
    for key, label, bearing, colour in (
        ("kadri_table_004958", "A · Kadri Table 1\n00:49:58", 260.41, "#7C8DA5"),
        ("kadri_table_005331", "B · Kadri Table 1\n00:53:31", 257.58, "#627E9A"),
    ):
        event = catalogue[key]
        window = broad_windows[key.replace("kadri_table_", "event_")]
        arc_text, latitude, longitude, hpd = bearing_context(bearing)
        impact_start, impact_end = event_impact(key)
        rows.append(
            SignalRow(
                key=key,
                label=label,
                category="Kadri catalogue only",
                cl_arrival=f"{hhmmss(event['arrival_utc'])}\n{bearing:.2f}° bearing",
                dg_arrival=(
                    f"Predicted {hhmmss(window['h08s_arrival_q2p5_utc'])}–"
                    f"{hhmmss(window['h08s_arrival_q97p5_utc'])}"
                ),
                impact_start_utc=impact_start,
                impact_end_utc=impact_end,
                arc_latitude=arc_text,
                integrated_pdf_hpd=hpd_label(hpd),
                trace_assessment="No corresponding peak recovered from the published H01W trace.",
                critical_limitation="Entry exists in Table 1; conditional DG window is not a detected counterpart.",
                colour=colour,
                source_point_latitude_deg=latitude,
                source_point_longitude_deg_e=longitude,
                integrated_pdf_hpd_fraction=hpd,
            )
        )

    event = catalogue["screened_h01_005204"]
    impact_start, impact_end = event_impact("screened_h01_005204")
    rows.append(
        SignalRow(
            key="figure9_rectangle_1_cluster",
            label="C · Figure 9 rectangle 1\n00:52 cluster",
            category="Visible H01W feature",
            cl_arrival="00:52:00 reported\n00:52:04.35 q99 peak",
            dg_arrival="None reported\n01:10:00.50 is post hoc",
            impact_start_utc=impact_start,
            impact_end_utc=impact_end,
            arc_latitude="No southern intersection",
            integrated_pdf_hpd="n/a · bearing misses arc",
            trace_assessment="Strong H01W local-energy feature is visible near the published rectangle.",
            critical_limitation="Reported 57° bearing is incompatible with the southern arc and the OSCAR direction.",
            colour="#2A8C9D",
        )
    )

    event = catalogue["figure9_rectangle_2"]
    impact_start, impact_end = event_impact("figure9_rectangle_2")
    preferred_intersection = next(
        row
        for row in bearing_intersections
        if row["event_id"] == "figure9_rectangle_2"
        and row["status"].startswith("SOURCE_REPORTED_SEVENTH_ARC_DISTANCE")
    )
    latitude = float(preferred_intersection["conditional_latitude_deg"])
    longitude = float(preferred_intersection["conditional_longitude_deg_e"])
    hpd = spatial.hpd_at(latitude, longitude)
    arc_text = f"{abs(latitude):.2f}°S · on arc"
    rows.append(
        SignalRow(
            key="figure9_rectangle_2",
            label="D · Kadri preferred\n00:54:30 / 306.18°",
            category="Published preferred candidate",
            cl_arrival="00:54:30 reported\nlocal score below q99",
            dg_arrival="No identified counterpart\n01:12:29–49 is periodic",
            impact_start_utc=impact_start,
            impact_end_utc=impact_end,
            arc_latitude=arc_text,
            integrated_pdf_hpd=hpd_label(hpd),
            trace_assessment="Kadri-labelled feature; our local-energy screen does not exceed panel q99.",
            critical_limitation="Bearing intersects far north of the independent high-density region.",
            colour="#B8903F",
            source_point_latitude_deg=latitude,
            source_point_longitude_deg_e=longitude,
            integrated_pdf_hpd_fraction=hpd,
        )
    )

    oscar_h01 = next(row for row in oscar_audit if row["arrival_utc"].endswith("00:52:04.350Z"))
    oscar_h08 = next(row for row in oscar_audit if row["arrival_utc"].endswith("01:10:00.500Z"))
    oscar_target = targets["oscar_v2_final_mode"]
    oscar_latitude = float(oscar_target["latitude_deg"])
    oscar_longitude = float(oscar_target["longitude_deg_e"])
    arc_text, hpd = source_context(oscar_latitude, oscar_longitude)
    rows.append(
        SignalRow(
            key="oscar_boundary_pair",
            label="E · OSCAR timing pair\npost hoc boundary audit",
            category="Exploratory two-station pair",
            cl_arrival=hhmmss(oscar_h01["arrival_utc"], fractional=True),
            dg_arrival=hhmmss(oscar_h08["arrival_utc"], fractional=True),
            impact_start_utc=hhmmss(oscar_h08["implied_source_utc"], fractional=True),
            impact_end_utc=hhmmss(oscar_h01["implied_source_utc"], fractional=True),
            arc_latitude=arc_text,
            integrated_pdf_hpd=hpd_label(hpd),
            trace_assessment="Strong CL feature plus a cropped DG panel-boundary segment.",
            critical_limitation=(
                f"DG segment lies in the airgun cadence; matched-window p="
                f"{float(oscar_metrics['matched_ten_second_window_p']):.3f}."
            ),
            colour="#6757A5",
            source_point_latitude_deg=oscar_latitude,
            source_point_longitude_deg_e=oscar_longitude,
            integrated_pdf_hpd_fraction=hpd,
        )
    )

    pulse = pulse_rows[3]
    pulse_latitude = float(pulse["latitude_deg"])
    pulse_longitude = float(pulse["longitude_deg_e"])
    arc_text, hpd = source_context(pulse_latitude, pulse_longitude)
    source_time = hhmmss(pulse["primary_source_utc"], fractional=True)
    rows.append(
        SignalRow(
            key="late_periodic_pair",
            label="F · 00:54:27 / 01:12:49\nfull-grid timing pair",
            category="Exploratory two-station pair",
            cl_arrival=hhmmss(pulse["h01_arrival_utc"], fractional=True),
            dg_arrival=hhmmss(pulse["h08_arrival_utc"], fractional=True),
            impact_start_utc=source_time,
            impact_end_utc=source_time,
            arc_latitude=arc_text,
            integrated_pdf_hpd=hpd_label(hpd),
            trace_assessment="Spatially compatible timing pair; DG cycle is among the pulse-tail leaders.",
            critical_limitation="Complete pulse/time-slide search p=1.000; not an association.",
            colour="#8A5CA8",
            source_point_latitude_deg=pulse_latitude,
            source_point_longitude_deg_e=pulse_longitude,
            integrated_pdf_hpd_fraction=hpd,
        )
    )

    event = catalogue["screened_h08_010313"]
    impact_start, impact_end = event_impact("screened_h08_010313")
    rows.append(
        SignalRow(
            key="screened_h08_010313",
            label="G · DG-only screen\n01:03:13",
            category="Periodic DG context",
            cl_arrival="No selected CL counterpart",
            dg_arrival="01:03:13.15\nrank-8 residual < q99",
            impact_start_utc=impact_start,
            impact_end_utc=impact_end,
            arc_latitude="Not localised",
            integrated_pdf_hpd="Not localised",
            trace_assessment="Elevated plotted segment, but not q99 after the control-selected filter.",
            critical_limitation="Inside the approximately 9.93-second periodic airgun train.",
            colour="#C46A47",
        )
    )
    return rows


def write_summary(rows: list[SignalRow]) -> None:
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(asdict(rows[0]))
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def wrapped(value: str, width: int) -> str:
    return "\n".join(
        "\n".join(textwrap.wrap(part, width=width, break_long_words=False))
        for part in value.splitlines()
    )


def rounded_box(axis, x, y, width, height, colour, radius=0.008, alpha=1.0, edge=None):
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=colour,
        edgecolor=edge or colour,
        linewidth=1.0,
        alpha=alpha,
        transform=axis.transAxes,
    )
    axis.add_patch(patch)
    return patch


def draw_infographic(rows: list[SignalRow]) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
        }
    )
    fig = plt.figure(figsize=(24, 15), facecolor="#F5F6F8")
    axis = fig.add_axes([0, 0, 1, 1])
    axis.set_axis_off()

    navy = "#102A43"
    muted = "#52667A"
    pale = "#E8EDF3"
    grid = "#CDD6E0"
    axis.add_patch(Rectangle((0, 0.915), 1, 0.085, transform=axis.transAxes, color=navy))
    axis.text(
        0.025,
        0.967,
        "MH370 hydroacoustics · potential signals of interest",
        transform=axis.transAxes,
        color="white",
        fontsize=29,
        fontweight="bold",
        va="center",
    )
    axis.text(
        0.025,
        0.932,
        "Cape Leeuwin (CL/H01W), Diego Garcia (DG/H08S), implied impact time and independent spatial-PDF compatibility",
        transform=axis.transAxes,
        color="#D9E7F3",
        fontsize=13,
        va="center",
    )

    chips = [
        ("0", "two-station associations survive\ncomplete-search correction", "#C84C4C"),
        ("2", "Kadri Table 1 bearings cross\nindependent PDF support", "#3F739B"),
        ("All", "DG features remain\nperiodic-airgun confounded", "#C46A47"),
    ]
    chip_x = [0.025, 0.35, 0.675]
    for x, (number, label, colour) in zip(chip_x, chips):
        rounded_box(axis, x, 0.838, 0.30, 0.058, "white", edge="#D8E0E8")
        rounded_box(axis, x + 0.010, 0.849, 0.058, 0.036, colour, radius=0.012)
        axis.text(
            x + 0.039,
            0.867,
            number,
            transform=axis.transAxes,
            color="white",
            fontsize=18,
            fontweight="bold",
            ha="center",
            va="center",
        )
        axis.text(
            x + 0.080,
            0.867,
            label,
            transform=axis.transAxes,
            color=navy,
            fontsize=11.2,
            fontweight="bold",
            va="center",
        )

    # Impact-time overview.
    rounded_box(axis, 0.025, 0.687, 0.95, 0.128, "white", edge="#D8E0E8")
    axis.text(
        0.04,
        0.795,
        "Implied impact/source time after the final SATCOM exchange",
        transform=axis.transAxes,
        color=navy,
        fontsize=13,
        fontweight="bold",
        va="center",
    )
    timeline_left, timeline_right = 0.145, 0.955
    timeline_top, timeline_bottom = 0.772, 0.705
    start_minute, end_minute = 19.0, 35.0
    for minute in (19, 23, 27, 31, 35):
        x = timeline_left + (minute - start_minute) / (end_minute - start_minute) * (
            timeline_right - timeline_left
        )
        axis.plot([x, x], [timeline_bottom, timeline_top], transform=axis.transAxes, color=grid, lw=0.8)
        axis.text(
            x,
            timeline_top + 0.006,
            f"00:{minute:02d}",
            transform=axis.transAxes,
            color=muted,
            fontsize=8.5,
            ha="center",
            va="bottom",
        )
    for index, row in enumerate(rows):
        y = timeline_top - 0.010 - index * 0.0092
        axis.text(0.125, y, row.label[0], transform=axis.transAxes, color=row.colour, fontsize=8.2, fontweight="bold", ha="right", va="center")
        begin = parse_utc(f"2014-03-08T{row.impact_start_utc}Z")
        finish = parse_utc(f"2014-03-08T{row.impact_end_utc}Z")
        begin_minute = begin.minute + begin.second / 60.0 + begin.microsecond / 60e6
        finish_minute = finish.minute + finish.second / 60.0 + finish.microsecond / 60e6
        x0 = timeline_left + (begin_minute - start_minute) / (end_minute - start_minute) * (
            timeline_right - timeline_left
        )
        x1 = timeline_left + (finish_minute - start_minute) / (end_minute - start_minute) * (
            timeline_right - timeline_left
        )
        x0, x1 = max(timeline_left, x0), min(timeline_right, x1)
        if x1 - x0 < 0.004:
            axis.plot([x0], [y], marker="o", ms=5.0, color=row.colour, transform=axis.transAxes)
        else:
            rounded_box(axis, x0, y - 0.0028, x1 - x0, 0.0056, row.colour, radius=0.003)

    # Main comparison table.
    columns = [
        (0.025, 0.160, "Candidate / status"),
        (0.185, 0.115, "CL / H01W arrival"),
        (0.300, 0.135, "DG / H08S arrival"),
        (0.435, 0.105, "Implied impact UTC"),
        (0.540, 0.115, "7th-arc latitude"),
        (0.655, 0.100, "Independent PDF HPD"),
        (0.755, 0.220, "What the traces show · critical limitation"),
    ]
    header_top, header_height = 0.665, 0.036
    axis.add_patch(
        Rectangle((0.025, header_top - header_height), 0.95, header_height, transform=axis.transAxes, color=navy)
    )
    for x, width, title in columns:
        axis.text(
            x + 0.008,
            header_top - header_height / 2,
            title,
            transform=axis.transAxes,
            color="white",
            fontsize=10.2,
            fontweight="bold",
            va="center",
        )

    row_top = header_top - header_height
    row_height = 0.069
    for index, row in enumerate(rows):
        top = row_top - index * row_height
        bottom = top - row_height
        background = "#FFFFFF" if index % 2 == 0 else "#F0F3F6"
        axis.add_patch(
            Rectangle((0.025, bottom), 0.95, row_height, transform=axis.transAxes, color=background)
        )
        axis.add_patch(
            Rectangle((0.025, bottom), 0.006, row_height, transform=axis.transAxes, color=row.colour)
        )
        for x, _, _ in columns[1:]:
            axis.plot([x, x], [bottom, top], transform=axis.transAxes, color=grid, lw=0.6)

        axis.text(
            0.040,
            top - 0.014,
            row.label,
            transform=axis.transAxes,
            color=navy,
            fontsize=9.2,
            fontweight="bold",
            va="top",
        )
        rounded_box(axis, 0.040, bottom + 0.008, 0.130, 0.015, pale, radius=0.005)
        axis.text(
            0.105,
            bottom + 0.0155,
            row.category,
            transform=axis.transAxes,
            color=muted,
            fontsize=7.5,
            fontweight="bold",
            ha="center",
            va="center",
        )

        body_cells = [
            (0.193, wrapped(row.cl_arrival, 21), 8.7),
            (0.308, wrapped(row.dg_arrival, 24), 8.5),
            (
                0.443,
                row.impact_start_utc
                if row.impact_start_utc == row.impact_end_utc
                else f"{row.impact_start_utc}\n– {row.impact_end_utc}",
                8.8,
            ),
            (0.548, wrapped(row.arc_latitude, 18), 8.7),
            (0.663, row.integrated_pdf_hpd, 9.0),
            (
                0.763,
                wrapped(f"{row.trace_assessment}  {row.critical_limitation}", 48),
                8.0,
            ),
        ]
        for x, content, font_size in body_cells:
            axis.text(
                x,
                top - 0.011,
                content,
                transform=axis.transAxes,
                color="#263746",
                fontsize=font_size,
                va="top",
                linespacing=1.18,
            )

    # Conclusions and definitions.
    rounded_box(axis, 0.025, 0.032, 0.455, 0.095, "#E7F1F4", edge="#AFCED5")
    axis.text(
        0.042,
        0.108,
        "Broad conclusion",
        transform=axis.transAxes,
        color="#1F6170",
        fontsize=12.5,
        fontweight="bold",
        va="center",
    )
    axis.text(
        0.042,
        0.086,
        wrapped(
            "The 00:49:58 and 00:53:31 bearings are spatially interesting, and the 00:52/00:54 timing clusters contain visible energy. However, no CL–DG pairing survives trials correction; all plausible DG counterparts remain embedded in the measured periodic train.",
            94,
        ),
        transform=axis.transAxes,
        color="#24434B",
        fontsize=9.4,
        va="top",
        linespacing=1.30,
    )
    rounded_box(axis, 0.495, 0.032, 0.480, 0.095, "#FFF5DF", edge="#E4C98F")
    axis.text(
        0.512,
        0.108,
        "How to read the numbers",
        transform=axis.transAxes,
        color="#7A5B1F",
        fontsize=12.5,
        fontweight="bold",
        va="center",
    )
    axis.text(
        0.512,
        0.086,
        wrapped(
            "Arrival-to-impact intervals use the independent integrated spatial PDF and 1.43–1.57 km s⁻¹ celerity. HPD is evaluated at the bearing–arc intersection or representative timing-source point; a lower percentile means higher density. Timing-derived points and bearing-derived points are conditional alternatives, not a fused location.",
            98,
        ),
        transform=axis.transAxes,
        color="#5C4821",
        fontsize=9.1,
        va="top",
        linespacing=1.30,
    )
    axis.text(
        0.025,
        0.014,
        "Inputs: Kadri (2024) Figure 9/Table 1; extracted publication vectors; independent archived integrated PDF; current complete-search controls. Publication traces are already filtered and are not raw CTBTO triad data.",
        transform=axis.transAxes,
        color=muted,
        fontsize=8.1,
        va="center",
    )

    fig.savefig(PNG_PATH, dpi=200, facecolor=fig.get_facecolor(), bbox_inches=None)
    fig.savefig(PDF_OUTPUT_PATH, metadata=PDF_METADATA, facecolor=fig.get_facecolor(), bbox_inches=None)
    plt.close(fig)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    write_summary(rows)
    draw_infographic(rows)
    inputs = [
        ARC_PATH,
        PDF_PATH,
        CATALOGUE_PATH,
        H08_WINDOWS_PATH,
        PULSE_PATH,
        OSCAR_AUDIT_PATH,
        OSCAR_METRICS_PATH,
        SOURCE_TARGETS_PATH,
        BEARING_INTERSECTIONS_PATH,
        Path(__file__),
    ]
    manifest = {
        "status": "SUMMARY_INFOGRAPHIC_NOT_EVENT_ASSOCIATION_OR_HYDROACOUSTIC_LIKELIHOOD",
        "inputs": {str(path.relative_to(HERE)): sha256(path) for path in inputs},
        "outputs": {
            str(path.relative_to(HERE)): sha256(path)
            for path in (SUMMARY_CSV, PNG_PATH, PDF_OUTPUT_PATH)
        },
        "row_count": len(rows),
        "spatial_pdf": "archived independent integrated PDF; not updated by hydroacoustics",
        "notes": [
            "CL means Cape Leeuwin H01W and DG means Diego Garcia H08S",
            "bearing-derived arc intersections and timing-derived source representatives are conditional alternatives",
            "publication traces are already filtered single plotted paths rather than raw CTBTO triad channels",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
