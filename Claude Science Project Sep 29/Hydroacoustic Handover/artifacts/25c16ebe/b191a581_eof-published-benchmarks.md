# Published end-of-flight benchmarks for MH370 (9M-MRO, Boeing 777-200ER)

An independently assembled sheet of published quantitative end-of-flight claims, for use as
calibration and sanity-check targets for a Monte Carlo end-of-flight simulator. Companion file:
`eof-published-benchmarks.csv` (91 rows, one row per claim).

Scope note: this is a record of what the retrievable literature states. It contains no new
analysis, no interpolation between published values, and no opinion about where the aircraft is.
Every row carries its source, identifier, provenance strength and conditions of validity.

## What was and was not retrieved

Retrieved in full: Holland (2018) via the arXiv v3 accepted preprint; Davey et al. (2016) via the
SpringerOpen PDF; the EASA Type-Certificate Data Sheet for the Boeing 777; the Malaysian Safety
Investigation Report briefing slide deck; the Los Alamos seismic and hydroacoustic report; the
Blelly and Marchand ditching analysis; three Radiant Physics articles reporting the Boeing
engineering-simulator dataset and independent-group end-of-flight work.

**Not retrieved — a material limitation of this sheet.** Every ATSB report (2014 search-area
definition, December 2015 update, November 2016 search and debris examination update, October 2017
operational search) is absent. The host `www.atsb.gov.au` is reachable at the transport layer but
its origin returned zero bytes on every path tried, including the homepage, over repeated attempts
of up to 900 s; one attempt returned an immediate HTTP/2 INTERNAL_ERROR. Two alternative
repositories holding the same official PDFs (`apo.org.au`, the National Library of Australia's
Australian Government Web Archive) are gated by anti-bot challenges and returned HTTP 403 or a
proof-of-work page. Also not retrieved: Safety Investigation Report Appendix 1.6E (the Boeing
performance analysis), the CSIRO drift reports EP167888 and EP172633, the FAA Type Certificate Data
Sheet T00001SE, any Boeing primary performance document, and the full text of Lyne (2024).

Consequence: **the ATSB-origin numbers in this sheet are all at second hand** — the 15 NM
uncontrolled-descent distance and the approximately 100 NM controlled-glide distance come from
Davey et al. §10.5 and §10.8 citing the December 2015 ATSB report; the ten Boeing
engineering-simulator case parameters and the 15,000 ft/min with 0.67 g pairing come from Iannello
(2017, 2018) citing the November 2016 ATSB report and from per-second data the ATSB supplied to
that author. None of these were verified against an ATSB document in this session. They should be
checked against the primary PDFs before they are used as published calibration targets in a paper.

## Group 1 — Boeing engineering-simulator runs (Safety Investigation Report Appendix 1.6E, ATSB)

**Available as calibration targets** (all via Iannello 2018, reporting an ATSB-released dataset):
ten cases; initial Mach 0.75–0.83; initial altitude 35,000 or 40,000 ft; initial heading 178°, 184°
or 190°; light or moderate turbulence, with winds. Six cases in the normal electrical configuration
(autopilot lost at the second flameout) and four in the alternate configuration (left generators
isolated, so the autopilot is lost at the *first* flameout while one engine still runs). All ten
paths remain within 32 NM of the position two minutes after autopilot loss, and the farthest impact
is about 15 NM from the 7th arc because the paths curve. Five cases (3, 4, 5, 6, 10) exceed
15,000 ft/min rate of descent *and* 0.67 g downward acceleration, with maximum downward
acceleration 0.87–1.30 g; for those, impact occurs 4.7–7.9 NM after the rate of descent first
exceeds 15,000 ft/min. Case 6 is described in enough detail to reproduce a full profile: 425 kt
ground speed at 35,000 ft, 15,000 ft/min first reached at 27,000 ft with only 0.3 g over the
preceding 8 s, a phugoid level-off near 19,000 ft, a second 15,000 ft/min at about 18,000 ft, and
impact 3.3 NM later. In no case did the aircraft fly straight with level wings after the autopilot
disengaged.

**Not published, so not checkable.** Per-case initial conditions, per-case bank-angle and attitude
histories, per-case time to impact, per-case impact speed and flight-path angle, and the assumed
interval between the two flameouts are all withheld for legal reasons. Appendix 1.6E itself, which
would give the Boeing performance basis, is not public. A simulator can therefore be compared with
the *ensemble* (radial spread, descent-rate and acceleration exceedance fractions, dive-leg length)
but not case by case, except for case 6.

## Group 2 — ATSB search-area reports

