# Recovered-debris evidence audit

This file separates reported observations, official identity assessments, and
ocean-drift model choices. The product does not read this directory; selected
records are rendered into runner configuration and the runner records that
configuration's hash.

## Evidence selections

The source audit in `inputs/debris-evidence-audit.csv` contains the 41 supplied
reports. It does not treat them as 41 MH370 observations.

- **Stringent nine-object set:** the nine confirmed or almost-certain objects
  used by Durgadoo et al. through June 2016. This is the primary multi-debris
  comparator because its identity filter does not depend on an arbitrary
  confidence weight and can be recreated against a peer-reviewed method.
- **Expanded dated official set:** 20 dated objects classified confirmed,
  almost certain, highly likely, or likely by Malaysia through January 2017.
  It is a sensitivity only. Several identity conclusions partly use agreement
  with the CSIRO drift model, so those rows are marked
  `identity_uses_prior_drift=yes`; feeding them back as independent drift
  observations would be circular.
- **Catalog-only high-confidence item:** the Sandravinany cabin-floor panel is
  retained in the audit but excluded from temporal likelihood because the
  published discovery interval spans late 2016 through late 2017.
- **Excluded reports:** unidentified, possible, unanalysed, coordinate-proxy,
  and unofficial objects remain visible in the audit but do not enter either
  selected likelihood.

The two same-area June 2016 Madagascar episodes contain several objects. Each
episode is one recovery likelihood factor. Object count remains reported, but
rows are not multiplied as independent beaching events.

The reproducible primary configuration is
`outputs/cmems-glorys12-waverys-multi-debris.toml`: nine objects in nine
recovery episodes plus two independently propagated Australian non-recovery
populations. The separately labelled
`outputs/cmems-glorys12-waverys-cabin-windage-sensitivity.toml` applies the 3%
total-leeway control to the two uncertain recovered interior panels without
claiming it is measured. The separately labelled
`outputs/cmems-glorys12-waverys-expanded-debris-sensitivity.toml` contains 20
objects in 17 episodes. It does not erase the audit's circularity flags and
cannot become primary merely by producing a narrower profile.

## Dates and coordinates

Dates are discovery dates, never asserted beaching dates. Durgadoo's nine-item
table and the Malaysian summary disagree on the reported date of the Mossel
Bay engine-cowling piece and differ by a few days for some other pieces. The
stringent comparator follows the dates used by Durgadoo; alternative published
dates must be a separate sensitivity, not silently reconciled.

Coordinates are reported beach/locality points transcribed in the earlier
inventory. They are not measurements of the exact coastal arrival point.
Spatial bandwidth and discovery-delay distributions therefore remain explicit
run parameters.

## Discovery-delay models

The published-method comparator uses a uniform 0--30 day arrival-to-discovery
delay, matching Durgadoo's leeway sensitivity. A conservative delayed-discovery
sensitivity uses piecewise-uniform bins and is reported separately. The bins
are probability masses, not likelihood powers. No item is assigned an exact
beaching date, and no uncalibrated refloating process is hidden in transport.

## Object-motion and environmental families

The isotope screen belongs only to the confirmed Réunion flaperon. The other
objects do not inherit the flaperon's barnacle record or empirical leeway.

The stringent comparator uses the published low-exposure response for the
eight non-flaperon pieces found on African or western-Indian-Ocean shores.
CSIRO described those recovered pieces as having little or no exposure to the
wind; it did not measure a 3% law for the recovered cabin panels. The panels
remain a separate named family so a 3%-total-leeway sensitivity can be run
without pretending it is a measurement. Direct windage is enabled only when a
separately supplied wind field is recorded.

CSIRO's 3% high-windage control is total current-relative leeway. Its own
glossary warns that an effective windage factor also contains Stokes when the
current field omits Stokes. The corresponding sensitivity therefore uses 3%
of 10 m wind with zero separately added Stokes; adding full Stokes plus 3%
would double count part of the response. The measured flaperon comparator is
different: full Stokes plus the observed 0.10 m/s extra response, 20 degrees
left of wind.

Not integrated: an early multi-debris diagnostic added full WAVERYS Stokes and
3% wind response to the recovered interior panels. That both double-counted
part of CSIRO's effective leeway and treated an unobserved-debris control as a
measured panel law. Its exact run was moved out of canonical outputs after the
source audit exposed the conflation.

