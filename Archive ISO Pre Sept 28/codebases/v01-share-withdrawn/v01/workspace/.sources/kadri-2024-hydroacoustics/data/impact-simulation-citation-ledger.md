# Impact-simulation source-to-claim citation ledger

Each row records a located passage from a retrieved full-text source. None of
these passages establishes that MH370 generated, or failed to generate, a
detectable hydroacoustic signal.

| Source and pinpoint | Short exact passage/result | Model use | Boundary |
| --- | --- | --- | --- |
| Malaysian Safety Investigation Report (2018), p. 97 (printed p. 51), Table 1.6D, extracted chunk `p0097:c01` | “Actual Take-Off Weight 223,469 kg”; “Zero Fuel Weight 174,369 kg”; “Take-Off Fuel 49,100 kg” | The actual ZFW of 9M-MRO on the final loadsheet is used as a fuel-exhaustion impact-mass surrogate | This is not a measured mass at 00:19 UTC. Actual impact mass is unknown and could include residual or unusable fuel. |
| Bisagni and Pigazzini (2018), p. 2, chunk `p0002:c02` | “maximum descending rate is 1.5 m/s” | Controlled-ditching class upper reference | Generic ditching class, not a 777 impact model. |
| Same, p. 11, chunk `p0011:c01` | “horizontal velocity ... generates complex hydrodynamic phenomena” | Prevents treating normal kinetic energy as a complete ditching model | Source discusses simplified modelling. |
| NTSB Flight 1549 report (2010), PDF p. 40, Table 2 | Accident-flight values: mass 151,017 lb; pitch 9.5°; airspeed 125 knots; glideslope −3.5°; descent rate 12.5 fps; average/maximum external pressure 15.1/22.6 psi | Low-energy contact-state and load validation case | A320 ditching evidence, not a 777 impact or remote-acoustic calibration. |
| Same, PDF p. 65 | “touched down ... at an airspeed of 125 KCAS with a pitch angle of 9.5° and a right roll angle of 0.4°”; calculated descent 12.5 fps, flightpath −3.4°, AOA 13°–14°, sideslip 2.2° | Complete measured contact kinematics for a reduced hydrodynamic validation case | No hydrophone observation or surface-to-SOFAR efficiency is reported. |
| Same, PDF p. 95 | The 12.5-fps impact generated pressures sufficient for “large-scale collapse and failure” and cracking that allowed water ingress | Contact-load/damage outcome for validation | Aircraft and water-entry conditions differ; this does not identify acoustic energy. |
| Holland (2018), p. 10, Table VII, chunk `p0010:c01` | “00:19:37Z 13,800 fpm ... 25,300 fpm” | Unarrested high-rate family endpoints | Conditional BFO-model result; triangular weighting is our assumption. |
| Brown et al. (2026), p. 10, chunk `p0010:c01` | “P peak = 52.4 × 10^6 (R/W^(1/3))^−1.13” | Reduced-order explosion-equivalent pressure relation | `R` in metres and `W` in kg TNT deposited in SOFAR; not validated for aircraft impacts. |
| Same, p. 18, chunk `p0018:c01` | “impacting kinetic energy of 900 ± 200 MJ” | F-35 empirical energy analogue | Different aircraft and impact conditions. |
| Same, p. 18, chunk `p0018:c01` | “observed peak pressure of 0.7 Pa at H11 ... range of 3300 km” | Independent numerical check of pressure scale | Does not calibrate H01W/H08S receiver noise. |
| Same, p. 18, chunk `p0018:c01` | “coupling efficiency from the surface to the SOFAR channel is of order 10−4” | Centre of one explicit sensitivity prior | Order-of-magnitude anchor, not an MH370 coupling posterior. |
| Same, p. 18, chunk `p0018:c01` | Aircraft breakup, fuel, impact angle and “penetration depth-time history” can change coupling; the relatively shallow local SOFAR channel may make the inferred efficiency high | Required limitation on transfer from the F-35 example | Prevents treating \(10^{-4}\) as a universal aircraft-impact efficiency or waveform. |
| Farrell, *HydroCAM User's Guide* (1997), p. 14, chunk `p0014:c01` | “transformation into detection probability requires a model for the receiver output statistics and specification of a detection threshold” | Prevents pressure proxies being labelled detection probabilities | Raw receiver statistics and a declared detector are unavailable. |
| Kadri (2024), p. 10, chunk `p0010:c02` | “kinetic energy of 4 GJ, equivalent to 956 kg of TNT” | Comparator kept separate from effective acoustic yield | Energy-unit conversion is not demonstrated surface-to-SOFAR efficiency. |