**Available, at second hand:** the official descent kernel — a uniform disc of radius 15 NM with a
Gaussian drop-off of standard deviation 30 NM beyond it, convolved with the particle distribution
at 00:19 (Davey et al. §10.5, on ATSB advice); the statement that uncontrolled-descent simulations
reach zero altitude within 15 NM of the start of descent; and the approximately 100 NM maximum
glide distance under human control (Davey et al. §10.8). The 15,000 ft/min and 0.67 g pairing the
ATSB used as the BFO-derived values, and the statement that cases matching the final BFO values and
their timing impacted within 15 NM of the 7th arc, are available only as quoted by Iannello.

**Not available in this session:** the ATSB's own statement of the 00:19 descent-rate bounds (the
reports are understood to carry DST Group's analysis, and the lower bound quoted in the 2017 report
is reported elsewhere to differ from Holland's published 14,800 ft/min — this sheet does not record
that value because it could not be read), the unresponsive-crew rationale as written, and the
glide-versus-dive search-width derivation.

## Group 3 — Boeing published performance for the 777-200ER / Trent 892

**Available:** maximum operating altitude 43,100 ft (13,140 m) pressure altitude, from EASA
Type-Certificate Data Sheet IM.A.003 Issue 20.0, Section 2 — a primary certification document.

**Not published or not retrievable, and therefore a genuine gap.** The data sheet does not state
VMO or MMO; it refers to the Airplane Flight Manual. The widely repeated 330 kt / Mach 0.87 pair
could not be traced to a primary document here. Neither could the maximum lift-to-drag ratio, the
best glide ratio, or the driftdown schedule: the Airplane Flight Manual and Performance Engineer's
Manual are not public, and Appendix 1.6E was not retrieved. The only driftdown figure on the sheet
is Blelly and Marchand's statement that the Boeing-recommended two-engine-inoperative speed is
270 kt indicated, which they give without a primary citation. **Flagged: a simulator's glide ratio
and driftdown schedule cannot presently be checked against any retrievable primary manufacturer
source.**

## Group 4 — Holland, burst frequency offset analysis

The strongest-provenance quantitative source on the sheet, and fully retrieved. Peer-reviewed in
IEEE Aerospace and Electronic Systems Magazine 33(2), 24–33 (2018); text used here is the accepted
preprint arXiv:1702.02432v3.

Recorded burst frequency offsets 182 Hz at 00:19:29 and −2 Hz at 00:19:37. Vertical-rate
sensitivity 2.8 Hz per 100 ft/min with the satellite overhead, reducing to 1.7 Hz per 100 ft/min at
the 38.8° elevation applying at 00:19 — this is the conversion factor the whole literature uses.
In-flight burst frequency offset error is treated as strictly bounded on [−28, +18] Hz, from all
2,501 valid in-flight error values over the 20 preceding flights of 9M-MRO; note this is a bounding
model, not the ±7 Hz standard deviation Davey et al. use. Level-flight reference values are about
260 Hz for a southerly track and 280 Hz for a northerly one.

Descent-rate bounds, separated by hypothesis (this separation matters, and is usually lost when the
numbers are quoted): under hypothesis 1, a roughly one-minute satellite data unit outage after fuel
exhaustion followed by restart on auxiliary power, with oscillator warm-up drift removed,
3,900–14,800 ft/min at 00:19:29 and 14,800–25,300 ft/min at 00:19:37; under hypothesis 2, a log-on
for some other reason and therefore no warm-up correction, 2,900–6,800 ft/min and
13,800–17,600 ft/min. Outer bounds across both: 2,900–14,800 ft/min and 13,800–25,300 ft/min.
Mean downward acceleration over the 8 s interval 0.68 g (10,700 ft/min increase, about
1,300 ft/min per second, 6.7 m/s²), taken from the midpoints of the bounds; Holland explicitly
rejects combining the extreme bounds, which would give about 2,800 ft/min per second. All bounds
hold for any ground track and ground speeds below about 500 kt, are rounded to 100 ft/min, and
assume no unknown factor affected the final two offsets.

**Not published:** a probability distribution over descent rate — the paper gives bounds only, so
there is no published likelihood to compare a simulator's descent-rate posterior against. The
warm-up-drift correction rests on seven prior log-on events of the same aircraft and is a
hypothesis, not a measurement; the two hypotheses are not assigned probabilities.

## Group 5 — Davey, Gordon, Holland, Rutten and Williams (2016)

