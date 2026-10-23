f = host.findings()
print([(x["id"], x["verdict"]) for x in f["findings"]])
print(host.findings.mark_addressed(
    [x["id"] for x in f["findings"] if x["verdict"] == "fail"],
    note=("Corrected in hydro-h08s-digitised-tail.png v2 (7c625221) and project memory row mem_246805f75b29. "
          "The footnote now reads: all four outliers coincident under loose and table1-gated; the 01:11:39 "
          "deficit (z=-4.17) is ALSO coincident under strict, the other three are not. Verified by reading "
          "h08s_outliers.csv back: strict is True only for the 01:11:39 row.")))
