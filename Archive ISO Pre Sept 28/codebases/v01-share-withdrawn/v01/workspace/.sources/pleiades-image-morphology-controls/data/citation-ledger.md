# Citation audit for the fuselage sensitivity

All cited sources are primary investigation or manufacturer records. “Printed
page” refers to the page number displayed in the report; “PDF page” counts from
the first PDF page. Sources were retrieved from the official URLs on
25 August 2026.

| Model or interpretation claim | Located support | Use in this analysis |
| --- | --- | --- |
| The 777 fuselage is defined by sections 41, 43, 44, 45, 46, 47 and 48, with six unique longitudinal intervals. | Murphy (2013), printed/PDF p. 4, gives BS 92.5–655, 655–1035, 1035–1434, 1434–1832, 1832–2150 and 2150–2570. | These six intervals define the documented-section family. Sections 44 and 45 share one interval and cannot be separated by an axisymmetric silhouette. |
| The aft pressure bulkhead is at BS 2150 and the pressurised fuselage extends from BS 126 to BS 2150. | Murphy (2013), printed/PDF p. 5. | Locates documented section 47 immediately forward of the aft pressure bulkhead and section 48 aft of it. |
| In Asiana 214, the upper portion of section 48 from about BS 2150 to BS 2370 departed with the vertical fin; the lower portion was severely damaged. | Murphy (2013), printed/PDF pp. 8–9. The report also states that examined fractures were consistent with overstress and showed no fatigue. | Accident context only. No separate Asiana-derived candidate family or transferability claim is retained. |
| The Asiana tail separated at the aft pressure bulkhead after the main landing gear and aft fuselage struck the seawall. | National Transportation Safety Board (2014), printed p. 34 (PDF p. 52); also synopsis printed p. xii (PDF p. 15). | Establishes accident sequence. It does not establish transferability to an ocean impact. |
| British Airways flight 38 recorded 2.9g at initial ground impact; later landing-gear structure punctured the fuselage at rows 29/30 without damage to the centre keel, forward/aft cargo floors or stanchions. | Air Accidents Investigation Branch (2010), printed pp. 43 and 63 (PDF pp. 57 and 77). | Demonstrates that a 777 impact can cause local penetration without producing separated barrel sections. It is not a matched impact case. |
| After the US Airways 1549 A320 water impact, the cabin remained intact, aft lower-fuselage damage progressed toward the pressure bulkhead, and the tail cone separated from most attachment points and lost its conical form. | National Transportation Safety Board (2010), printed pp. 30–32 (PDF pp. 47–49); causal discussion at printed p. 78 (PDF p. 95). | Demonstrates that water impact can cause progressive local shell and bulkhead failure without preserving a neat barrel silhouette. The aircraft type and energy state differ. |
| Boeing airport-planning geometry supplies an aircraft outline but no evidence about breakup. | Boeing Commercial Airplanes (2024); derived geometry hash below. | Supplies the side outline used to construct the axisymmetric radius profile. |

## Source identities and integrity

