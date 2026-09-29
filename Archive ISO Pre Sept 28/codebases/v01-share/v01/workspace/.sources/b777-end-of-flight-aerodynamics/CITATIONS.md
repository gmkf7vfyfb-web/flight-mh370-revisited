# Citation ledger

Every scientific or legal intake claim used by this audit is tied to a located passage, table, code field, or complete archive inventory. Links go to the primary publisher or upstream repository. Retrieved files are kept only in the selected `/tmp` cache and are verified against `data/source-pins.json`.

This is an engineering provenance and redistribution screen, not legal advice.

## Aircraft and engine identity

| Audit claim | Primary source and located passage | Locator | Audit use |
|---|---|---|---|
| 9M-MRO was a B777-200ER with RB211 Trent 892B-17 engines. | [Malaysian Safety Investigation Report](https://www.mot.gov.my/en/MH370%20Investigation%20Report/01-Report/MH370SafetyInvestigationReport.pdf): “Engine Model RB211 Trent 892B-17”. | PDF p. 84, aircraft information table | Fixes the required aircraft/engine identity. |
| The installed engine description reports bypass ratio 6.4 and take-off thrust 92,800 lb. | Same report: “bypass ratio of 6.4”; “92,800 lb”. | PDF pp. 135–136, §1.6.4.1 | Checks candidate engine identity; it is not an in-flight thrust map. |
| The occurrence take-off weight was 223,469 kg, but that is not an end-of-flight prior. | Same report. | PDF pp. 95–96, weight table | Context only; no audit calculation uses this value. |

## OpenAP

| Audit claim | Primary source and located passage | Locator | Audit use |
|---|---|---|---|
| The published model is point-mass and does not explicitly carry AoA, sideslip, or angular rates. | [Sun, Hoekstra & Ellerbroek (2020)](https://resolver.tudelft.nl/uuid:c3ff6240-e5d7-46fa-a47c-77304f5c1c49): “angle of attack … side-slip angle and … angular rates, are not explicitly considered.” | Publisher PDF p. 4 / journal p. 392, §1–2 | Blocks use as a stall/post-stall or six-axis model. Retrieved PDF SHA-256 `cf77acf25536922867270a764b0511ada2cfcb330c0d8a7e70dc6eb5be41c141`. |
| The paper reports B772 clean-polar values cd0 0.034, k 0.051, e 0.723 and critical Mach 0.65. | Same paper. | PDF p. 13 / journal p. 401, Table 4 | Audit-only published comparator. |
| Its public aerodynamic validation example is B747, at M0.3 and alpha −5° to 30°, with the fit restricted through 15°. | Same paper. | PDF p. 11 / journal p. 399, §5.1 and Fig. 7 | Prevents describing the B772 coefficients as aircraft-validated. |
| B772 estimates came from roughly 100 Schiphol departures in March 2018; thrust/model uncertainty remains material. | Same paper. | PDF pp. 10–11 and 15–16 / journal pp. 398–399, 403–404 | Defines the empirical envelope and limitations. |
| The pinned dataset is version 2 under CC BY 4.0. | [Figshare record 11424924 v2](https://figshare.com/articles/dataset/Open_aircraft_performance_modeling_data/11424924/2), licence field “CC BY 4.0”. | Record metadata and file 20369382 | Permits reproducible coefficient/coverage statistics. ZIP SHA-256 `79e1a631597ec3984d0077ba62bfe10059464a9072773cae41117eabe271be4b`. |
| OpenAP v2.6.0 uses current B772 values 0.024/0.047/0.783 and lists PW4090 as default; Trent 892 is absent from the options. | [Pinned B772 aircraft YAML](https://github.com/junzis/openap/blob/4fb21d6e402fd1f4a48b191ad6801c74479e71f5/openap/data/aircraft/b772.yml) and [drag-polar YAML](https://github.com/junzis/openap/blob/4fb21d6e402fd1f4a48b191ad6801c74479e71f5/openap/data/dragpolar/b772.yml). | Exact fields under `engine`, `drag`, and `clean` | Runtime identity rejection and current-polar audit. Member hashes are pinned in the manifest. |
| Upstream changed the B772 polar from the paper values without a B772 validation artifact in that change. | [OpenAP commit `2ca2a05`](https://github.com/junzis/openap/commit/2ca2a05cc4c11fc7bff22f40f4098d06f229e62e), message “update drag polars”. | `openap/data/dragpolar/b772.yml` diff, 2020-12-07 | Makes the current coefficients non-admissible absent traceable validation. |
| OpenAP rejects an unlisted aircraft/engine pair unless `force_engine` is set; descent idle is 7% of available thrust. | [Pinned thrust implementation](https://github.com/junzis/openap/blob/4fb21d6e402fd1f4a48b191ad6801c74479e71f5/openap/thrust.py). | Constructor option guard and `descent_idle()` | Shows that forced Trent 892 and modeled idle are not flameout/windmilling evidence. |
| OpenAP source is LGPL-3.0-only at the pinned release. | [Pinned OpenAP licence](https://github.com/junzis/openap/blob/4fb21d6e402fd1f4a48b191ad6801c74479e71f5/LICENSE). | Complete licence file | Legal intake. Licence SHA-256 `e3a994d82e644b03a792a930f574002658412f62407f5fee083f2555c5f23118`. |

## FlightGear/YASim and JSBSim

| Audit claim | Primary source and located passage | Locator | Audit use |
|---|---|---|---|
| The modern GPL community 777 definition actively uses two GE90-115B jets at 115,540 lb and generic stall-shape values. | [Pinned `777-200ER-v2.xml`](https://github.com/franck-vmd/Boeing-777-Flightgear/blob/62396863bf567695b1137873bb939005accf85b3/777-VMD/777-200ER-v2.xml). | `<jet>` elements and wing `<stall>` element | Rejects engine identity and aircraft-validation claims. File SHA-256 `0d24ed659b6664af10d465ac71392405bb407c7a3b4d0a65efa64a5dbe129cb3`. |
| The modern repository is GPL-2.0-only. | [Pinned licence](https://github.com/franck-vmd/Boeing-777-Flightgear/blob/62396863bf567695b1137873bb939005accf85b3/LICENSE). | Complete licence file | Legal intake. Licence SHA-256 `8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643`. |
| The historical FGMEMBERS file uses 93,400-lb jets described in comments as Trent 895, not 892; no root/file licence was located. | [Pinned historical XML](https://github.com/FGMEMBERS/777/blob/371a354e5805c3c54afac926fea16bb19ea71fda/777-200ER.xml) and [repository tree](https://github.com/FGMEMBERS/777/tree/371a354e5805c3c54afac926fea16bb19ea71fda). | Header, `<jet>` elements, complete pinned tree inventory | Rejects identity and blocks redistribution. File SHA-256 `9efa7d64bbcd6e7b31f87d3c60552712191cf16d88d8e87f78c2baedcdf75ede`. |
| Official JSBSim v1.3.1 is a general LGPL flight-dynamics framework, but its complete model inventory has no 777/B772/Trent 892 path. | [JSBSim v1.3.1 source](https://github.com/JSBSim-Team/jsbsim/tree/3b25f25e49b42d0489c04ac805674fc1450ca579) and [licence](https://github.com/JSBSim-Team/jsbsim/blob/3b25f25e49b42d0489c04ac805674fc1450ca579/COPYING). | Complete tar member inventory under `aircraft/`, `engine/`, and `scripts/` | Distinguishes a simulator framework from a B777 model. Archive SHA-256 `69d410ec9281cd4b03d029c3430b99f3ff9d240a64f83a7479cf746fd8bdffff`. |

## Boeing/ATSB public trajectory cases

| Audit claim | Primary source and located passage | Locator | Audit use |
|---|---|---|---|
| ATSB says the engineering simulator used the same aerodynamic model as a Level D simulator. | [ATSB Search and debris examination update](https://www.atsb.gov.au/sites/default/files/media/5773389/ae-2014-054_mh370-search-and-debris-update_aug2017.pdf): “same aerodynamic model as a Level D simulator”. | PDF p. 10, End of flight simulations | Establishes provenance without claiming public access to the model. |
| ATSB warns some motion left the simulation database and later data require caution. | Same report: “outside the simulation database”. | PDF p. 11 | Prevents treating every output point as validated. |
| The ATSB report itself is CC BY 3.0 Australia, excluding identified third-party material. | Same report. | PDF p. 1, publishing information | Applies to the report, not automatically to Boeing files or the later CSV archive. |
| The ten public exports contain only one-second X, Y, and altitude; detailed case conditions were withheld for legal reasons. | [Iannello, End-of-Flight Simulations of MH370](https://mh370.radiantphysics.com/2018/08/19/end-of-flight-simulations-of-mh370/): “ATSB has permitted me to share these results on this blog”. | “Simulation Results”, published 2018-08-19, modified 2018-08-31 | Defines link-only intake and what can be independently reproduced. Archive SHA-256 `e400ac73478dff8698cd344a69d7969804f6adb0eb2121d5cacd3b58d63111db`. |
| The published high-rate partition is cases 3, 4, 5, 6 and 10; the reported post-threshold distance is 4.7–7.9 NM. | Same Iannello post. | Generalized observations under “Simulation Results” | Independent public B777 trajectory reproduction target. |
| ATSB gives a theoretical controlled-glide comparator of approximately 17:1. | [The Operational Search for MH370](https://www.atsb.gov.au/sites/default/files/media/5773565/operational-search-for-mh370_final_3oct2017.pdf): “unpowered glide ratio of approximately 17:1”. | PDF p. 99, Controlled glide or ditching | Comparator only; it is not used to tune either public polar. |

## Other public/restricted families

| Audit claim | Primary source and located passage | Locator | Audit use |
|---|---|---|---|
| ICAO/EASA publishes manufacturer-supplied emissions certification data; Trent 892 row 2RR027 reports 411.48 kN and four LTO fuel flows. | [EASA ICAO Engine Emissions Databank](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank), “provided by the engine manufacturers”. | 03/2026 workbook, `Gaseous Emissions and Smoke`, row UID 2RR027 | Engine identity/static-point check only. Workbook SHA-256 `57a9ff572458ad3a3141afc1aea932b5faa5796d279f0ac74600b27869302530`. |
| NASA TCM has generic extended-angle aerodynamics and generic 40,000-lbf engines, not B777 data. | [NASA/TM-2011-217169](https://ntrs.nasa.gov/citations/20110014509): “alpha: –5 to 85 deg, beta: ±45 deg”; “40,000 lbs”. | PDF pp. 10–11 and 14 | High-AoA/control family screen; no cross-aircraft transfer is inferred. PDF SHA-256 `22570bc60fd366a86ae2e3eb44dff7008a2764e5e3c31545c66ba758626800b5`. |
| NASA release LAR-17625-1 is open source by request and requires MATLAB/Simulink. | [NASA Software Catalog LAR-17625-1](https://software.nasa.gov/software/LAR-17625-1). | Software details and overview | Reproducibility/legal intake; still not a B777 candidate. |
| BADA requires reviewed access under a restricted, non-transferable licence. | [EUROCONTROL BADA Product Management Document](https://www.eurocontrol.int/sites/default/files/library/008_BADA_Product_management.pdf): “non-sublicenseable, non-transferable”. | Appendix B, licence agreement | Excludes BADA from a public redistributable source package. |

## Inferences made by this audit

The following are explicitly audit inferences, not source quotations:

- No single candidate meets all six admission requirements in `candidate-families.json`.
- Combining OpenAP, NASA TCM, and community YASim would mix incompatible model families without a public B777 transfer/uncertainty model.
- The public Boeing exports are the strongest B777 behavioral comparator but cannot reveal the coefficients, state, controls, or uncertainty needed for implementation.
- Therefore the exact admission is blocked and the implementation-ready parameter field remains `null`.
