import json, os
os.makedirs("handoff", exist_ok=True)

task = """
You are assembling an INDEPENDENT BENCHMARK SHEET of published end-of-flight / terminal-descent
results for Malaysia Airlines MH370 (Boeing 777-200ER, 9M-MRO), to be used as calibration and
sanity-check targets for a Monte Carlo end-of-flight simulator. You are NOT auditing any code and
NOT producing opinions about MH370's location. You are building a table of what the published
literature actually states, with sources.

Collect, for each source, the quantitative end-of-flight claims that a simulator could be checked
against. Target sources (search for them; use what you can actually retrieve):

1. Boeing engineering-simulator runs reported in the Malaysian Safety Investigation Report (SIR)
   Appendix 1.6E and in ATSB publications: the ~10 simulated cases of uncontrolled flight after
   dual fuel exhaustion. For each case you can find: initial altitude, bank/trim/electrical
   configuration, time to high rates of descent, maximum rate of descent, distance travelled from
   the point of fuel exhaustion, and time to water impact.
2. ATSB reports "MH370 - Definition of Underwater Search Areas" (2014, 2016) and
   "The Operational Search for MH370" (2017): the stated end-of-flight descent rates derived from
   the 00:19:29 and 00:19:37 BFO values (the widely quoted ~0.7 g / 15,000 ft/min and
   ~25,000 ft/min figures), the glide-versus-dive distance bounds (e.g. the ~100 NM glide radius),
   and the stated unresponsive-crew/uncontrolled-descent rationale.
3. Boeing published performance for the 777-200ER / Trent 892: driftdown and best glide ratio,
   maximum L/D, MMO/VMO, maximum operating altitude.
4. Holland (arXiv, "MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at
   End-of-Flight" and any later paper incl. 2024 descent work): the inferred descent and
   acceleration rates at 00:19:29 and 00:19:37, the start-up-transient / oscillator-offset
   argument, and the stated uncertainty.
5. Davey, Gordon, Holland, Rutten, Williams, "Bayesian Methods in the Search for MH370"
   (Springer 2016, open access): the end-of-flight treatment, the assumed post-fuel-exhaustion
   flight distance distribution, and the figures that show the impact/arc distributions
   (Ch. 10 / Ch. 11 in particular).
6. Independent Group / other peer-reviewed or preprint end-of-flight analyses: any published
   estimate of post-fuel-exhaustion flight time, distance, impact speed, impact flight-path angle
   or impact energy. Also CSIRO drift-study assumptions about the impact point if they state an
   end-of-flight constraint.
7. Any published ditching-hypothesis analysis with numbers (e.g. attempted-ditching glide
   distances, touchdown vertical speeds), and published 777 ditching guidance figures that are
   citable from primary sources (not mirrored manuals).

For EVERY row record: source (full citation + DOI/URL), the quantity, the stated value and units,
the stated uncertainty if any, and a one-line note on provenance strength (primary official
report / peer-reviewed / preprint / secondary). Flag explicitly where a widely repeated number
cannot be traced to a primary source. Do NOT invent or interpolate values; if you cannot retrieve
a source, record it as not retrieved rather than quoting from memory.

Deliverables, saved as artifacts:
 - `eof-published-benchmarks.csv` — one row per quantitative claim, columns:
   source_key, citation, doi_or_url, provenance_strength, quantity, value, units, uncertainty,
   conditions, note
 - `eof-published-benchmarks.md` — short narrative: for each of the 7 source groups, what is
   available as a calibration target and what is NOT published (the gaps a simulator cannot be
   checked against), plus a final section listing the 8-12 single most useful numerical
   calibration targets for an end-of-flight Monte Carlo, in priority order.

Use the fetch_article_fulltext tool for anything with a DOI, and web search for official reports.
Be rigorous about not fabricating citations. If a number is contested in the literature, record
both values and say who disputes which.
"""

ctx = """
Context: a Bayesian MH370 reanalysis project is auditing its own end-of-flight Monte Carlo module.
The module simulates from a particle-filter posterior at 00:11 UTC (optionally 22:41) through fuel
exhaustion and descent to ocean impact, emitting impact position, time, attitude, energy and
energy-transfer duration. The audit needs an independently assembled sheet of published numbers
to check the simulator against. You are only building that sheet.
Project convention: no project jargon in chart/table headings; use standard scientific and
statistical terms. Record units explicitly.
"""

d = host.delegate({"task": task, "name": "Benchmarks", "context_summary": ctx}, wait=False)
print(d)
