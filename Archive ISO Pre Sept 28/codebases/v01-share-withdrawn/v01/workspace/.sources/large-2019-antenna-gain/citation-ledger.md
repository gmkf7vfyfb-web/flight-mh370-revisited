# Citation ledger — Large (2019) end-of-flight claims

Full source: Peter O. Large, *A Meta-Analysis of Geospatial Estimates in the
Case of Malaysian Airlines Flight MH370*, ProQuest 13857090 (2019),
`paper/paper.pdf`, SHA-256
`7fbc853d9903b3769fce18bd9f5e08da17f459a4fa6507333231df28afb222ee`.

The page locators below distinguish the PDF page index from the printed thesis
page. Text was checked against the complete local PDF; extraction used pypdf
6.0.0 only as a locator and the source page was then read in context.

| Claim | Located passage |
| --- | --- |
| The 00:19 R600 sensitivity calculation assumes Mach 0.78, FL300, and initially zero vertical speed. | PDF p.201 / printed p.185, paragraph beginning “For the 00:19Z R600 channel data”. |
| At the southerly residual minimum, the reported required descent is 1,400–1,800 ft/min, 980–2,250 ft/min at two standard deviations, with a mean of 1,662 ft/min. | PDF p.201 / printed p.185, same paragraph and Table 19 discussion. |
| The 00:19 R600 fixed BFO bias is estimated as 150.0 Hz through a two-stage cross-channel procedure. | PDF pp.167–168 / printed pp.151–152; the method is described at PDF p.128 / printed p.112. |
| The physical BFO model uses separate satellite-translation and GES-AFC terms interpolated from proprietary Ashton data. | PDF p.131 / printed p.115, “BFO Physical Functional Model”. |
| The conclusion characterizes the raw-R600 result as roughly 1,600–2,000 ft/min and argues that the R600 channel may not share the transient affecting R1200. | PDF p.256 / printed p.240, end-of-flight discussion. |
| The thesis recognizes that multiple BFO solutions can fit unknown states and that validity does not identify uniqueness. | PDF pp.254–255 / printed pp.238–239, discussion of local solutions and trajectory ambiguity. |

Reproduction status: the reported 1,662 ft/min result is **not reproduced** by
the current canonical forward model. This ledger records the source claim; it
does not endorse the numerical result.
