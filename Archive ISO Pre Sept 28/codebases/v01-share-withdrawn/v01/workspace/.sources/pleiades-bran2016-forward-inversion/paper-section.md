# Pléiades imagery: morphology and conditional source-location analysis

<!-- Narrative is constrained by an invariant test to 500–650 words; table rows and references are excluded. -->

On 23 March 2014, Pléiades 1A acquired four 0.5 m
southern Indian Ocean scenes. At the ATSB's request, Geoscience Australia
analysed imagery from French military intelligence and CNES (Minchin et al.,
2017). Twelve of at least 70 objects were rated 5 (probably not natural objects
or features). This did not identify aircraft debris. Targets 06, 18, 19, 26 and
27 were retained because repeated public-panel segmentation was stable (15/18
size-qualified trials for 06; 18/18 otherwise), not because they resembled aircraft.

Eight equal-sized families covered 777 parts, matched random geometry, ocean
controls, and whole, documented or random fuselage sections. Boeing geometry
(Boeing Commercial Airplanes, 2024) supplied shapes; controls included containers,
nets, cargo/plastic/timber, hulls and fish-aggregating devices (Hapag-Lloyd,
2016; Indian Ocean Tuna Commission, 2023; Lebreton et al., 2018). Murphy (2013)
gives six reproducible section boundaries; they are not asserted weak points or an MH370 breakup prior.

Each family contained 3,372 masks (26,976; 134,880 family–object
comparisons). Fuselage orientation was isotropic; 20% were fully visible and
the remainder used 15–100% linear-waterline coverage. Eligibility required
area, length and width within both limits. These were sensitivities, not
probabilities. Principal-axis-normalised masks used four reflections. For
candidate \(c\), target \(o\), family \(g\), masks \(T_o,P_o\),
reflections \(\mathcal F\), and eligible set \(E_o\),

\[
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|},\quad
\ell(c,o)=1-\frac{\max_{f\in\mathcal F}\operatorname{IoU}(T_o,f(c))+
\max_{f\in\mathcal F}\operatorname{IoU}(P_o,f(c))}{2},\quad
\ell^{*}_{g,o}=\min_{c\in g\cap E_o}\ell(c,o).
\]

Lower loss is greater overlap, not an identity probability.

Extended minima were an ocean net/rope control (06), matched random geometry
(18/19), a random-pose wing (26), and documented section 47 (27). Object-06
ocean and random losses differed by 0.0007. Section 47 scored 0.3058, but
0.3556 when fully visible. The whole shell ranked lowest for none.
Dimension-matched random controls therefore left 777 shapes admissible but
non-specific.

Object 18's complete-wing PCA minimum was unconstrained. In a post-hoc
hydrostatic sensitivity, none of 168 original flooding states matched; 10/24
multistart refinements met the 25%-per-slope and strict-size criteria. All
required an absent engine, flooded midspan/tip cells and inboard-only buoyancy.
The closest four-height RMSE was 0.796 m and PCA loss 0.3421, versus 0.2730
unconstrained. The cells are not Boeing tank bays. Integral tanks and protected
engine separation make residual buoyancy possible, but atmospheric venting and
no documented sealed inboard bay leave it unsupported (Air Accidents
Investigation Branch, 2010; Ministry of Transport Malaysia, 2018; National
Transportation Safety Board, 2014). Target fitting and unequal budget exclude
it from the ranking.

| Family | Objects with a size-eligible candidate | Mean lowest loss* | Objects at lowest loss |
| --- | ---: | ---: | ---: |
| Flooding-model wing | 1/5 | 0.3286 | 0 |
| Random-pose wing | 5/5 | 0.3232 | 1 |
| Other shortlisted 777 parts | 4/5 | 0.3704 | 0 |
| Matched random geometry | 5/5 | 0.3267 | 2 |
| Generic ocean objects | 4/5 | 0.3532 | 1 |
| Whole 777 fuselage | 4/5 | 0.3472 | 0 |
| Documented 777 fuselage sections | 5/5 | 0.3318 | 1 |
| Random 777 fuselage sections | 4/5 | 0.3388 | 0 |

\*Mean over eligible objects only; family means are therefore not directly
comparable.

For source location, Griffin and Oke (2017) propagated debris forward
conditional on some objects being from 9M-MRO. A clean-sheet ensemble released
particles from 5,289 cells within ±100 NM of the seventh arc. BRAN2016, OSCAR
v2 (Earth & Space Research and Dohan, 2021), and GLORYS12 currents plus WAVERYS
Stokes drift (E.U. Copernicus Marine Service Information, 2023, 2024) were
alternatives. Common NCEP winds (Kalnay et al., 1996), three windages and 5
NM/day dispersion were used. All twelve location likelihoods were averaged
rather than drawing one object; the five retained targets formed a sensitivity.

Modes were 35.418°S, 92.886°E for BRAN (24,309 km² 90% region); 34.917°S,
92.047°E for OSCAR (18,393 km²); and 35.391°S, 92.163°E for GLORYS12/WAVERYS
(22,123 km²). Pairwise total variation was 0.484–0.570 and mode separation
53.8–94.4 km. An equal-prior mixture has mode 35.218°S, 92.247°E and a 28,768
km² region. It is neither independent-evidence multiplication nor a calibrated
posterior. The PDFs enter the integrated estimator only under the conditional
image-debris hypothesis and provide no unconditional update.

## References