Fully retrieved, open access. The end-of-flight treatment is deliberately thin: the particle filter
produces the state distribution at 00:19 and the descent is handled by convolving it with the
15 NM / 30 NM kernel supplied by the ATSB (§10.5, radial profile in Fig. 10.9, resulting heat map
and 90/95/99 per cent regions in Fig. 10.10). Fuel exhaustion is placed between 00:11 and 00:19,
with the final message attributed to the modem rebooting on auxiliary power, so the engines are
taken as unpowered at 00:19. Both final burst timing offsets are retained even though their
residuals have opposite signs and are mutually inconsistent. Both 00:19 burst frequency offsets are
**discarded** as unreliable — the official Bayesian solution therefore used no 00:19 frequency
information at all. §10.8 records that the two things which materially move the output distribution
are the assumed Mach-number spread and the end-of-flight model, and that a different end-of-flight
model spreads the search zone over a larger area. Chapter 11 gives the search-update formulation and
the probability of detection of 0.9 adopted for side-scan sonar in the AF447 analysis.

**Not published:** no post-fuel-exhaustion flight-time, impact-speed, flight-path-angle or
impact-energy distribution; no functional form or parameters for the descent kernel beyond the
15 NM core and 30 NM Gaussian tail; no decomposition of the kernel into controlled and uncontrolled
components. The figures showing the impact distribution are maps, not tabulated distributions, so
they are not usable as numerical targets without digitisation.

## Group 6 — Independent-group and other analyses; hydroacoustics; drift

**Available.** Ulich and Iannello (2020): lateral shift along the arc from the post-exhaustion turn
1.1–8.8 NM across the ten Boeing cases, with 8.8 NM adopted as a standard deviation; 32 NM adopted
as a two-standard-deviation distance travelled after the arc crossing; about 5 NM of additional
travel after 0.67 g and 15,000 ft/min occur together; combined impact-point standard deviations of
19.2 NM along the arc and 16.3 NM normal to it; arc-position sensitivity 0.104 NM per microsecond of
burst timing offset; an assumed 20,000 ft altitude at 00:19:29, reached 1.5–2 min after fuel
exhaustion. Iannello (2017), on a consumer-grade simulator and therefore the weakest aerodynamic
provenance here: descent rates of 4,000 then 14,400 ft/min derived from the same two offsets under
different bias, track and speed assumptions; about 50 s from 4,000 ft/min to impact; impact about
4.8 NM from the arc crossing; a peak of about Mach 1.1 and 60,000 ft/min that the author notes is
outside the model's validated envelope; and the Aircraft Maintenance Manual note that with the ram
air turbine extended and hydraulics off the aircraft rolls left, needing two to three units of right
control wheel to hold the wings level.

Hydroacoustics: the Los Alamos report gives a candidate arrival at station H01 with direction of
arrival 246.9° and SOFAR-channel phase velocity 1.46 km/s, and concludes the evidence is
inconclusive though it may favour a more southerly location.

**Not available.** No published estimate of MH370's impact speed, impact flight-path angle, impact
energy, or energy-transfer duration was found in any retrievable source. The Los Alamos report
contains no impact-energy figure. **Flagged: a simulator's impact-energy and energy-transfer-
duration outputs have no published calibration target at all** — the nearest retrievable
quantities are the descent rate and attitude at impact implied by the simulator cases. The CSIRO
drift reports, which would state any end-of-flight constraint used in the drift modelling, were not
retrieved.

**Contested.** Lyne (2024, Journal of Navigation, peer-reviewed) disputes the Doppler model
underlying the official interpretation and argues for a controlled eastward descent ending in a
powered glide landing with extended flaps, rejecting the fuel-starvation dive outright. Only the
abstract was retrievable, so no numerical values from it are on the sheet. Separately, Ulich and
Iannello record an unresolved contradiction *within* the official material: none of the ten Boeing
cases is in a steep descent as the 7th arc is crossed, so the simulator ensemble and the
offset-derived descent at 00:19 do not agree.

## Group 7 — Ditching hypothesis and 777 ditching guidance

**Available.** Blelly and Marchand give the only published ditching numbers found: a
two-engine-inoperative driftdown at 270 kt indicated giving about 2,200 ft/min, 306 kt average
ground speed, under about 9 min from 19,500 ft and a maximum of about 45 NM from the 7th arc; a
minimum-speed glide at 210 kt indicated (taken as reference landing speed plus 80 kt at 175 t)
giving about 1,150 ft/min, 236 kt average ground speed, about 17 min and a maximum of about 67 NM;
and, in their variant including a 10 s dive before the arc followed by a 50 s recovery covering
6 NM, a reduced range of 42–59 NM. Their largest glide distance, 67 NM, is well short of the
approximately 100 NM attributed to the ATSB and the 120 NM or more Iannello obtains from a glide
begun at 40,000 ft; the three are not the same quantity, since the glide-start altitude differs.

**Not available.** No touchdown vertical speed, pitch attitude or flare profile for a 777 ditching
could be traced to a primary Boeing or regulatory document; the figures that circulate come from
mirrored flight-crew manuals. **Flagged: a simulator's ditching touchdown conditions cannot be
checked against a citable primary source.**

