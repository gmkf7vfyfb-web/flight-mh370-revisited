#!/usr/bin/env python3
"""Deterministic self-contained HTML report renderer."""

from __future__ import annotations

from html import escape
from typing import Any


def number(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}"


def acars_error_chart(intervals: list[dict[str, Any]]) -> str:
    width, height = 760, 250
    left, right, top, bottom = 86, 28, 24, 42
    plot_width = width - left - right
    plot_height = height - top - bottom
    limit = 180.0
    zero = left + plot_width / 2
    scale = (plot_width / 2) / limit
    rows = []
    for index, row in enumerate(intervals):
        value = row["error_predicted_minus_observed_kg"]
        y = top + (index + 0.5) * plot_height / len(intervals)
        x = zero if value >= 0 else zero + value * scale
        bar_width = abs(value) * scale
        color = "#de6b48" if value >= 0 else "#2d7f82"
        label_x = zero + value * scale + (8 if value >= 0 else -8)
        anchor = "start" if value >= 0 else "end"
        rows.append(
            f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end">{index + 1}</text>'
            f'<rect x="{x:.1f}" y="{y - 10:.1f}" width="{bar_width:.1f}" height="20" rx="3" fill="{color}"/>'
            f'<text x="{label_x:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}" class="value">{value:+.1f}</text>'
        )
    ticks = []
    for tick in (-180, -90, 0, 90, 180):
        x = zero + tick * scale
        ticks.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height-bottom}" class="grid"/>'
            f'<text x="{x:.1f}" y="{height-16}" text-anchor="middle">{tick:+d}</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="ACARS interval prediction errors in kilograms">'
        '<style>text{font:12px system-ui;fill:#344054}.value{font-weight:650}.grid{stroke:#d6dce5;stroke-width:1}.axis{stroke:#667085;stroke-width:1.5}</style>'
        + "".join(ticks)
        + f'<line x1="{zero:.1f}" y1="{top}" x2="{zero:.1f}" y2="{height-bottom}" class="axis"/>'
        + "".join(rows)
        + f'<text x="{left + plot_width/2:.1f}" y="{height-1}" text-anchor="middle">predicted − observed burn (kg)</text>'
        + '</svg>'
    )


def post_chart(post: dict[str, Any], seconds_per_hour: float) -> str:
    width, height = 760, 300
    left, right, top, bottom = 76, 30, 24, 48
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_x = post["printed_duration_s"] / seconds_per_hour
    min_y, max_y = 28000.0, 44500.0

    def point(x: float, y: float) -> tuple[float, float]:
        return (
            left + x / max_x * plot_width,
            top + (max_y - y) / (max_y - min_y) * plot_height,
        )

    official = [(0.0, 43800.0)] + [
        (row["elapsed_s"] / seconds_per_hour, row["official_ending_fuel_kg"])
        for row in post["segments"]
    ]
    proxy = [(0.0, 43800.0)] + [
        (row["elapsed_s"] / seconds_per_hour, row["predicted_ending_fuel_kg"])
        for row in post["segments"]
    ]

    def polyline(values: list[tuple[float, float]], color: str) -> str:
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(*item) for item in values))
        circles = "".join(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>'
            for x, y in (point(*item) for item in values)
        )
        return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="3"/>{circles}'

    grid = []
    for y_value in (30000, 35000, 40000):
        _, y = point(0, y_value)
        grid.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="grid"/>'
            f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end">{y_value/1000:.0f}t</text>'
        )
    for x_value in (0.0, 0.5, 1.0, max_x):
        x, _ = point(x_value, min_y)
        grid.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height-bottom}" class="grid"/>'
            f'<text x="{x:.1f}" y="{height-20}" text-anchor="middle">{x_value:.2g} h</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Official and proxy post-ACARS ending fuel">'
        '<style>text{font:12px system-ui;fill:#344054}.grid{stroke:#e0e5ec;stroke-width:1}</style>'
        + "".join(grid)
        + polyline(official, "#3a6ea5")
        + polyline(proxy, "#c6533f")
        + '<g transform="translate(470 25)"><line x1="0" y1="0" x2="28" y2="0" stroke="#3a6ea5" stroke-width="3"/><text x="36" y="4">official calculation</text><line x1="0" y1="22" x2="28" y2="22" stroke="#c6533f" stroke-width="3"/><text x="36" y="26">public proxy</text></g>'
        + f'<text x="{left + plot_width/2:.1f}" y="{height-2}" text-anchor="middle">elapsed from final ACARS anchor</text>'
        + '</svg>'
    )


