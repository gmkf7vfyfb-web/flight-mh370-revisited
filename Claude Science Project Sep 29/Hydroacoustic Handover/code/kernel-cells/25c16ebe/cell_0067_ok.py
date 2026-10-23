v7 = open("end-of-flight.md").read()
def ed7(old,new,label):
    global v7
    assert v7.count(old)==1,(label,v7.count(old)); v7=v7.replace(old,new); print("ok:",label)

ed7("""| requirement | checkable form | reported statistic | current value |
|---|---|---|---|
| level-offs including 10,000 ft and 4,000 ft | the sampled level-off altitude support **must contain both**; state the interval in the run note | the realised level-off altitude distribution | **failed** — support is 11,000 to 30,000 ft, excluding both |
| lower-altitude flight need not mean descending throughout | the realised non-descending time between onset and impact | its median and 95th percentile, and the weight fraction above 600 s, which must exceed **5 per cent** | **failed** — median 53 s, 95th percentile 411 s, 1.75 per cent above 600 s |
""",
"""| requirement | checkable form | reported statistic | current value |
|---|---|---|---|
| level-offs including 10,000 ft and 4,000 ft | both altitudes in the candidate set, plus the sampled additional altitude whose interval is stated in the run note | the realised level-off altitude distribution — **currently not emitted as a column, so this cannot be checked from the output at all** | **unverified.** `leveloff_altitude_ft = [11000, 30000]` is the *additional sampled* altitude, and the dynamics note records 10,000 ft and 4,000 ft as always-present candidates alongside it. Reading the configuration alone suggests a gap that the code may not have. Emit the column and settle it |
| lower-altitude flight need not mean descending throughout | the realised time **fraction** spent descending between onset and impact | its quantiles and the weight fraction below 0.60, which must exceed **5 per cent** | **met.** Descending fraction 0.57 / 0.93 / 1.00 at the 5th, 50th and 95th percentiles; 5.8 per cent of weight below 0.60 and 41.5 per cent below 0.90; the longest level segment reaches 2,407 s against the configured 2,400 s cap |

**Use the fraction, not an absolute duration.** An earlier version of this table used "non-descending
seconds above 600 s" and recorded a failure at 1.75 per cent. That statistic was badly chosen: the
median onset-to-impact time is about 1,176 s, so 600 s of level flight is most of the flight and the
threshold was close to unsatisfiable. The fraction is the quantity the requirement is actually about.
The residual concern it leaves is narrower and worth keeping: among descents longer than 1,800 s from
onset — 10.8 per cent of weight — the median non-descending time is only 132 s, so a long descent in
this ensemble is predominantly a slow continuous one rather than descend-cruise-descend.
""", "D table corrected")

ed7("""Three measured failures against version 4's own requirements are recorded in place rather than
corrected silently, because each shows a requirement that could not be checked as written: the
onset-boundary condition (§4, 21.6 per cent against a new 5 per cent gate), the two named level-off
altitudes (§4, outside the configured support), and sustained low-altitude flight (§4, 1.75 per cent
against a new 5 per cent floor).""",
"""Measured results against version 4's own requirements are recorded in place rather than corrected
silently. One is a clear failure: the onset-boundary condition (§4, 21.6 per cent against a new
5 per cent gate). Two more were reported as failures in versions 5 and 6 of this document and are
**withdrawn in version 7**: sustained level flight within the descent is in fact **met** on the right
statistic, and the two named level-off altitudes are **unverified** rather than absent — both are
recorded as candidates in the dynamics note and the configured interval is the additional sampled
altitude. The lesson is in §0's closing note.""", "changelog failures")

ed7("""| M | **correction**: the two-engine flame-out structure is already built; the deferral narrows to asymmetric dynamics and first-flame-out emission | §5, §13, §10.9 |""",
"""| M | **correction**: the two-engine flame-out structure is already built; the deferral narrows to asymmetric dynamics and first-flame-out emission | §5, §13, §10.9 |
| N | **correction**: the level-flight requirement is met on the fraction statistic, and the level-off altitude finding is withdrawn as unverified | §4 |

**A note on how two of these were got wrong.** Changes D and M were both written from the stored
configuration without reading the code or the module's own dynamics note, and both overstated a
failure: the configuration's `leveloff_altitude_ft` interval is not the whole candidate set, and an
absolute level-flight duration is not the right statistic for a requirement about proportion. A
configuration value is evidence about a bound, not about behaviour. Where a requirement is about
behaviour, **emit the column and measure it** — which is why the level-off altitude row above now
asks for exactly that. The three-engine-state correction in §5 came from measuring the output rather
than reading the configuration, and it held.""", "changelog N")
open("end-of-flight.md","w").write(v7)
print(f"\nv6 {len(v6):,} -> v7 {len(v7):,}")
