# H08S seismic-survey source identification and public-data audit

Research completed 3 September 2026. This is the canonical research source for
the browser report `outputs/h08s-seismic-survey-source-research.html`.

## Question

Which seismic surveys could account for the approximately 9.95-second periodic
interference in the Diego Garcia South (H08S) publication trace on 8 March
2014? Can a public AIS track identify the source, and is the received pressure
physically compatible with a large marine airgun array at the inferred range?

## Executive finding

The source is not merely an AIS hypothesis. The Australian Transport Safety
Bureau (ATSB) reports that both operators conducting relevant surveys off
north-west Australia supplied their actual navigation data. The reception time
of the last shot and the change in measured bearing identified the H08S train as
the TGS Huzzas 3D survey; the simultaneous Woodside Centaurus 3D survey was not
detected. ATSB attributes the contrast to Huzzas operating above a favourably
sloping continental seabed at about 260 m depth, enabling efficient coupling
into the Deep Sound Channel, while Centaurus was over flatter seabed in just
over 1,000 m of water.

The Huzzas acquisition was undertaken by M/V *Geo Caspian* during January–March
2014. TGS lists a 3,366 in³ airgun source, 18.75 m flip/flop shot spacing,
NE–SW shooting orientation and 2,121.9 km² final survey area. The regulatory
plan describes approximately 2,000 psi operation, alternating sub-arrays, pulses
every 8–10 seconds, and approximately 262 dB re 1 μPa SPL within a few metres.
Australian Notice to Mariners 78(T)/2014 independently places *Geo Caspian* and
two support vessels inside a published survey polygon until 1 April 2014.

## Geometry and pressure calculation

Using the mean H08S triplet coordinate (-7.63937°, 72.48383°) and the planar
area centroid of the Huzzas regulatory operational polygon (-21.12139°,
114.63699°), a spherical-Earth calculation gives 4,763.05 km and an initial
bearing of 112.96°.
Across the polygon, the range is approximately 4,706–4,812 km and the bearing is
112.14–113.67°. These are independent coarse calculations, not a substitute for
ATSB's shot-by-shot navigation fit.

The Huzzas environmental plan gives representative pressure levels of 201 dB re
1 μPa at 1 km and 181 dB re 1 μPa at 10 km. Continuing that stated 20 dB per
decade decay only as an arithmetic sensitivity check,

\[
L_p(r)=181-20\log_{10}\!\left(\frac{r}{10\;\mathrm{km}}\right),
\qquad
p(r)=10^{L_p(r)/20}\times10^{-6}\;\mathrm{Pa}.
\]

At 4,763.05 km, \(L_p=127.44\) dB re 1 μPa and \(p=2.36\) Pa. Kadri (2024)
reports H08S airgun noise of approximately 2–4 Pa, equivalent to 126.02–132.04
dB re 1 μPa. The agreement is encouraging at order-of-magnitude level, but it
does not validate a transmission model: source directivity, bathymetry,
frequency-dependent absorption, sound-speed structure, channel coupling,
instrument response and Kadri's filters are omitted.

Pressure is not energy. A comparable 2,600 in³ north-west Australian array was
modelled by McCauley, Meekan and Parsons (2021) at a per-shot SEL of 228 dB re
1 μPa²·m²·s at 15° below horizontal. If that directional source-level number
were treated as isotropic solely to establish scale, it corresponds to about
0.52 MJ acoustic energy and about 1.8 nJ m⁻² at 4,763 km under spherical
spreading. It is not a measurement of the Huzzas array, and it cannot be
compared directly with a 2–4 Pa peak without the calibrated waveform and
integration interval.

## Contemporary surveys

* **TGS Huzzas 3D, north-west Australia:** active on 8 March; M/V *Geo
  Caspian*; detected and matched by ATSB to operator navigation.
* **Woodside Centaurus 3D, north-west Australia:** 24 February–18 March 2014;
  up to 4,000 in³ and 18.75 m shot spacing in the environmental plan; operator
  navigation supplied to ATSB; not detected at H08S.
