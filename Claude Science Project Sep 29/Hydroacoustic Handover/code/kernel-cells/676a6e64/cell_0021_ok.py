import re, pathlib
P = pathlib.Path('repo/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md')
s = P.read_text()
orig = s
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:60])
    s = s.replace(old, new)

rep("# Hydroacoustics — mission and master prompt\n",
"# Hydroacoustics — mission and master prompt\n\n"
"**Refresh v2, 21 October 2026 (Pete's rulings of 21 Oct).** The section \"Refresh v2\" at the end of this file\n"
"governs where it differs from the text above it. The current work order is\n"
"`threads/work-orders/hydroacoustics-order-2026-10-21.md`. Run J is the impact set; run I and run-i-dive are\n"
"superseded wherever they are named below.\n")

rep("   *Revised 17 Oct 2026 (ARCHITECTURE.md rule 5): be accurate across the whole arc span that the flight\n"
    "   prior covers. Your evidence is also shown alone, on a prior uniform along the arc (composer.md §0).*\n",
    "   *Revised 17 Oct 2026 (ARCHITECTURE.md rule 5): be accurate across the whole arc span that the flight\n"
    "   prior covers. Your evidence is also shown alone, on a prior uniform along the arc (composer.md §0).*\n"
    "   *Latitude span (Pete, 21 Oct 2026): never truncate latitude arbitrarily. Every table, grid, window and\n"
    "   chart extends north to 20°S or to the 99th-percentile contour of the prior, whichever is more northerly.*\n")

rep("So η is swept log-uniform over at least three decades with the F-35 value as the upper anchor, and\nis reported as a sweep rather than a value.",
    "So η is swept log-uniform over at least four decades (amendment 3, 9 Oct) with the F-35 value as the upper\nanchor, and is reported as a sweep rather than a value.")

rep("**IMOS/Curtin**, 566 MB. Loggers: Perth Canyon 3315 at 31°52.0′S 115°00.1′E; Perth Canyon 3376 at\n31°50.5′S 115°00.8′E, staggered five minutes from 3315; Scott Reef 3250 at 15°29.0′S 121°15.1′E.\n",
    "**IMOS/Curtin**, 566 MB. Loggers: Perth Canyon 3315 at 31°52.0′S 115°00.1′E; Perth Canyon 3376 at\n31°50.5′S 115°00.8′E, staggered five minutes from 3315; Scott Reef 3250 at 15°29.0′S 121°15.1′E.\n*Updated 21 Oct 2026: the set now covers five loggers (Portland 3274 and 3275 added) with a 14 GB\nbackground set for injection-recovery, kept on the Mac. Scott Reef's path to the arc crosses land and\ncarries no information; it stays in the tables as a declared no-information row.*\n")

rep("Set against §3's 20–30 dB, expect that a single-site search cannot clear 5.3σ.",
    "*Threshold ruling, 13 Oct 2026, supersedes the 5.3σ framing of this section as a reporting threshold:\ncandidates are screened at p = 0.3, marked at 0.1 and reported at 0.05, with significance from time slides\nand surrogates. The p-value floor is set by the background set (0.0101 on 98 realisations); to go lower,\nenlarge the background set, do not lower the threshold. The 2·W·B arithmetic above still governs what a\nclaim of detection must clear.*\n\nSet against §3's 20–30 dB, expect that a single-site search cannot clear 5.3σ.")

rep("- **Kadri's identified candidates** from his paper and tables, including the main one at 00:54:30 on\n  a bearing of 306.18°, which crosses the arc near 25.8°S.",
    "- **Kadri's identified candidates** from his paper and tables, including the main one on a bearing of\n  306.18°, which crosses the arc near 25.8°S. His paper gives two times for it: carry **both**, labelled\n  **\"text time 00:52:03\"** and **\"caption time 00:54:30\"** (Pete, 21 Oct 2026), in every window, table\n  and chart; do not pick one. The six H01W signals boxed on his SnT 2025 poster are a named test set\n  (Refresh v2, item 6).")

rep("`make smoke H=hydroacoustics` is the code-path check; **`make hypothesis H=hydroacoustics` runs at\nfull scale.** Queue anything over ~10 minutes or ~4 GB behind `lockf -k /tmp/.mh370-heavy.lock`.",
    "`make smoke H=hydroacoustics` is the code-path check; **`make hypothesis H=hydroacoustics` runs at\nfull scale.** *The `lockf` heavy-lock rule was retired on 17 Oct 2026.* Anything over ~10 minutes or\n~4 GB on the Mac needs a compute slot agreed with end of flight first (post to `coordination/END_OF_FLIGHT.md`),\nbecause end of flight uses all 18 cores; start at 4 threads and expand as cores free.")

print(len(orig), len(s))
P.write_text(s)