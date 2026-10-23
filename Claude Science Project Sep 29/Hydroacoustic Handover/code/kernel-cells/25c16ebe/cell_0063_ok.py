ed6("| L | the ordering — simulate, then test, never shape — leads the mission | §1 |",
    "| L | the ordering — simulate, then test, never shape — leads the mission | §1 |\n| M | **correction**: the two-engine flame-out structure is already built; the deferral narrows to asymmetric dynamics and first-flame-out emission | §5, §13, §10.9 |",
    "changelog row M")
ed6("Twelve changes. A–C alter what the module is obliged to produce",
    "Thirteen changes. A–C alter what the module is obliged to produce", "count in §0")
ed6("**Version 5, 13 October 2026.**", "**Version 6, 13 October 2026.**", "version header")
ed6("Twelve changes, listed in §0.",
    "Thirteen changes, listed in §0. Change M corrects a factual error carried by versions 1 to 5.", "header count")
open("end-of-flight.md","w").write(v6)
heads = re.findall(r"^## \d+\..*$", v6, re.M)
assert [int(re.match(r"## (\d+)\.",h).group(1)) for h in heads] == list(range(0,len(heads)))
print(f"\nsections 0..{len(heads)-1} contiguous | v5 {len(v5):,} -> v6 {len(v6):,} chars")