* **TGS CSM-14 and AN-14, offshore Madagascar:** announced in acquisition in
  January and completed during Q1 2014, using M/V *Geo Arctic* and *BGP
  Challenger*. Exact activity on 8 March was not established. These demonstrate
  that the wider Indian Ocean survey inventory is not exhausted, but they are
  not candidates for the ATSB-matched 113° sequence.

## AIS and source-navigation availability

No open, downloadable *Geo Caspian* AIS track for 8 March 2014 was located in
this search. Global Fishing Watch can display vessel activity from 2012 and
accepts name/MMSI/IMO searches, but API access requires a token and coverage of
this non-fishing survey vessel was not verified. Commercial historical AIS may
exist, but its satellite coverage and retention for this date must be checked
before purchase.

AIS is secondary here. Shot navigation is scientifically better because it
contains the source position and firing sequence. TGS's product sheet lists
Navmerge shot gathers as an available deliverable. Geoscience Australia's
NOPIMS catalogue states that open-file offshore survey holdings can include
navigation and acquisition reports; enquiries for missing holdings go to
<email>. The practical request order is: (1) TGS/Searcher for the
Huzzas UKOOA/P1 or shot-navigation file, (2) ATSB for the exact navigation
subset/derived series used in Figures 8 and 10 and its disclosure status, and
(3) NOPIMS/Geoscience Australia for open-file navigation and acquisition
reports. Request UTC shot time, source latitude/longitude, line and shot number,
active sub-array, gun state/volume, vessel speed and datum.

## Scientific consequence

The periodic H08S train should be treated as identified seismic clutter and a
potential calibration source, not as an unknown event family. With raw H08S
triad data and shot navigation, it could calibrate clock alignment, bearing
bias, station response, pulse-shape variability, propagation-time residuals and
the performance/false-dismissal cost of an airgun-removal method. Publication
figure traces cannot support those inferences.

## Located primary and technical sources

1. ATSB, *The Operational Search for MH370* (2017), pp. 22–24:
   https://www.atsb.gov.au/sites/default/files/media/5773565/operational-search-for-mh370_final_3oct2017.pdf
2. NOPSEMA, *Huzzas Multi Client 3D Marine Seismic Survey Environment Plan
   Summary* (2013): https://docs.nopsema.gov.au/A333623
3. Australian Hydrographic Office, Notice 78(T)/2014:
   https://www.hydro.gov.au/n2m/2014/blocks/tempprelim_2_2014.pdf
4. TGS, *Huzzas 3D specification sheet*:
   https://map.tgs.com/specsheets/Huzzas_3D_Spec_Sheet.pdf
5. Woodside, *2014 Half-Year Report*, p. 13:
   https://www.woodside.com/docs/default-source/investor-documents/quarterly-and-half-yearly-pdfs-and-data-tables/2014/20-08-2014-2014-half-year-report-incl-appendix-4d.pdf
6. NOPSEMA, *Babylon and Centaurus 3D MSS Environment Plan Summary*:
   https://docs.nopsema.gov.au/A333595
7. TGS, *TGS announces four new multi-client surveys* (9 January 2014):
   https://www.tgs.com/press-releases/tgs-announces-four-new-multi-client-surveys
8. Kadri, *Scientific Reports* 14, 10102 (2024):
   https://www.nature.com/articles/s41598-024-60529-1
9. McCauley, Meekan and Parsons, *Journal of Marine Science and Engineering*
   9, 571 (2021): https://www.mdpi.com/2077-1312/9/6/571
10. Global Fishing Watch Map User Guide:
    https://globalfishingwatch.org/user-guide/
11. Global Fishing Watch API documentation:
    https://api-doc.globalfishingwatch.org/our-apis/documentation/
12. Geoscience Australia, NOPIMS:
    https://www.ga.gov.au/nopims

## Boundaries

The Huzzas sail lines drawn in the browser report are schematic lines clipped to
the regulatory polygon in the published NE–SW shooting orientation. They are
not AIS, not operator navigation and not evidence of the vessel's position at a
particular UTC. The pressure calculation is a one-number sensitivity check,
not a range estimate, energy inversion or evidence about MH370.