Adaptive transport is event-targeted: each independent recovery episode gets
the declared particles-per-cell budget and its own deterministic keyed random
stream, proposal history, correction weights, and termination accounting. This
prevents a union proposal from spending nearly all of its rare-event effort on
the easiest one of several destinations. When one co-recovery episode contains
objects assigned to different defensible motion laws, the episode is counted
once using the least-suppressive compatibility across those laws. This is a
conservative profile, not an uncalibrated mixture weight or a product of the
same discovery episode. Hypothetical Australian non-recovery populations have
no arrival destination and therefore use separate independent forward
ensembles rather than an artificial recovery proposal.

CSIRO/Pleiades provides useful model diversity, not an extra recovered-debris
observation. Part III compared BRAN2015 and BRAN2016, added 5 NM/day unresolved
random walks, and used 1.2% wind response for low-exposure objects. Its
35.6 degrees south scenario is conditional on the unconfirmed image objects.
It must not be inserted as a recovery datum or used as a prior for this spoke.

GLORYS12/WAVERYS, native HYCOM, BRAN, and GDP are incompatible environmental
families and must be reported separately. No subjective equal-weight mixture
is accepted. A future current-family mixture requires out-of-sample drifter
prediction weights that include failed trajectories; object-response weights
need corresponding held-out object data.

BRAN2016 is not used for the full-period recovered-debris run. The current NCI
catalog is reachable, but the attached CSIRO terms require prior registration
of the user and intended use, restrict the licence to government-funded
research, and make it non-transferable and revocable. This thread has no basis
to accept those terms on Pete's behalf. The short March 2014 BRAN derivative
in the independent Pléiades source recreation is neither full-period coverage
nor evidence that the present use is licensed. Until CSIRO authorizes this use,
BRAN is a precisely recorded model-diversity blocker rather than a current
family silently substituted into the runner. GLORYS12/WAVERYS remains the
scientifically explicit full-period alternative.

## Australian non-recovery

CSIRO treated the absence of Australian findings as informative while noting
lower observer density and high reporting awareness. The runner represents
this as zero reported recoveries within an explicit western-Australia bounds
box and time interval. Its `expected_reportable_items` is a Poisson exposure
sensitivity, because reporting effort is not calibrated. A field failure
before the observation interval ends is conservatively counted as unresolved
and receives the same penalty as a possible Australian landfall; missing data
can never improve compatibility.

Australian non-recovery is propagated through two independent hypothetical
debris populations rather than attached to the particular objects recovered
in Africa: a low-exposure population with explicit Stokes, and CSIRO's 3%
total-leeway high-windage control without separately added Stokes. Each uses a
weak Poisson exposure of 0.5 expected reportable findings if every trajectory
reached the observation region. This total exposure of 1.0 is an explicit
sensitivity for unknown debris count, waterlogging, observer effort, and
reporting—not an estimate derived from the number of selected recovered
objects. These non-recovery populations use independent forward ensembles;
they are not rare-arrival proposals targeted on an African recovery.

## Source files and integrity

| Source | Public record | Local SHA-256 |
|---|---|---|
| Malaysian Safety Investigation Team, *Summary of Possible MH370 Debris Recovered*, updated 30 Dec 2018 | <https://www.mot.gov.my/en/Laporan%20MH%20370/Summary%20of%20Debris%20Recovered%20-%20Updated%2030%20Dec%202018.pdf> | `369b511262cca74dc8b00bd2f272471760f59755acb6d1189b9cf4068c9c1b82` |
| Malaysian Safety Investigation Team, debris examination report, Feb 2017 | Malaysian Ministry of Transport MH370 investigation appendices | `08f17b56f65151fbc18c3433f77854f50ae24802df93dc8e04b99e95a3d76594` |
| Durgadoo et al., *Strategies for simulating the drift of marine debris* | <https://doi.org/10.1080/1755876X.2019.1602102> | `68829c0892a980cd54eabc89a4c9a79ed15d7fe8f454af27b4c77e1879a7d1f0` |
| CSIRO, *The search for MH370 and ocean surface drift* | <https://www.atsb.gov.au/csiro-mh370-drift-reports> | `2aaebc93eeb02903cff2a6c0f5c14909e81b698580d931ce9ef647473144db54` |
| CSIRO, ocean drift Part II | <https://www.atsb.gov.au/csiro-mh370-drift-reports> | `42f1d128046339ad65c21aea84c5eae44f2ed38f1051a0a92fd0d52cd839cbaa` |
| CSIRO, ocean drift Part III | <https://www.atsb.gov.au/sites/default/files/media/5773371/mh370_csiro-ocean-drift-iiil.pdf> | `66df719be1b683632f36d1fafce2682f150297e5545e041e72874b0be1c438a0` |
| CSIRO/NCI, BRAN2016 access terms | <https://thredds.nci.org.au/thredds/fileServer/gb6/BRAN/BRAN_2016/gb6_license.txt> | `d4bdc483ba03bfbe3c3e178df24e2d8d368122bf19084a97752ea680f461384e` |

