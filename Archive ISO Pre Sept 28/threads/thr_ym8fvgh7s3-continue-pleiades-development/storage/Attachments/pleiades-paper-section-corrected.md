# Pléiades imagery: morphology and conditional source-location analysis

<!-- Narrative is constrained by an invariant test to 500–650 words; table rows and references are excluded. -->

On 23 March 2014 near 04:00 UTC, Pléiades 1A acquired four 0.5 m
southern Indian Ocean scenes. Geoscience Australia analysed imagery supplied by
French military intelligence and CNES at the ATSB's request (Minchin et al.,
2017). Twelve of at least 70 catalogued objects were rated 5 (probably not
natural objects or features). This did not identify aircraft debris. Targets
06, 18, 19, 26 and 27 were retained by mask-stability screening; other rating-5
objects had weaker geometry. Correspondence-qualified perturbations (baseline
mask IoU ≥0.25) set size intervals: 15/18 for object 06 and 18/18 for every
other target; three rejects had switched components. Selection measured
segmentation stability, not aircraft resemblance.

Eight equal-sized families covered flooding-model and random-pose wings; other
777 parts; matched random geometry; ocean controls; the whole fuselage; and
documented-boundary or random-cut sections. Boeing geometry was used (Boeing
Commercial Airplanes, 2024). Controls represented containers, nets/ropes,
clustered cargo/plastic/timber, wreckage/hulls and fish-aggregating devices
(Hapag-Lloyd, 2016; Indian Ocean Tuna Commission, 2023; Lebreton et al., 2018).
Murphy (2013) gives six 777 section intervals, including BS 2150 at the aft
pressure bulkhead. These reproducible boundaries are not asserted weak points.
Reported Asiana separation, local 777 puncture and A320 aft damage (Air
Accidents Investigation Branch, 2010; National Transportation Safety Board,
2010, 2014) do not define an MH370 breakup prior.

Each family contained 3,372 masks: 26,976 masks and 134,880 family–object
comparisons. Fuselage orientation was isotropic; one fifth were fully visible,
otherwise a linear waterline targeted 15–100% visibility. These were coverage
sensitivities, not probabilities. Eligibility required visible area, oriented
length and width each between the target's lower and upper limits.
Principal-axis-normalised masks were compared under identity and three
reflections. For candidate \(c\), target \(o\), family \(g\), masks
\(T_o,P_o\), reflection set \(\mathcal F\), and eligible set \(E_o\),

\[
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|},\quad
\ell(c,o)=1-\frac{\max_{f\in\mathcal F}\operatorname{IoU}(T_o,f(c))+
\max_{f\in\mathcal F}\operatorname{IoU}(P_o,f(c))}{2},\quad
\ell^{*}_{g,o}=\min_{c\in g\cap E_o}\ell(c,o).
\]

Lower loss is greater overlap, not an identity probability.

Extended minima were an ocean-control fishing-net-or-rope mask (06), matched
random geometry (18/19), a random-pose wing (26), and documented section 47
(27). Object-06 ocean and random-geometry losses differed by 0.0007.
Section 47 scored 0.3058 versus 0.3145 for random geometry, but 0.3556 with fully visible masks. The whole shell ranked lowest for none; its
minima required axis/view cosines 0.885–0.988 and visible fractions 0.305–0.672:
near-end-on, occluded, or both. Random geometry matched dimension ranges, not outlines. 777 shapes were admissible but
not preferentially selected; morphology remained non-specific.

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

For conditional source location, Griffin and Oke (2017) propagated debris
forward from trial sites assuming some objects were from 9M-MRO. A separate
clean-sheet forward-ensemble reconstruction released particles from 5,289
cells along and within ±100 NM of the seventh arc. BRAN2016 and OSCAR v2 were
evaluated separately (Earth & Space Research and Dohan, 2021), with common NCEP
winds (Kalnay et al., 1996), three windage alternatives and 5 NM/day
dispersion. All twelve location likelihoods were averaged equally; no object
was randomly drawn. The five-object set was a sensitivity.

BRAN's mode was 35.418°S, 92.886°E with a 24,309 km² 90% region; OSCAR's was
34.917°S, 92.047°E with 18,393 km². Averaging
uniform subsets of one to five objects reproduces that PDF for any subset-size
prior; a product needs correlated debris and detection models. The 50:50
BRAN–OSCAR prior mixture has mode 35.300°S, 92.891°E and a 25,896 km² 90%
region. It is not independent-evidence multiplication or a calibrated
posterior. These are conditional hypotheses for an integrated estimator; none
establishes identity or updates the main estimate unconditionally.

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

Murphy, B. (2013). *Structures Group Chairman's Factual Report: Boeing
777-200 Series HL7742*. DCA13MA120. National Transportation Safety Board,
Washington, DC.
[Official report](https://data.ntsb.gov/Docket/Document/docBLOB?FileExtension=pdf&FileName=Structures+7-Factual+Report+of+Group+Chairman-Master.pdf&ID=398690).
Accessed 25 August 2026.

National Transportation Safety Board. (2010). *Loss of Thrust in Both Engines
After Encountering a Flock of Birds and Subsequent Ditching on the Hudson
River: US Airways Flight 1549, Airbus A320-214, N106US, Weehawken, New Jersey,
January 15, 2009*. Aircraft Accident Report NTSB/AAR-10/03. National
Transportation Safety Board, Washington, DC.
[Official report](https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1003.pdf).
Accessed 25 August 2026.

National Transportation Safety Board. (2014). *Descent Below Visual Glidepath
and Impact With Seawall: Asiana Airlines Flight 214, Boeing 777-200ER, HL7742,
San Francisco, California, July 6, 2013*. Aircraft Accident Report
NTSB/AAR-14/01. National Transportation Safety Board, Washington, DC.
[Official report](https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1401.pdf).
Accessed 25 August 2026.