Air Accidents Investigation Branch. (2010). *Report on the Accident to Boeing
777-236ER, G-YMMM, at London Heathrow Airport on 17 January 2008*. Aircraft
Accident Report 1/2010. Air Accidents Investigation Branch, Farnborough.
[Official report](https://assets.publishing.service.gov.uk/media/5422f3dbe5274a1314000495/1-2010_G-YMMM.pdf).
Accessed 25 August 2026.

Boeing Commercial Airplanes. (2024). *777-200/200ER/300 Airplane
Characteristics for Airport Planning*. Document D6-58329, Revision E. Boeing
Commercial Airplanes.

Earth & Space Research and Dohan, K. (2021). *Ocean Surface Current Analyses
Real-time (OSCAR) Surface Currents—Final 0.25 Degree (Version 2.0)*. Version
2.0. NASA Physical Oceanography Distributed Active Archive Center. Dataset.
[https://doi.org/10.5067/OSCAR-25F20](https://doi.org/10.5067/OSCAR-25F20).
Accessed 24 August 2026.

E.U. Copernicus Marine Service Information. (2023). *Global Ocean Physics
Reanalysis*. Product GLOBAL_MULTIYEAR_PHY_001_030. Marine Data Store. Dataset.
[https://doi.org/10.48670/moi-00021](https://doi.org/10.48670/moi-00021).
Accessed 26 August 2026.

E.U. Copernicus Marine Service Information. (2024). *Global Ocean Waves
Reanalysis*. Product GLOBAL_MULTIYEAR_WAV_001_032, dataset
cmems_mod_glo_wav_my_0.2deg_PT3H-i. Marine Data Store. Dataset.
[https://doi.org/10.48670/moi-00022](https://doi.org/10.48670/moi-00022).
Accessed 26 August 2026.

Griffin, D. A. and Oke, P. R. (2017). *The Search for MH370 and Ocean Surface
Drift—Part III*. Report EP174155. CSIRO Oceans and Atmosphere, Australia.
[https://doi.org/10.4225/08/599344b9beead](https://doi.org/10.4225/08/599344b9beead).

Hapag-Lloyd. (2016). *Container Specification*. Hapag-Lloyd.

Indian Ocean Tuna Commission. (2023). *Regional Observer Scheme Scientific
Field Observer Manual*. Indian Ocean Tuna Commission.

Kalnay, E., Kanamitsu, M., Kistler, R., Collins, W., Deaven, D., Gandin, L.,
Iredell, M., Saha, S., White, G., Woollen, J., Zhu, Y., Chelliah, M.,
Ebisuzaki, W., Higgins, W., Janowiak, J., Mo, K. C., Ropelewski, C., Wang, J.,
Leetmaa, A., Reynolds, R., Jenne, R. and Joseph, D. (1996). The NCEP/NCAR
40-Year Reanalysis Project. *Bulletin of the American Meteorological Society*,
77, 437–471.
[https://doi.org/10.1175/1520-0477(1996)077%3C0437:TNYRP%3E2.0.CO%3B2](https://doi.org/10.1175/1520-0477%281996%29077%3C0437%3ATNYRP%3E2.0.CO%3B2).

Lebreton, L., Slat, B., Ferrari, F., Sainte-Rose, B., Aitken, J., Marthouse,
R., Hajbane, S., Cunsolo, S., Schwarz, A., Levivier, A., Noble, K., Debeljak,
P., Maral, H., Schoeneich-Argent, R., Brambini, R. and Reisser, J. (2018).
Evidence that the Great Pacific Garbage Patch is rapidly accumulating plastic.
*Scientific Reports*, 8, 4666.
[https://doi.org/10.1038/s41598-018-22939-w](https://doi.org/10.1038/s41598-018-22939-w).

Minchin, S., Mueller, N., Lewis, A., Byrne, G. and Tran, M. (2017). *Summary
of Imagery Analyses for Non-Natural Objects in Support of the Search for
Flight MH370: Results from the Analysis of Imagery from the PLEIADES 1A
Satellite Undertaken by Geoscience Australia*. Record 2017/13. Geoscience
Australia, Canberra.
[https://doi.org/10.11636/Record.2017.013](https://doi.org/10.11636/Record.2017.013).

Ministry of Transport Malaysia. (2018). *Safety Investigation Report MH370
(9M-MRO)*. Ministry of Transport Malaysia, Putrajaya, Malaysia.
[Official report](https://www.mot.gov.my/en/AAIB%20Statistic%20%20Accident%20Report%20Document/A%200514%209M-MRO%20MH370.pdf).
Accessed 26 August 2026.

Murphy, B. (2013). *Structures Group Chairman's Factual Report: Boeing
777-200 Series HL7742*. DCA13MA120. National Transportation Safety Board,
Washington, DC.
[Official report](https://data.ntsb.gov/Docket/Document/docBLOB?FileExtension=pdf&FileName=Structures+7-Factual+Report+of+Group+Chairman-Master.pdf&ID=398690).
Accessed 25 August 2026.

National Transportation Safety Board. (2014). *Structures Group Chairman's
Factual Report: Addendum 1, Boeing Fuel Tank Report*. DCA13MA120. National
Transportation Safety Board, Washington, DC.
[Official report](https://data.ntsb.gov/Docket/Document/docBLOB?FileExtension=pdf&FileName=Structures+7-Addendum+1+Boeing+Fuel+Tank+Report+24+embedded+Figures-Photos-Master.pdf&ID=398832).
Accessed 26 August 2026.