| Local file | Official source | SHA-256 |
| --- | --- | --- |
| [ntsb-asiana-structures-factual-report.pdf](../paper/ntsb-asiana-structures-factual-report.pdf) | [NTSB docket: Structures Group Chairman’s Factual Report, DCA13MA120](https://data.ntsb.gov/Docket/Document/docBLOB?FileExtension=pdf&FileName=Structures+7-Factual+Report+of+Group+Chairman-Master.pdf&ID=398690) | 0da7ac8f4f6f1f88c050eb181226d17ed31da09f7b8e303516d168cd294b064e |
| [ntsb-asiana-214-final-report.pdf](../paper/ntsb-asiana-214-final-report.pdf) | [NTSB/AAR-14/01](https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1401.pdf) | 842b2947e957b64d948d6a9d38a4aac3203f11f22946906c8e807a94a9508e6f |
| [aaib-british-airways-38-final-report.pdf](../paper/aaib-british-airways-38-final-report.pdf) | [AAIB Aircraft Accident Report 1/2010](https://assets.publishing.service.gov.uk/media/5422f3dbe5274a1314000495/1-2010_G-YMMM.pdf) | 2e95e1018fba4f95a3d563f6f1c5c47e29f2099e5337fb2e3ed25c6e88672868 |
| [ntsb-us-airways-1549-final-report.pdf](../paper/ntsb-us-airways-1549-final-report.pdf) | [NTSB/AAR-10/03](https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1003.pdf) | fe9e1733e8400f3ea9ce0832f36d934c829ac369e8a66765dc423d18973640ef |

Derived-input hashes:

- target masks and strict intervals: e27c4185dadedbc05ae476e61b8dc964c624bb96fdbccb5af2cbd9fc695edb2c
- Boeing-derived fuselage geometry: 708dc8fc0e56ebf83a615dd0f6393c9d763426d05ea60855449902acbb24ba1c
- preceding five-family result: 3e4e60ffee52482c113a8fbf49aef3236cd819eabff830932c79dc057fd1b8fb
- selected legacy PCA display masks: 56222c54bd6cbc9b7b8119818472e9b4e40dc46aead69c86dd19fa848071349d
- selected Boeing full-component display context: 820061b135ed1e6fbcb176f1171c7147a9f4c641b87cc76de7dbc9e0676322be

## Excluded inferences

The sources do not support any of the following:

- treating every production-section boundary as a fracture plane;
- assigning numerical breakup probabilities to the six sections;
- transferring the Asiana seawall breakup sequence to an MH370 ocean impact;
- treating the A320 ditching as a 777 structural calibration;
- inferring a whole-airframe impact attitude or speed from a Pléiades mask.

Accordingly, whole-shell, documented-section and random-cut candidates remain
separate geometry sensitivities. The separately oversampled Asiana analogue
was removed; no accident-derived family is retained as a breakup prior.

## Flooding-attitude sensitivity citation audit

The following claims were checked against primary manufacturer or investigation
records on 26 August 2026. The reports describe the service fuel system and
particular investigated failures; none observes a detached 777 wing floating
at sea.

| Model or interpretation claim | Located support | Use in this analysis |
| --- | --- | --- |
| The 9M-MRO fuel system had two integral wing tanks and one centre tank; the tanks were part of the wing structure and vented through wing channels to maintain near-ambient pressure. | Ministry of Transport Malaysia (2018), printed p. 78 (PDF p. 124), fuel-system section. | Supports an integral wing-box buoyancy source but contradicts treating an intact service tank as a permanently sealed air chamber. |
| On the 777-200, each main tank occupies the integral wing box from Rib 8 (WS 387.0) to Rib 32 (WS 1021.5), with structural tank-end ribs separating it from the centre tank. | National Transportation Safety Board (2014b), PDF p. 2, introduction and 777-200 fuel-tank arrangement. The same page identifies front and rear spars as tank-boundary structure. | Shows that the model's nine equal span/chord cells are not Boeing tank bays. The coarse root row crosses real structural and tank regions and cannot be interpreted as one documented pocket. |
| Each tank is normally vented to atmosphere through roof channels, outboard surge tanks, a flame arrestor and a lower-wing scoop; a pressure-relief valve limits differential pressure if the scoop or arrestor is blocked. | Air Accidents Investigation Branch (2010), printed p. 18 (PDF p. 32), “Fuel tank vent system”. | A submerged or severed outboard vent could admit water, but retained inboard air requires the post-breakup flow path to become isolated or sufficiently slow. That isolation is an inference, not a documented outcome. |
| Engine-strut fuse pins are intended to fail first under prescribed overload and protect the wing tank boundary. In the investigated event the engines separated and the tank boundaries remained intact. | National Transportation Safety Board (2014b), PDF pp. 6–7 and summary on p. 10. | Makes engine absence with a surviving tank boundary mechanically possible for a designed overload sequence. It does not establish the outcome of a high-energy ocean impact or root separation. |
| Boeing lists each high-gross-weight 777-200 main tank at 35,200 L; the complete high-gross fuel system is listed at 169,200 L. | Boeing Commercial Airplanes (2024), printed p. 5-10 (PDF p. 79), tank-capacity table. | The closest attitude state retained 49.3 m³ of equivalent modeled air, 1.40 times one main tank's nominal capacity; it therefore cannot represent air held solely in the left main tank. The lowest-PCA target-like state retained 12.7 m³, below that volumetric ceiling. Neither modeled value is a physical tank-volume estimate. |

### Source identities and integrity for the flooding audit

| Local file or retrieval record | Official source | SHA-256 |
| --- | --- | --- |
| [malaysia-mh370-safety-investigation-report.pdf](../paper/malaysia-mh370-safety-investigation-report.pdf) | [Ministry of Transport Malaysia, Safety Investigation Report MH370 (9M-MRO)](https://www.mot.gov.my/en/AAIB%20Statistic%20%20Accident%20Report%20Document/A%200514%209M-MRO%20MH370.pdf) | b39fa554b38c8e156fbb0f09567de0baf32bafaf012b0f2b80133745f3ed1f32 |
| [ntsb-boeing-777-fuel-tank-addendum.pdf](../paper/ntsb-boeing-777-fuel-tank-addendum.pdf) | [NTSB docket DCA13MA120, Structures Addendum 1: Boeing Fuel Tank Report](https://data.ntsb.gov/Docket/Document/docBLOB?FileExtension=pdf&FileName=Structures+7-Addendum+1+Boeing+Fuel+Tank+Report+24+embedded+Figures-Photos-Master.pdf&ID=398832) | a775fff10a8606ef43ea50b5bb2d555209343677aede20bba51122f8573dbdae |
| [aaib-british-airways-38-final-report.pdf](../paper/aaib-british-airways-38-final-report.pdf) | [AAIB Aircraft Accident Report 1/2010](https://assets.publishing.service.gov.uk/media/5422f3dbe5274a1314000495/1-2010_G-YMMM.pdf) | 2e95e1018fba4f95a3d563f6f1c5c47e29f2099e5337fb2e3ed25c6e88672868 |
| Retrieval record only; Boeing copyright source is not redistributed here. | [Boeing 777-200/200ER/300 Airport Planning, D6-58329 Rev. E](https://www.boeing.com/content/dam/boeing/v2/airports/acaps/777-200-200ER-300_Rev_E.pdf) | ef189aefb353fc15a33866453c51fe2e6251d54a8ca979ba639e9980e5cf19a5 |

Generated-result identities:

- flooding input: c5ccc0e12a2d8fc3d170e82b8663fa9cda90664c4f4ea9d69d350da34c5f68f3
- hydrostatics code: 20f55a1285ddaf26049b26e85fc21f525c2fa85ab4b4ec506787f7b8fbfef79b
- sensitivity runner: ea9fe14dddff07f52ad43ba2411f5b3c9dcfaff95b3a71632a402da2f7317e10
- generated sensitivity JSON: f61fea4c6103804e32e3645d21efc3a7f925f250c87eeec7c8a666549f4c3f68

### Unsupported assumptions

No located primary source establishes that a detached complete 777 wing would
retain an isolated inboard air volume while its entire midspan and tip flooded,
that the modeled 6.33–13.0 t dry-mass range is the actual mass of such a
fragment, or that the wing could remain structurally complete after the
requisite root failure. The public record therefore supports only conditional
mechanical feasibility: integral tank structure and protected engine
separation can preserve buoyancy, while normal venting and the absence of a
documented sealed inboard bay weigh against the fitted retention pattern.

