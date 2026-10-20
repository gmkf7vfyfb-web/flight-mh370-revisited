# Passage-grounded citation ledger

This ledger distinguishes a source's statement from the reproduction's
inference. Page numbers are PDF pages in the retained versions.

| Claim used | Located passage | Assessment use |
| --- | --- | --- |
| Forty-eight B777 flights were selected using known ADS-B segments. | Proposed Global Passive Radar, pp. 4-6: four flights in each of twelve regions; short confirmed or estimated FlightRadar24 segments were downloaded. | The validation begins with known aircraft tracks. |
| The anomaly threshold is either SNR or received frequency at 0.75 sample SD. | Proposed Global Passive Radar, p. 6: mean and SD over plus or minus three hours; anomaly at at least 75% SD. | Reproduced exactly for same transmitter, receiver and band with at least five rows. |
| A hit is selected within 2 km of the known two-minute aircraft segment. | Proposed Global Passive Radar, pp. 6-7: candidate links first within 40 km, then links within 2 km of target track. | This is target-conditioned classification, not blind location. |
| The source control is six minutes later. | Proposed Global Passive Radar, p. 6. | We reproduced it and added symmetric time controls. |
| PropLab is used for hop and MUF plausibility. | Proposed Global Passive Radar, p. 6: realistic hop count and maximum usable frequency checks. | No numerical acceptance rule or realized-mode observation is specified. |
| Antenna verification means owner-sourced coordinates checked against Maidenhead. | Proposed Global Passive Radar, pp. 6-7. | No historic pattern, azimuth, polarization or beam-state verification was found. |
| The headline data contain a high anomaly base rate. | Proposed Global Passive Radar, p. 16: 742 unique anomalous observations out of 1,078; about 13 links per aircraft. | Explains why at-least-one-anomaly accumulation is weak evidence. |
| Reported discrimination is weak over oceans. | Proposed Global Passive Radar, pp. 16-17: AUC 55.6% overall and 52.8% over oceans. | Ocean performance is the relevant MH370 regime. |
| The MH370 position was updated using WSPR every two minutes. | MH370 Flight Path Analysis, p. 6: estimated position updated every two minutes and moving reachability grid used. | This is a sequential trajectory-conditioned search. |
| The paper says a 3-D aircraft/ray intersection is required. | MH370 Flight Path Analysis, p. 5. | We treat altitude as a material unresolved requirement. |
| The implemented PropLab description is only a plausibility check. | MH370 Flight Path Analysis, pp. 6 and 12-13: IRI-2007, topography, MUF, elevation and hop count. | No explicit 10 km intersection rule was located. |
| A worked ray uses about 2 degrees elevation and five hops. | MH370 Flight Path Analysis, p. 13. | A 10 km ray point is hundreds of kilometres from a ground endpoint at such an angle. |
| The archived WSPR time is a nominal two-minute-cycle label, not the physical midpoint of the transmission. | MH370 Flight Path Analysis, p. 5: "WSPR signals are sent every two minutes and are synchronised with GPS to start one second after every even UTC minute. The transmission of the WSPR protocol takes 110.484 seconds." The WSPRnet API documentation says spots are timestamped with the start of the decoded two-minute cycle (xx:00, xx:02, etc.). | The frozen PHaRLAP protocol evaluates the ionosphere at 56.242 seconds after the archive label, and records this interpretation explicitly. |
| The published PropLab worked example contains conflicting calendar years. | MH370 Flight Path Analysis, p. 13: the prose identifies 7 March 2014 at 22:52 UTC, while the titles embedded in Figures 9 and 10 state 2019/03/07; Figure 10 also displays elevation 1.981 degrees, azimuth 99.3427 degrees and path length 12,273.9 km. | Historical 2014 is the primary physical epoch because it is the event described in the prose; the screenshot inconsistency prevents an exact reproduction of the displayed configuration and is reported rather than silently corrected. |
| The later paper estimates 9.7% at commercial altitudes. | Long Distance paper, p. 3; no derivation or uncertainty accompanies the figure. | Compared with the transparent h/H sensitivity. |
| The later worked example reports 7.97 degrees and a three-hop ray. | Long Distance paper, p. 7. | At the stated 9,045 ft aircraft altitude, a straight final leg reaches that height about 19.7 km before a ground endpoint. |
| Bearing alignment is approximately 180 degrees. | Long Distance paper, p. 11: final-to-initial bearing difference within about 0.323 degrees. | Because links were selected through the aircraft location, this is not an independent reflection measurement. |
| PropLab supports 2-D and 3-D tracing but 2-D trades accuracy for speed. | PropLab User Guide, PDF pp. 30 and 33. | Exact mode matters to reproduction. |
| PropLab exposes transmitter and receiver height, normally defaulting to zero. | PropLab User Guide, PDF p. 34. | A faithful altitude test is possible, but the authors' saved settings are missing. |
| PropLab settings can materially alter results. | PropLab User Guide, PDF pp. 34-37: hop limits, step lengths, IRI choices and 2-D/3-D ground-reflection differences. | A substitute default run would not reproduce the historic method. |
| Independent work identified the target-selection problem. | Loi et al., p. 4: existing studies first find an aircraft and then nearby intersections. | Independent agreement on the validation-design issue. |
| Independent blind intersection fields remain extremely dense. | Loi et al., p. 6: 12,324 intersections fell only to 11,804 after an optimistic SNR screen. | Propagation filtering alone need not solve multiplicity. |
| Independent work did not verify localization. | Loi et al., pp. 9-10: unable to conclusively verify; recommends a probability model and ray tracing. | Supports the narrow current exclusion, not impossibility. |
| Conventional passive forward-scatter radar is physically real. | Contu et al. 2017 reports experimental airborne-target signatures extracted from raw broadcast signals by correlation. | Distinguishes HF/passive-radar physics from the adequacy of WSPRnet summary metadata. |
| The public archive timestamp is a spot/report field, not a range observable. | WSPR Live schema: one-second DateTime storage and raw fields as reported by WSPRnet; WSJT-X uses two-minute WSPR sequences. | No separate transmission, reception, delay or angle measurement localizes the perturbation along a path. |
| WSPR spot metadata do not select short versus long path. | Kent, WSPR and MH370 - Theory, pp. 17-18. | Full-circle extension is a model choice, not an observed route. |
| Long-distance scatter benchmark has very large extra loss. | Kent, pp. 6-7; independently recalculated in this bundle. | Used only as a favorable stress test. |
| The earlier blind flight disclosed substantial prior information. | GDTAAA V2 Blind Test Flight, pp. 1, 4-5. | It was not blind global localization. |
| The reported crash endpoint changed materially. | 2022 report gives 33.177 S, 95.300 E; 2023/2025 gives 29.128 S, 99.934 E. | Great-circle displacement is 630.1 km; result is method-version dependent. |
| ATSB did not validate WSPR. | ATSB MH370 statement, 2022: it could not assess validity; sonar review was due diligence. | Official re-review is not scientific endorsement. |
| Liverpool described the work prospectively. | University of Liverpool, 6 Mar 2024: testing whether WSPR could track and might help define a search area. | Evidence of research interest, not validation. |
| Ocean Infinity did not publicly identify WSPR as an operational input. | Ocean Infinity, 8 Mar 2026, says all available information was considered but does not mention WSPR or coordinates. | Stronger claims about operational influence are unsupported by a primary source located here. |
| The authors' implementation replaces Maidenhead cell centres with date-specific antenna coordinates. | Godfrey, OE-FGR Case Study comment, 9 Jul 2024, numbered workflow steps 2-4: enrich each call with the actual antenna location at that date, sourced from amateur-radio sites/registries, check it against the locator, and repair missing database entries. A later paragraph on the same page says final published links use confirmed antenna locations. | The public six-character-locator reproduction is conditional on cell centres and cannot be described as a complete coordinate-level reproduction. |
| The antenna-coordinate database is not publicly inspectable in the cited material but has been offered on request. | Godfrey, OE-FGR Case Study comment, 9 Jul 2024: the database uses public-domain information but requires confidential handling. Godfrey, New Search comment, 9 May 2025: the free-on-request package includes an antenna database claimed to locate study antennas within 10 m. | The claimed precision and temporal validity require the versioned database rows and source provenance; modern callbook or postal points are not substitutes for 2014 antenna truth. |

Online source links:

- https://www.mh370search.com/2025/01/01/new-technology/
- https://news.liverpool.ac.uk/2024/03/06/university-researchers-provide-statistical-expertise-to-help-locate-mh370/
- https://www.atsb.gov.au/news/2022/mh370-statement
- https://www.atsb.gov.au/mh370-data-review
- https://oceaninfinity.com/news/conclusion-of-the-search-for-malaysian-airlines-flight-mh370/
- https://www.mh370search.com/2022/10/28/oe-fgr-case-study/
- https://www.mh370search.com/2024/05/05/new-search/comment-page-10/
- https://shop.spacew.com/index.php/product/proplab-pro-hf-radio-propagation-laboratory/
- https://www.dst.defence.gov.au/our-technologies/pharlap-provision-high-frequency-raytracing-laboratory-propagation-studies
- https://www.dsta.gov.sg/staticfile/ydsp/projects/files/reports/Report%20-%20Forward%20Scatter%20Aircraft%20Detection%20with%20Amateur%20Radio%20Network%20WSPRnet.pdf
- https://research.birmingham.ac.uk/en/publications/passive-multifrequency-forward-scatter-radar-measurements-of-airb/
- https://wspr.live/
- https://github.com/garymcm/wsprnet_api
