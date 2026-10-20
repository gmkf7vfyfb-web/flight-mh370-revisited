# Source conditions for final-contact sensitivities

The paper is Ian D. Holland, *MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight*, arXiv:1702.02432v3, 15 January 2018. The retained exact PDF SHA256 is c76dd9f1b6c341e99d95c68002202aad7ba6797eb1f1b343f00468235cd22821. Browser retrieval failed on this continuation; the matching local PDF was read directly.

| Claim | Source and locator | Short passage | Status |
| --- | --- | --- | --- |
| Conditional first startup offset 17–136Hz | Holland v3, PDFp7 §V-B, first numbered conclusion | “between 17 and 136 Hz higher” | FOUND |
| Conditional second startup offset 17–130Hz | Holland v3, PDFp7 §V-B, second numbered conclusion | “between 17 and 130 Hz higher” | FOUND |
| Shared startup offsets decrease by 0–6Hz | Holland v3, PDFp7 §V-A, discussion following Fig8 | “range of [0,6] Hz lower” | FOUND |
| A short power loss need not have the same warm-up | Holland v3, PDFp8 §VI and footnote13 | “no ‘warm-up drift’” (typography normalized) | FOUND |

These are historical conditional bounds, not a calibrated probability law for the last log-on. The implementation may compare zero startup offset with an explicitly declared uniform joint law over second offset17–130Hz and first-minus-second offset0–6Hz. That uniform density is an analyst-selected sensitivity assumption. It preserves the shared-event dependence; it is not attributed to Holland. Measurement noise remains the separately stated Gaussian likelihood unless another error family is explicitly selected. The paper’s historical bounded-error sign inconsistency remains in the source recreation and is not silently imported into that Gaussian likelihood.

Primary contact times/values and R600 correction are attributed separately in inputs/accident/final-satcom-bursts.json. The anomalous second BTO is not replaced by the unsupported legacy18,380microsecond value.


## Kadri original preferred event, inspected 9 September2026

Primary paper: https://doi.org/10.1038/s41598-024-60529-1 ; local exact PDF SHA256 b4f8f37ad1577a0f4726e6acdbfeea295b89197c88fac4ab5546d80bd9eb9db4

Located passages: PDFp14 Table1 and caption give00:54:30UTC and bearing306.18degrees atH01W. PDFp13 gives a seventh-arc range1586km and celerity1500±70m/s. PDFp14 assigns a0.5degree bearing tolerance and its Eq4 relates post-arc travel time/range to source motion. PDFp9 narrative associates306degrees with00:52, conflicting with its own Figure9 rectangle numbering andTable1; retainTable1/rectangle2 as the preferred event definition.

The1586km crossing is conditional geometry, not a measured crash position. Independent division gives17.622minutes at1500m/s, not the paper's stated17.45minutes; at1430–1570m/s the interval is16.837–18.485minutes. At the crossing itself this implies an impact around00:36:01–00:37:40, central00:36:53. End-of-flight trajectories can move away from the crossing, changing travel time. No event identity, calibrated bearing error law, or detection likelihood is established here.
