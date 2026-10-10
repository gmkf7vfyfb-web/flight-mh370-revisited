"""Plain-language descriptions for chart titles and notes (Pete, 10 Oct 2026: "use more informative descriptions of
what you ran"). Internal option keys (end of flight's `loglik:<messages>/<BFO treatment>`, plus its `+alive`
constraint) and field codes (P, C3, C4, P+C3, P+C4) never appear alone on a chart: always with these words.
"""

MESSAGES = {
    "none": "00:19 satellite messages not used (held out)",
    "r600": "00:19:29 log-on request (R600) used; 00:19:37 message not used",
    "r1200": "00:19:37 log-on acknowledge (R1200) used; 00:19:29 message not used",
    "both": "both 00:19 messages used (R600 at 00:19:29 and R1200 at 00:19:37)",
}
BFO = {
    "no-offset": "BFO as observed (no offset)",
    "inflated": "BFO with an inflated, zero-mean error",
    "startup-offset": "BFO with Holland's start-up frequency offset",
}
CONSTRAINT = {
    "alive": "aircraft required to be airborne at 00:19:37 (end of flight's 'alive' constraint)",
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
    "C4": "COSMO-SkyMed radar contacts F1–F4 only (20/21 Mar)",
    "P+C3": "Pléiades objects and COSMO contacts F1–F3, all from one debris field",
    "P+C4": "Pléiades objects and COSMO contacts F1–F4, all from one debris field",
}
FIELD_SHORT = {"P": "Pléiades", "C3": "COSMO F1–F3", "C4": "COSMO F1–F4",
               "P+C3": "Pléiades + COSMO F1–F3", "P+C4": "Pléiades + COSMO F1–F4"}
SEARCH = {
    "none": "before any seabed search",
    "base": "after ATSB Phase 2 and Bluefin-21 (official)",
    "oi2018": "after Phase 2, Bluefin-21 and Ocean Infinity 2018 (grade C)",
    "oi2018-2025": "after Phase 2, Bluefin-21, Ocean Infinity 2018 and the 2025-26 south-east band (grade C)",
}


def describe_option(opt, short=False):
    """'none+alive' -> '00:19 satellite messages not used (held out); aircraft required to be airborne at ...'."""
    base, _, con = opt.partition("+")
    if short:
        s = SHORT.get(base, base)
        return s + (", airborne at 00:19:37" if con == "alive" else (f", +{con}" if con else ""))
    msg, _, bfo = base.partition("/")
    parts = [MESSAGES.get(msg, msg)]
    if bfo:
        parts.append(BFO.get(bfo, bfo))
    if con:
        parts.append(CONSTRAINT.get(con, con))
    return "; ".join(parts) + f" [end-of-flight option key: {opt}]"


def describe_field(code, short=False):
    return (FIELD_SHORT if short else FIELD).get(code, code)

SEARCH_SHORT = {
    "none": "before any seabed search",
    "base": "after Phase 2 + Bluefin-21 (official)",
    "oi2018": "after Phase 2 + Bluefin-21 + OI 2018 (grade C)",
    "oi2018-2025": "after Phase 2 + Bluefin-21 + OI 2018 + 2025-26 (grade C)",
}
