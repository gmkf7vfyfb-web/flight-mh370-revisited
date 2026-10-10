"""Plain-language descriptions for chart titles and notes (Pete, 10 Oct 2026: "use more informative descriptions of
what you ran"). Internal option keys (end of flight's `loglik:<messages>/<BFO treatment>`, plus its `+alive`
constraint) and field codes (P, C3, C4, P+C3, P+C4) never appear alone on a chart: always with these words.
"""

# Architecture ruling 10 Oct ~16:30 UTC (Pete): the core set and its plain names, used on every chart.
CORE_NAMES = {
    "none": "00:19 Held Out",
    "r600-bto": "00:19 R600 BTO Only",
    "r600/no-offset": "00:19 R600 BTO + Raw BFO",
    "both/startup-offset@fuel-exhaustion": "00:19 Holland H1",
    "both/no-offset": "00:19 Holland H2",
}
MESSAGES = {
    "none": "none of the 00:19 BTO/BFO values scored (held out)",
    "r600-bto": "R600 BTO (18,400 µs) scored; no BFO",
    "both-bto": "R600 BTO and the corrected R1200 BTO scored; no BFO",
    "r600": "R600 BTO (18,400 µs) + R600 BFO (182 Hz) scored; R1200 not scored",
    "r1200": "R1200 BFO only scored (no BTO); R600 not scored",
    "both": "R600 BTO + R600 BFO + R1200 BFO scored (no R1200 BTO)",
}
BFO = {
    "no-offset": "BFO at face value (raw)",
    "inflated": "BFO with an inflated, zero-mean error",
    "startup-offset": "BFO with Holland's start-up frequency offset",
}
CONSTRAINT = {
    "alive": "aircraft transmitting at 00:19:37 (end of flight's 'alive' existence constraint)",
    "silent": "airborne at 00:19:37 and unpowered by the 01:15:56 handshake (end of flight's 'silent' constraint)",
}
SHORT = {  # short panel-title forms
    "none": "00:19 data held out", "r600/no-offset": "R600 as observed", "r600/inflated": "R600, inflated BFO error",
    "r600/startup-offset": "R600, start-up offset", "r1200/no-offset": "R1200 as observed",
    "r1200/inflated": "R1200, inflated BFO error", "r1200/startup-offset": "R1200, start-up offset",
    "both/no-offset": "both bursts as observed", "both/inflated": "both bursts, inflated BFO error",
    "both/startup-offset": "both bursts, start-up offset",
}
FIELD = {
    "P": "Pléiades objects only (12 rating-5 objects in 6 clusters, 23 Mar)",
    "C3": "COSMO-SkyMed radar contacts F1–F3 only (20/21 Mar)",
    "C4": "all four COSMO-SkyMed radar contacts only (20/21 Mar)",
    "P+C3": "Pléiades objects and COSMO contacts F1–F3, all from one debris field",
    "P+C4": "Pléiades objects and all four COSMO-SkyMed contacts, all from one debris field",
}
FIELD_SHORT = {"P": "Pléiades", "C3": "three COSMO-SkyMed contacts", "C4": "all four COSMO-SkyMed contacts",
               "P+C3": "Pléiades + three COSMO-SkyMed contacts", "P+C4": "Pléiades + all four COSMO-SkyMed contacts"}
# Pete, 10 Oct 2026: the three-contact COSMO set is dropped from reporting; all four contacts are used (it makes little
# difference to the PDF). C3 stays computable for sensitivity only.
SEARCH = {
    "none": "before any seabed search",
    "base": "after ATSB Phase 2 and Bluefin-21 (official)",
    "oi2018": "after Phase 2, Bluefin-21 and Ocean Infinity 2018 (grade C)",
    "oi2018-2025": "after Phase 2, Bluefin-21, Ocean Infinity 2018 and the 2025-26 south-east band (grade C)",
}


CAUSE = {"other": "log-on not from fuel exhaustion (no lag term)",
         "fuel-exhaustion": "log-on from fuel exhaustion (end of flight's APU log-on lag density)"}


def describe_option(opt, short=False):
    """'none+alive' -> '00:19 satellite messages not used (held out); aircraft required to be airborne at ...'."""
    o, _, cause = opt.partition("@")
    base, _, con = o.partition("+")
    key = base + (f"@{cause}" if cause and cause != "other" else "")
    if short:
        if key in CORE_NAMES:
            name = CORE_NAMES[key]
        else:
            name = "00:19 " + SHORT.get(base, base) + (f", {cause} log-on" if cause and cause != "other" else "")
        return name + ("" if con == "alive" else (" (unconstrained)" if not con else f", +{con}"))
    msg, _, bfo = base.partition("/")
    parts = [(CORE_NAMES[key] + ": ") if key in CORE_NAMES else ""]
    parts[0] += MESSAGES.get(msg, msg)
    if bfo:
        parts.append(BFO.get(bfo, bfo))
    parts.append(CAUSE[cause or "other"])
    if con:
        parts.append(CONSTRAINT.get(con, con))
    return "; ".join(parts) + f" [end-of-flight arm: {opt}]"


def describe_field(code, short=False):
    return (FIELD_SHORT if short else FIELD).get(code, code)

SEARCH_SHORT = {
    "none": "before any seabed search",
    "base": "after Phase 2 + Bluefin-21 (official)",
    "oi2018": "after Phase 2 + Bluefin-21 + OI 2018 (grade C)",
    "oi2018-2025": "after Phase 2 + Bluefin-21 + OI 2018 + 2025-26 (grade C)",
}
