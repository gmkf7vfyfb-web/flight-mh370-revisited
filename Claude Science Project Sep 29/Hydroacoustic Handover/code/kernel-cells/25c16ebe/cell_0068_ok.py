v7 = open("end-of-flight.md").read()
v7 = v7.replace("**Version 6, 13 October 2026.**","**Version 7, 13 October 2026.**")
v7 = v7.replace("Thirteen changes, listed in §0. Change M corrects a factual error carried by versions 1 to 5.",
  "Fourteen changes, listed in §0. Changes M and N correct factual errors — M one carried by versions 1 to 5, N one introduced by version 5 itself.")
v7 = v7.replace("Thirteen changes. A–C alter what the module is obliged to produce","Fourteen changes. A–C alter what the module is obliged to produce")
open("end-of-flight.md","w").write(v7)

rep = open("eof-audit-2026-10-13.md").read()
ed_old = """- Configured level-off altitudes are 11,000 to 30,000 ft. The intent explicitly requires 10,000 ft
  and 4,000 ft inside the envelope: 10,000 ft falls just below the lower bound and 4,000 ft is well
  outside it. The approach band of 500 to 2,000 ft and the transition band of 8,000 to 15,000 ft
  cover the altitudes in passing but not as *level-off* options.
- The intent states that an hour between onset and impact need not mean an hour descending.
  Measured: the non-descending time between onset and impact is 53 s at the median and 411 s at the
  95th percentile, and only **1.75 per cent** of the weight has more than 600 s of non-descending
  flight. Sustained low-altitude cruise after a descent is in the configuration but not in the
  realised ensemble."""
ed_new = """**Both items in this subsection were overstated in the first version of this audit and are corrected
here.** They were written from the stored configuration before the module's own dynamics note was
read.

- **Level-off altitudes: unverified, not failed.** The configured `leveloff_altitude_ft` interval is
  11,000 to 30,000 ft, which reads as excluding the 10,000 ft and 4,000 ft the intent requires. But
  the module's dynamics note records both of those as *always-present candidates* with the
  configured interval supplying one additional sampled altitude. The realised level-off altitude is
  not emitted as a column, so this cannot be settled from the output. It needs either source access
  or the column; the audit's original claim of a gap is withdrawn.
- **Level flight within the descent: met.** Measured on the right statistic — the fraction of
  onset-to-impact time spent descending — the quantiles are 0.57 / 0.82 / 0.93 / 1.00 / 1.00 at the
  5th, 25th, 50th, 75th and 95th percentiles, with **5.8 per cent of weight below 0.60** and
  41.5 per cent below 0.90, and the longest level segment reaching 2,407 s against a configured cap
  of 2,400 s. The original statistic — non-descending seconds above 600 s, measured at 1.75 per cent
  — was close to unsatisfiable given a median onset-to-impact time of about 1,176 s, and recorded a
  failure that is not there.
- **What does survive**, narrowly: among descents longer than 1,800 s from onset, which carry
  10.8 per cent of weight, the median non-descending time is 132 s. So a long descent in this
  ensemble is predominantly a slow continuous one rather than descend, cruise, descend again."""
assert rep.count(ed_old)==1
rep = rep.replace(ed_old, ed_new)
rep = rep.replace("""Not yet. Three specific gaps, all measured, all closable.""",
 """Not fully. One significant gap, measured and closable; two items originally reported as gaps are
corrected in §4.3 below, one to "met" and one to "unverified".""")
rep = rep.replace("""| Adequately sample the feasible kinematic space | **No, in three identified places** | Onset support truncated at the hand-off; level-off altitudes exclude 10,000 ft and 4,000 ft; sustained low-altitude flight is effectively absent |""",
 """| Adequately sample the feasible kinematic space | **One confirmed gap** | Onset support truncated at the hand-off (21.6% of the deliberate family's weight against the boundary). Level flight within the descent is covered; the level-off altitude question is unresolved from the output — see §4.3 |""")
open("eof-audit-2026-10-13.md","w").write(rep)
print("report updated; '1.75 per cent' remaining:", rep.count("1.75 per cent"))