## Public-tool and environmental-data passages

Web passages were located on 25 August 2026. These sources establish capability
or data availability, not validation for an aircraft impact.

| Source and located passage | Design use | Boundary |
| --- | --- | --- |
| [DualSPHysics formulation, lines 589–596](https://github.com/DualSPHysics/DualSPHysics/wiki/3.-SPH-formulation): Project Chrono supports rigid/flexible parts and fluid–solid interaction; the present coupling uses rigid-body, constraint and collision components | Candidate free-surface/multi-body solver | Flexible aircraft breakup is not supplied by the cited present coupling. |
| [Acoustics Toolbox overview, lines 2010–2063](https://github.com/oalib-acoustics/Acoustics-Toolbox/blob/main/index.htm): BELLHOP/BELLHOP3D are ray codes, KRAKEN a normal-mode code, SCOOTER a finite-element FFP code and SPARC a time-domain FFP code | Path-propagation model family | Does not supply the aircraft source or acoustic–gravity coupling model. |
| [GEBCO grid description, lines 3–5 and 28–35](https://www.gebco.net/data-products/gridded-bathymetry-data): global 15-arc-second elevation grid with direct and OPeNDAP access | Path bathymetry | Resolution and source-data quality vary by region. |
| [Copernicus GLORYS12V1 description](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description): 1/12-degree, 50-level daily/monthly ocean reanalysis covering 1993 onwards with temperature and salinity | March 2014 path-specific sound-speed profiles | Reanalysis uncertainty must be propagated; it is not an in-situ station profile. |
| [NOAA World Ocean Atlas, lines 305 and 434–445](https://www.ncei.noaa.gov/products/world-ocean-atlas): temperature and salinity at standard depths; climatological means and uncertainty fields are available | Independent climatological sound-speed control | Long-term climatology is not contemporaneous March 2014 ocean state. |
| [Boeing plan manuals, lines 38–42](https://www.boeing.com/commercial/airports/plan-manuals): public 777-200/200ER/300 airport-planning manual | External dimensions and geometric control | Not structural CAD, material properties or a breakup finite-element model. |

## Retrieved-file identities

| Source | SHA-256 |
| --- | --- |
| Malaysian 2018 safety investigation report | `b39fa554b38c8e156fbb0f09567de0baf32bafaf012b0f2b80133745f3ed1f32` |
| Bisagni and Pigazzini published-version PDF | `64ae0200e6ea545ba7e20edf7ca2f910706cb8f430963f187ff1d1e6324059d8` |
| NTSB Flight 1549 final report | `fe9e1733e8400f3ea9ce0832f36d934c829ac369e8a66765dc423d18973640ef` |
| Holland 2018 BFO v3 | `c76dd9f1b6c341e99d95c68002202aad7ba6797eb1f1b343f00468235cd22821` |
| Brown et al. hydroacoustic-bolides preprint | `4b45d454bba9e563b568e81c7e64d28ba92e6195650cb028a97230a417a967f8` |
| Farrell HydroCAM guide | `d4d5902f0654f9a52958026d979ef9963da76c2ed29776bd826263c79c73fa68` |
| Kadri 2024 official PDF | `b4f8f37ad1577a0f4726e6acdbfeea295b89197c88fac4ab5546d80bd9eb9db4` |