## The most useful numerical calibration targets, in priority order

1. **Maximum distance from the 7th arc to impact, uncontrolled, about 15 NM**, with the full path
   envelope within 32 NM of the two-minute reference position (ten Boeing cases, via Iannello 2018).
   This is the single number the official search width rests on, it appears independently as the
   15 NM uniform core of the official descent kernel, and it tests the radial spread of an
   uncontrolled simulation directly.
2. **Descent-rate bounds at the two final transmissions, 2,900–14,800 ft/min at 00:19:29 and
   13,800–25,300 ft/min at 00:19:37** (Holland 2018, Table VII), checked separately against the
   hypothesis-1 and hypothesis-2 sub-bounds rather than the outer envelope alone. Highest
   provenance of any descent quantity, and the only one with its conditions of validity published.
3. **Mean downward acceleration over the 8 s interval, 0.68 g** (Holland 2018), derived from bound
   midpoints. A simulator's acceleration at the burst times should be compared with this and not
   with the extreme-bound value of about 2,800 ft/min per second, which Holland rejects.
4. **Exceedance fraction: 5 of 10 cases above both 15,000 ft/min and 0.67 g, with maximum downward
   acceleration 0.87–1.30 g in those cases** (via Iannello 2018). This is an ensemble statistic, so
   it tests the *distribution* a simulator produces rather than a single trajectory.
5. **Distance from the first exceedance of 15,000 ft/min to impact, 4.7–7.9 NM** (via Iannello
   2018), with the independent corroboration of about 5 NM from the banked-descent simulation. The
   tightest published constraint on the dive leg.
6. **The official descent kernel: uniform disc of radius 15 NM with a Gaussian tail of standard
   deviation 30 NM** (Davey et al. §10.5). The benchmark for the marginal impact-position
   distribution an end-of-flight module should produce from a given 00:19 state distribution.
7. **Maximum controlled glide distance after fuel exhaustion, about 100 NM** (ATSB via Davey et al.
   §10.8), with Iannello's 120 NM or more from a 40,000 ft start recorded alongside it. Upper bound
   on the controlled-flight arm; the altitude dependence must be preserved when comparing.
8. **Case 6 vertical profile: 425 kt ground speed at 35,000 ft; 15,000 ft/min at 27,000 ft with
   0.3 g over the preceding 8 s; level-off near 19,000 ft; 15,000 ft/min again at about 18,000 ft;
   impact 3.3 NM later, 7.9 NM from the first exceedance** (via Iannello 2018). The only published
   case that can be reproduced trajectory-by-trajectory, and the only published test of multi-
   phugoid behaviour.
9. **Vertical-rate to frequency-offset sensitivity, 1.7 Hz per 100 ft/min at 38.8° elevation**
   (Holland 2018, eq. 6), with 2.8 Hz per 100 ft/min overhead. Checks the simulator's own
   observation model rather than its dynamics, and is analytic, so any disagreement is a bug.
10. **Time from the onset of a steep descent to impact, about 50 s from 4,000 ft/min** (Iannello
    2017). Weak provenance, but it is the only published time-to-impact figure for a dive case.
11. **Driftdown and minimum-speed glide pairs for the ditching arm: 2,200 ft/min with 306 kt ground
    speed giving about 45 NM, and 1,150 ft/min with 236 kt giving about 67 NM** (Blelly and
    Marchand). The only published numbers for a deliberate-ditching end of flight.
12. **Maximum operating altitude, 43,100 ft pressure altitude** (EASA Type-Certificate Data Sheet
    IM.A.003). A hard certificated ceiling on any glide-start altitude a sampler proposes.

## Numbers that could not be traced to a primary source

- VMO and MMO of 330 kt and Mach 0.87 — repeated everywhere; the EASA data sheet defers to the
  Airplane Flight Manual and the FAA data sheet was not retrievable.
- Maximum lift-to-drag ratio and best glide ratio of the 777-200ER, and the driftdown schedule —
  no retrievable primary manufacturer source.
- The approximately 100 NM glide radius — traced only to Davey et al. citing the December 2015 ATSB
  report; the ATSB original was not read.
- The 15,000 ft/min with 0.67 g pairing attributed to the ATSB — traced only to Iannello quoting the
  November 2016 report. Note it differs from Holland's own 14,800–25,300 ft/min and 0.68 g.
- The −4,000 to −14,500 ft/min pair that Blelly and Marchand attribute to Holland over 9 s. Holland
  (2018) states neither value nor that interval; the pair resembles Iannello's 2017 derivation under
  different bias, track and speed assumptions. Recorded in the sheet as a flagged misattribution.
- 777 ditching touchdown vertical speed and attitude — mirrored manuals only.
