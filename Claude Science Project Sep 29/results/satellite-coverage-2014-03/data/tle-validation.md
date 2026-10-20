# Element-set validation, March 2014 (ELEMENTS track)

Element sets: `tle-2014-03.csv` (Space-Track GP elements via the public Hugging Face bulk export, plus amateur sets for classified objects).
Propagator: SGP4 (python `sgp4` 2.x, WGS72), sub-satellite point from TEME position with GMST rotation and geodetic latitude (WGS84 flattening).
Great-circle distances on a 6371 km sphere. "Off-nadir" is the look angle at the satellite, "incidence" the angle at the ground between the line of sight and the local vertical:
sin(incidence) = (R+h)/R * sin(off-nadir).

## (a) THEOS, 24 Mar 2014 03:07:56 UTC, target 46.5 S 89.5 E, published incidence 26.98 deg

- Element set used: epoch 2014-03-24 05:48:10 UTC (2.7 h after the fix).
- Time of closest approach of the sub-satellite point to the target: **03:08:00 UTC**, 4 s after the published acquisition time.
- Nadir point at TCA: 47.489 S, 94.177 E; altitude 839.8 km; ground distance to target **371.3 km** (target is west of the track, i.e. a left-looking roll).
- Implied off-nadir 23.57 deg, implied incidence **26.91 deg** versus 26.98 deg published (difference 0.07 deg, about 1 km on the ground).
- Inverse check: 26.98 deg incidence from 840 km requires off-nadir 23.63 deg and a ground offset of 372 km. Consistent.
- Solar elevation at the target at 03:07:56 UTC: 27.9 deg (daylight, as required for an optical scene).

Residual: 4 s along-track (about 28 km of satellite motion, well inside the 3 s rounding of the published time plus scene-centre uncertainty) and 1 km cross-track.

## (b) DigitalGlobe image, 16 Mar 2014 04:16 UTC, near 44.0 S 91.0 E

| Satellite | Element epoch | Nadir at 04:16:00 | Distance to target at 04:16 | TCA within +-60 min | Distance at TCA | Off-nadir at TCA |
|---|---|---|---|---|---|---|
| WorldView-2 (35946) | 16 Mar 04:53 (+0.6 h) | 44.68 S, 89.29 E, 781 km | 156 km | **04:15:44** | **114 km** | **8.3 deg** |
| WorldView-1 (32060) | 16 Mar 02:50 | 51.2 N, 97.4 W | 18,998 km (other side of Earth) | 03:27:03 | 459 km | 41.2 deg |
| GeoEye-1 (33331) | 16 Mar 03:57 | 65.6 N, 104.8 W | 17,430 km | 03:21:08 | 645 km | 41.3 deg |
| QuickBird-2 (26953) | 16 Mar 03:05 | 2.8 S, 96.1 W | 14,768 km | 03:41:30 | 450 km | 46.0 deg |
| IKONOS-2 (25919) | 16 Mar 03:45 | 67.7 N, 113.7 E | 12,568 km | 04:46:33 | 1,036 km | 53.0 deg |

Only **WorldView-2** was over the area at 04:16 UTC (TCA 04:15:44, 16 s before the published minute; 114 km east-west offset, 8.3 deg off-nadir; solar elevation 41 deg). WorldView-1, GeoEye-1 and QuickBird were over North America at that time and could not have taken the image. The 16 Mar DigitalGlobe scene is therefore attributed to WorldView-2.

## (c) Element-set self-consistency (catalogued objects)

Position difference between consecutive element sets, evaluated at the epoch of the later set (a proxy for SGP4 propagation error over one update interval, typically 8 h):

- THEOS: 84 pairs, median gap 8.3 h; along-track |dr| median 0.17 km, 95% 4.17 km, max 12.05 km; cross/radial median 0.036 km, max 0.60 km
- WorldView-2: 83 pairs, median gap 8.4 h; along-track |dr| median 0.23 km, 95% 0.47 km, max 0.61 km; cross/radial median 0.035 km, max 0.10 km
- WorldView-1: 98 pairs, median gap 7.9 h; along-track |dr| median 0.55 km, 95% 7.24 km, max 210.60 km; cross/radial median 0.032 km, max 4.69 km
- Landsat 8: 26 pairs, median gap 24.7 h; along-track |dr| median 0.55 km, 95% 9.87 km, max 11.93 km; cross/radial median 0.158 km, max 0.65 km
- RADARSAT-2: 82 pairs, median gap 8.2 h; along-track |dr| median 0.21 km, 95% 0.74 km, max 0.94 km; cross/radial median 0.037 km, max 0.21 km
- Yaogan-5: 90 pairs, median gap 7.8 h; along-track |dr| median 0.93 km, 95% 7.17 km, max 13.81 km; cross/radial median 0.074 km, max 0.69 km

WorldView-1 shows three along-track jumps of 82-211 km on 6-7 Mar 2014 with step changes in mean motion (15.2491 -> 15.2415 -> 15.2491 rev/day): an orbit-maintenance manoeuvre sequence. Element sets straddling a manoeuvre must not be propagated across it; always use the set nearest in time.

## (d) Amateur (classified-object) sets

- USA 245: the SeeSat-L recovery set of 8 Mar 2014 (C. Bassa, post Mar-2014/0048) propagated to the classfd epoch of 13 Mar differs from the classfd set by 187 km along-track (25 s) and 3.3 km cross/radial after 5 days. This is the expected scale for a freshly recovered manoeuvring object: tens of km per day along-track, a few km cross-track.
- No independent fix exists for the other amateur sets (Lacrosse 5, USA 186, SAR-Lupe 3, SAR-Lupe 5). Their stated accuracy (a few km within days of epoch, growing to tens of km per week) is the standard SeeSat-L experience and is not verified here.

## Accuracy statement for the map footnote

Catalogued satellites (Space-Track GP elements, SGP4, nearest element set): ground-track position good to about 1 km cross-track and 1-10 km along-track (1-2 s of motion) within the 8-24 h update interval; verified against the THEOS 24 Mar 2014 acquisition (4 s, 1 km) and the WorldView-2 16 Mar 2014 acquisition (16 s, within the published minute). Amateur-tracked classified satellites with March 2014 element sets (USA 186, USA 245, Lacrosse 5, SAR-Lupe 3, SAR-Lupe 5): a few km to tens of km along-track within a week of epoch, unverified. Classified satellites whose newest element set is older than two months (USA 224, SAR-Lupe 1/2/4, Helios 2A/2B, Ofeq 9, all IGS) have no usable pass timing in March 2014; Ofeq 5 and Ofeq 7 have no element set at all.

## Caveats on the catalogued set

- The bulk export stores parsed fields (float32 angles), not the original lines. Lines in `tle-2014-03.csv` were regenerated from those fields with correct checksums; the round-trip error is <= 2e-5 deg in angles and 0.04 ms in epoch, far below SGP4 accuracy. nddot, element-set number and revolution number are not in the export and are set to 0 (not used by SGP4).
- 18 exact duplicate records in the export were removed (6586 -> 6568 catalogued sets).