def render_report(results: dict[str, Any], audit: dict[str, Any], sources: dict[str, Any]) -> str:
    acars = results["acars_validation"]
    post = results["post_acars_comparison"]
    stress = results["stress_family"]
    seconds_per_hour = results["calculation_conventions"]["seconds_per_hour"]
    reference_attestation = audit["public_reference_pin_attestation"]
    source_map = {row["id"]: row for row in sources["sources"]}
    report_url = escape(source_map["malaysia_safety_report"]["url"])
    appendix_url = escape(source_map["official_appendix_1_6e"]["url"])
    sage_url = escape(source_map["faa_sage_technical_manual"]["url"])
    icao_url = escape(source_map["icao_doc_9889_update"]["url"])

    interval_rows = "".join(
        "<tr>"
        f"<td>{index}</td><td>{escape(row['start_utc'][11:19])}–{escape(row['end_utc'][11:19])}</td>"
        f"<td>{number(row['observed_burn_kg'], 0)}</td><td>{number(row['predicted_burn_kg'], 1)}</td>"
        f"<td class={'positive' if row['error_predicted_minus_observed_kg'] > 0 else 'negative'}>{row['error_predicted_minus_observed_kg']:+.1f}</td>"
        "</tr>"
        for index, row in enumerate(acars["intervals"], start=1)
    )
    post_rows = "".join(
        "<tr>"
        f"<td>{row['segment']}</td><td>{number(row['duration_s'], 1)}</td>"
        f"<td>{number(row['official_ending_fuel_kg'], 1)}</td><td>{number(row['predicted_ending_fuel_kg'], 1)}</td>"
        f"<td class='negative'>{number(row['predicted_minus_official_ending_fuel_kg'], 1)}</td>"
        "</tr>"
        for row in post["segments"]
    )
    stress_rows = "".join(
        "<tr>"
        f"<td>{escape(row['profile_id'])}</td><td>{number(row['burn_kg'], 1)}</td>"
        f"<td>{row['likelihood_weight']:.1f}</td><td>{'yes' if row['initializer_eligible'] else 'no'}</td>"
        "</tr>"
        for row in stress["profiles"]
    )
    range_rows = "".join(
        "<tr>"
        f"<td>{escape(row['id'])}</td><td>{escape(row['sheet'])}!{escape(row['range'])}</td>"
        f"<td><code>{escape(row['canonical_value_sha256'][:16])}…</code></td><td>{'match' if row['matches_pin'] else 'MISMATCH'}</td>"
        "</tr>"
        for row in audit["range_pins"]
    )
    convergence = results["numerical_convergence"]
    command = (
        "python3 src/recreate.py --workbook "
        "'/jackbox/home/.iso/thread-storage/MH370-legacy-pre-refactor-20260824/"
        "corpus/repositories/flight-mh370-revisited-e0115e817975d073bdf2b09a428fbce62aeda35c/"
        "downloads/MH370/9M-MRO Fuel Model V5.X.xlsm'"
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MH370 public fuel/performance recreation</title>
<style>
:root{{--ink:#17202a;--muted:#667085;--paper:#f6f4ef;--card:#fff;--line:#d9dde5;--blue:#3a6ea5;--teal:#2d7f82;--red:#b74735;--amber:#a96618}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1040px;margin:auto;padding:52px 28px 80px}} h1{{font:700 clamp(2rem,5vw,4rem)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.3rem 0 1rem;max-width:850px}}
h2{{font:700 1.65rem/1.2 Georgia,serif;margin:3.2rem 0 1rem}} h3{{font-size:1rem;margin:0 0 .45rem}} p{{max-width:850px}} a{{color:#245f91}} code{{font:12px ui-monospace,SFMono-Regular,monospace}}
.eyebrow{{color:var(--blue);font-weight:750;text-transform:uppercase;letter-spacing:.12em;font-size:.76rem}} .lede{{font-size:1.17rem;color:#344054;max-width:850px}}
.badge{{display:inline-block;border:1px solid #d29a58;background:#fff4df;color:#7a4506;border-radius:999px;padding:.32rem .75rem;font-weight:750}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:28px 0}} .card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;box-shadow:0 8px 24px rgba(20,30,45,.04)}}
.metric{{font:700 1.8rem/1.1 Georgia,serif;margin:.2rem 0}} .label{{color:var(--muted);font-size:.83rem}} .callout{{border-left:5px solid var(--amber);background:#fff8ea;padding:16px 19px;margin:22px 0;border-radius:0 9px 9px 0}}
.chart{{background:white;border:1px solid var(--line);border-radius:12px;padding:14px;overflow:auto}} svg{{width:100%;min-width:620px;display:block}} table{{width:100%;border-collapse:collapse;background:white;font-size:.9rem}}
th,td{{padding:9px 10px;border-bottom:1px solid #e5e8ee;text-align:right}} th{{background:#f0f3f7;color:#475467;font-size:.76rem;text-transform:uppercase;letter-spacing:.04em}} th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){{text-align:left}}
.positive{{color:var(--red);font-weight:650}} .negative{{color:var(--teal);font-weight:650}} .equation{{font:15px/1.6 ui-monospace,SFMono-Regular,monospace;background:#17202a;color:#f2f5f7;padding:16px 19px;border-radius:9px;overflow:auto}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:16px}} .small{{color:var(--muted);font-size:.86rem}} .hash{{word-break:break-all}} .status-ok{{color:#237451;font-weight:700}} .status-block{{color:#9b3c2c;font-weight:700}}
footer{{border-top:1px solid var(--line);margin-top:55px;padding-top:18px;color:var(--muted)}}
@media(max-width:760px){{.grid,.two{{grid-template-columns:1fr}}main{{padding:34px 16px 60px}}}}
@media print{{body{{background:white}}main{{padding:0;max-width:none}}.card,.chart{{box-shadow:none;break-inside:avoid}}a{{color:inherit;text-decoration:none}}}}
</style></head><body><main>
<div class="eyebrow">Source-only technical recreation</div>
<h1>Public equations pass a coarse climb check and fail level cruise.</h1>
<p class="lede">A clean-room B772 point-mass/BFFM2 proxy reproduces the six official ACARS fuel reports surprisingly closely in total, but the interval signs reveal cancellation. Applied unchanged to the official post-ACARS segment abstraction, it burns <strong>{number(post['overburn_vs_official_calculation_kg'],3)} kg too much</strong> by Arc 1.</p>
<p><span class="badge">Canonical initializer: blocked</span></p>
<div class="grid">
  <div class="card"><div class="label">ACARS total error · predicted − observed</div><div class="metric">{acars['total_error_predicted_minus_observed_kg']:+.2f} kg</div><div class="small">Observed burn 5,400 kg</div></div>
  <div class="card"><div class="label">Five-interval RMSE</div><div class="metric">{number(acars['interval_rmse_kg'],2)} kg</div><div class="small">Fuel reports are rounded to 100 kg</div></div>
  <div class="card"><div class="label">Arc‑1 over-burn</div><div class="metric">{number(post['overburn_vs_official_calculation_kg']/1000,3)} t</div><div class="small">Not tuned away</div></div>
</div>

<h2>Official anchor</h2>
<p>The state is fixed exactly at <strong>2014‑03‑07 17:06:43 UTC</strong>: ZFW 174,369 kg; fuel 43,800 kg; pressure altitude 35,004 ft; Mach 0.821; SAT −43.8 °C. These values and the earlier five ACARS rows come from <a href="{report_url}">Table 1.9A of the Malaysian safety report</a>.</p>

<h2>Coarse ACARS validation</h2>
<div class="chart">{acars_error_chart(acars['intervals'])}</div>
<p>The first climb interval is over-predicted by 163.9 kg. All four later intervals are under-predicted by 32–57 kg. The small −15.7 kg total error is therefore cancellation, not evidence of a uniformly accurate performance model.</p>
<div class="chart"><table><thead><tr><th>Interval</th><th>UTC</th><th>Observed kg</th><th>Proxy kg</th><th>Error kg</th></tr></thead><tbody>{interval_rows}</tbody></table></div>

<h2>Unchanged post-ACARS comparison</h2>
<div class="chart">{post_chart(post, seconds_per_hour)}</div>
<div class="chart"><table><thead><tr><th>Segment</th><th>Duration s</th><th>Official end kg</th><th>Proxy end kg</th><th>Proxy − official kg</th></tr></thead><tbody>{post_rows}</tbody></table></div>
<div class="callout"><strong>This is a reproduction of the discrepancy, not a fit.</strong> The public proxy ends at {number(post['predicted_ending_fuel_kg'],1)} kg versus the official calculated {number(post['official_calculated_ending_fuel_kg'],1)} kg. The printed segment durations total {number(post['printed_duration_s'],1)} s, 4.9 s short of the stated Arc‑1 epoch because Table 3 durations are rounded.</div>

<h2>Why the apparent agreement breaks</h2>
<div class="two">
  <div class="card"><h3>What the public model actually is</h3><p>A generic B772 parabolic polar computes drag and required thrust. Installation-adjusted ICAO LTO fuel flows are linearly interpolated by fraction of static rated thrust, then transformed with the BFFM2 ambient relation.</p><div class="equation">CD = CD0 + k·CL²<br>Wf = Wf,ref · δ / (θ^3.8 · exp(0.2·M²))</div></div>
  <div class="card"><h3>What it is not</h3><p>It is not the 9M‑MRO engine deck, does not capture the exact airframe/Trent 892B integration or compressibility/wave-drag behavior, and uses an emissions correction as a cruise fuel model. At the anchor it interpolates near {acars['anchor_flow']['raw_thrust_fraction']*100:.1f}% of static thrust—far below the <a href="{icao_url}">ICAO 60–100% reduced-takeoff interpolation domain</a>.</p></div>
</div>
<p>The official comparator used proprietary Boeing 777 performance information and Rolls‑Royce left/right engine analysis, as stated in <a href="{appendix_url}">Appendix 1.6E</a>. Standard-day post-ACARS temperatures also make the proxy's θ<sup>−3.8</sup> correction materially different from the warm measured anchor. These mechanisms explain why a climb-total coincidence cannot license cruise propagation; they do not apportion the 4.2265 t gap uniquely.</p>

<h2>Workbook audit: evidence, never executable input</h2>
<div class="grid">
  <div class="card"><div class="label">Preserved artifact</div><div class="metric">{audit['package']['member_count']} parts</div><div class="small">{number(audit['file']['size_bytes']/1_000_000,3)} MB · {audit['package']['sheet_count']} sheets</div></div>
  <div class="card"><div class="label">Pinned ranges</div><div class="metric">{sum(row['matches_pin'] for row in audit['range_pins'])}/{len(audit['range_pins'])}</div><div class="small">Cached/constant value hashes only; no values exported</div></div>
  <div class="card"><div class="label">Execution policy</div><div class="metric">0 macros</div><div class="small">No formula recalculation or external-link traversal</div></div>
</div>
<p class="hash"><strong>Preserved SHA‑256:</strong> <code>{audit['file']['sha256']}</code></p>
<p>The artifact identifies itself as <strong>{escape(audit['version']['text'])}</strong>. It contains an unsigned VBA project, one external link, {audit['formula_environment']['bicubic_interpolation_formula_count']:,} calls to a workbook UDF, @RISK/Solver names, and Boeing-confidential notices. A local side-by-side audit found all {reference_attestation['equal_range_count']} selected performance-range value digests identical to the hash-pinned public V5.6 artifact while {reference_attestation['ooxml_changed_part_count']} OOXML parts differ overall. Rights/provenance mixing and event-linked calibration keep every table <strong>audit-only</strong>.</p>
<details><summary>Show 19 audit-only range pins</summary><div class="chart"><table><thead><tr><th>ID</th><th>Range</th><th>SHA‑256 prefix</th><th>Status</th></tr></thead><tbody>{range_rows}</tbody></table></div></details>

<h2>Circular quantities are excluded</h2>
<p>The executable model has no legacy 18:22 fuel input, no 0.45 t standard deviation, and no 00:17:30 exhaustion target. The <a href="{report_url}">official event sequence</a> models roughly two minutes from dual-engine flameout through APU/SDU startup to the 00:19 handshake, so back-solving 00:17:30 from that event is circular. The workbook audit finds an event-time calibration indicator and exports only its cell locator and content hash.</p>

<h2>Pulau Perak altitude stress family</h2>
<p>These three counterfactual profiles test sensitivity to a descent/reclimb shape. Every waypoint is a model choice, every likelihood weight is zero, and none can validate or initialize the estimator.</p>
<div class="chart"><table><thead><tr><th>Profile</th><th>Proxy burn kg</th><th>Weight</th><th>Initializer eligible</th></tr></thead><tbody>{stress_rows}</tbody></table></div>

<h2>Initializer contract and blocker</h2>
<p class="status-block">BLOCKED for canonical integration.</p>
<p>The exact contract fixes the final ACARS anchor, requires one explicitly identified trajectory/performance family, and returns unit-tagged fuel and mass with hashes and convergence diagnostics. Engine-specific end-of-flight use additionally requires left/right accessible fuel and feed state, which total ACARS fuel does not provide.</p>
<ol><li>Resolve the level-cruise performance failure using legally usable, independently validated Trent 892B/B772-relevant evidence—without fitting Arc 1 or a later event.</li><li>Provide an independently supported tank/feed split and uncertainty model before predicting engine-specific flameout.</li></ol>

<h2>Determinism and reproduction</h2>
<p>The 2 s, 1 s, and 0.5 s ACARS runs span only {convergence['spread_kg']:.4f} kg. Scientific fingerprint: <code>{escape(results['scientific_fingerprint_sha256'])}</code>.</p>
<div class="equation">cd .sources/ulich-mh370-fuel-performance<br>{escape(command)}</div>
<p class="small">Python standard library only. `outputs/execution_metrics.json` records run-specific wall time and peak resident memory; `SHA256SUMS` hashes the source and generated artifacts. The run-specific metrics file is intentionally outside the scientific fingerprint.</p>

<h2>Sources</h2>
<p>Claims are passage-located in <code>citation-ledger.md</code>. Core equation sources: <a href="{sage_url}">FAA SAGE technical manual</a>; interpretation bounds: <a href="{icao_url}">ICAO Doc 9889 update</a>; official comparison: <a href="{appendix_url}">Appendix 1.6E</a>.</p>
<footer>Generated entirely from pinned JSON fixtures and source code. No workbook table value is embedded in this report.</footer>
</main></body></html>"""
