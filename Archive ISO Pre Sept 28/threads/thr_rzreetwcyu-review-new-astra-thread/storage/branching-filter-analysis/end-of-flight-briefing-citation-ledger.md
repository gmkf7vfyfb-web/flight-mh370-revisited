# End-of-flight briefing: source checks

The duration and count claims come from saved project calculations, not from the external papers. Citations below locate only the equations and coefficients used as conditional inputs.

| Claim | Retrieved source | Locator / passage | Status |
|---|---|---|---|
| Published B772 clean coefficients 0.034 / 0.051 | Sun, J., Hoekstra, J. M. & Ellerbroek, J. (2020), Estimating aircraft drag polar using open flight surveillance data and a stochastic total energy model, Transportation Research Part C 114, 391–404. DOI 10.1016/j.trc.2020.01.026 | Table 4, journal p.401 / PDF p.13: B772 row, 0.034 and 0.051 | FOUND |
| The adopted force approximation uses lift/drag and a quadratic polar | Same published paper | §2, journal p.392 / PDF p.4, Eqs.(1), (3); C_D = C_D0 + k C_L² | FOUND |
| This approximation does not carry aircraft angular attitude dynamics | Same published paper | PDF p.4 opening paragraph: angular rates “are not explicitly considered” | FOUND |
| Pinned OpenAP 2.6 clean coefficients 0.024 / 0.047 | Upstream commit 4fb21d6e402fd1f4a48b191ad6801c74479e71f5, openap/data/dragpolar/b772.yml | `clean: cd0: 0.024; k: 0.047` | FOUND |
| 31.4733 / 26.7472 min are largest computed durations in this source ensemble | terminal-million-extended-weather/continuations.jsonl, SHA cd63c75b237d766263fbe64e5ca2b3187353bbc01fbe6046e6a488ca744ac98e | openap26-positive-lift-1-targets source3/draw208; openap2020-positive-lift-1-targets source4/draw475; impact.point.time minus boundary.aircraft.time | FOUND; rounded for slides |
| Configured simulation window is 60 min | terminal-million-extended-weather/resolved-config.json | kernel.integration.maximum_duration = 3600 seconds | FOUND; not a proven physical bound |
| Selected plotted replays preserve the original states | end-of-flight-briefing-traces/replay-verification.json and the original source records | Four identities; all physical, contact, fuel and weight fields agree exactly; only passive trace/weather-count fields differ | FOUND |

Paper retrieved from https://repository.tudelft.nl/file/File_fc242ad5-d745-4225-8f2b-ef7faf810d0a ; PDF SHA cf77acf25536922867270a764b0511ada2cfcb330c0d8a7e70dc6eb5be41c141. Full text checked by PyMuPDF and browser. Do not distribute this cached paper with the slides.

Upstream coefficients retrieved with HTTP200 from https://raw.githubusercontent.com/junzis/openap/4fb21d6e402fd1f4a48b191ad6801c74479e71f5/openap/data/dragpolar/b772.yml ; SHA b05b381eac8a896d6a7564ccd8277242c05de307c515b75eb4b3b96fd560ed42 matches the previously pinned source. The web tool returned an internal error for this GitHub resource; direct retrieval and byte verification succeeded.

The final-contact source and exact timing/correction provenance are carried unchanged from terminal-final-contacts.json, Inmarsat/DCA December2014 log, PDF pp.1 and41. These data were checked previously in the owner thread; no new time or frequency correction is introduced.