## Located-passage ledger

| Claim | Source | Locator | Located passage | Status |
|---|---|---|---|---|
| Nine of the 20 pieces recovered through June 2016 were confirmed or almost certain. | Durgadoo et al. | PDF p. 4, Materials and methods | “20 pieces ... of which 9 were identified as ‘confirmed’ or ‘almost certain’” | Supports stringent selection |
| Durgadoo used daily 1/12-degree delayed-mode assimilative currents and matching Stokes drift. | Durgadoo et al. | PDF p. 4, Model data | Daily CMEMS global 1/12-degree surface velocities through 26 July 2016; daily HRES-WAM Stokes was added separately. | Supports comparator forcing |
| Discovery can substantially post-date arrival. | Durgadoo et al. | PDF p. 4 and p. 12 | Discovery date might differ substantially from true arrival; precise arrival times would refine the result. | Supports delay distribution |
| Durgadoo's reference forward calculation was extremely large. | Durgadoo et al. | PDF p. 5, reference experiments | Approximately 22 million independent forward objects were released on 8 March 2014. | Supports adaptive rare-event need |
| Stokes response materially changes inferred source area. | Durgadoo et al. | PDF pp. 6--7 | Stokes is comparable with currents in the gyre; response sensitivities span 50--150 percent. | Supports separate sensitivity families |
| The nine-item calculation is limited by common object properties and unknown arrivals. | Durgadoo et al. | PDF pp. 9 and 12 | The method assumes the same drift properties; delayed discoveries can shift the inferred origin. | Limits direct multiplication |
| Several official likely classifications reuse CSIRO drift consistency. | Malaysian debris examination report | PDF pp. 9, 14, 21, 24, 27, 43, 48 | Each section cites consistency with CSIRO drift as part of its MH370 identity conclusion. | Excludes these rows from non-circular primary set |
| The almost-certain cabin panel has an aircraft-specific independent basis. | Malaysian debris examination report | PDF p. 39 | Decorative laminate matched the Malaysia Airlines 777 cabin specification. | Supports stringent identity |
| No Australian recovery is informative but observation effort is imperfect. | CSIRO Part I | PDF p. 23 (report p. 17) | Observer density is lower, while awareness and reporting likelihood were considered high. | Supports explicit sensitivity, not certainty |
| CSIRO distinguished an unobserved higher-windage debris population. | CSIRO Part II | PDF pp. 20--21 and glossary p. 23 | Small buoyant items not recovered were assigned 3% total current-relative leeway; the glossary states that effective windage contains Stokes when the current estimate omits it. | Supports a separate non-recovery population and forbids adding full Stokes plus 3% |
| Measured flaperon motion does not precisely locate the crash by itself. | CSIRO Part II | PDF p. 23 | The measured-response arrival was consistent with source latitudes from about 40 south to 30.5 south. | Limits flaperon-only localization |
| Pleiades drift model diversity included two BRAN versions. | CSIRO Part III | PDF pp. 18--22 | BRAN2015 and BRAN2016 were compared; unresolved turbulence used 5 NM/day random walks. | Supports BRAN comparator |
| The Pleiades scenario used conditional image evidence. | CSIRO Part III | PDF p. 23 | The 35.6 south simulation checks consistency with image objects and later non-recoveries/recoveries. | Excludes it as recovered-debris evidence |
| Full-period BRAN use needs authorization that this thread cannot assume. | CSIRO/NCI BRAN2016 access terms | Clauses 1, 4--5, 10, and 16 | Prior registration and intended-use disclosure are required; use is limited to government-funded research under a non-transferable, revocable licence. | Blocks unapproved BRAN retrieval |

All ledger claims above were checked against the locally hashed PDFs rather
than copied from secondary summaries.
