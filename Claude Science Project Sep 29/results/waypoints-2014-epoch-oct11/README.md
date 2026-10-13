# 2014-epoch fix table for the waypoint-family reset (11 Oct 2026)

Pete's instruction (11 Oct): use fixes valid in March 2014, not the current cycle. This folder holds
the table and its sources. No run uses it yet.

## Sources, in order of authority

1. **AIP Malaysia ENR 3.3, AIP AMDT 2/2010 (03 JUN 2010)**, from Pete's Drive. It gives N571
   VAMPI-MEKAR-NILAM-IGOGU (FIR BDRY), P574 ANSAX (FIR BDRY)-IGEBO-NOPEK (FIR BDRY), P627
   RUSET-DUKUN-LEKIR-NILAM-SANOB-IGEBO-POVUS (FIR BDRY), and P628 IGREX (FIR BDRY)-MINAT-MAPSO-DUKUN-GIVAL.
   Plus the engine's earlier pre-2014 rows (Malaysia AIP SUP 36/2008, AMDT 3/2011; India AIP archive
   effective 1 Apr 2012 for SAMAK and IGOGU).
2. **Robin A. Peel navigation data, cycle 2013.10** (fix.dat / awy.dat build 20131334, the X-Plane and
   FlightGear default data; GPL), retrieved from GitHub FGDATA/fgdata. Five months before the flight.
   Covers the Indian, Indonesian and Australian FIRs, where no 2013-14 AIP is online.
3. The Drive `waypoint_catalog.csv` (current cycle: AirNav Indonesia AMDT 2021-25, India ENR 4.4
   AMDT 01/2018, Australia ERSA).

## Tiers

| Tier | Meaning | Count |
|---|---|---|
| A | In a pre-2014 AIP | 9 |
| B | In the 2013.10 navigation data; coordinate taken from it | 17 |
| C | En-route fix in the current cycle only; 2014 existence not shown | 5 |
| D | Current-cycle terminal or approach fix (WITT / WITN AD 2.24, AMDT 2021-24) | 13 |
| S | In 2013.10 data only, but absent from the 2010 AIP (stale) | 1 |

Proposed sampling set: tiers A and B (26 fixes). C as a sensitivity arm. D and S excluded.

## Findings

- Every fix found in two or more sources agrees to within 0.02 NM, except ANOKO: 0.222 NM between
  2013.10 (7.138583, 94.413489) and the current cycle (7.136111, 94.416111). The 2013.10 value is adopted.
- VAMPI and NOPEK are confirmed by the 2010 AIP. The engine table still marks them as unverified.
- **EMRAN** (8.575, 94.416667, current L510) is not in the 2013.10 data. No boundary point lies between
  SAMAK and IGREX in that cycle. Tier C.
- **IVRAR** (the south-east corner of Pete's phase-2 box) is absent from 2013.10 as well as from the
  current data. The declared vertex 4N 96E stays.
- The 2013.10 data lags the AIP in places. It has N571 as VAMPI-DOVUM-IGOGU-LAGOG, without MEKAR
  and NILAM. DOVUM lies 4.5 NM from NILAM. So 2013.10 is used to confirm coordinates and existence,
  not as the authority on route structure.
- The 2013.10 data has no terminal fixes, so a tier-D fix missing from it is not evidence about 2014.

## Phase regions (column `phase_regions`)

- Phase 1, "west of MEKAR": taken here as 5.5-8.5 N, 94.0 E to MEKAR's longitude. This is my reading of the spec.
- Phase 2: the box from 10 NM NW of LAGOG to 4N 96E.
- Phase 3: Pete's polygon, with IVRAR replaced by 4N 96E.
- Waypoint flight is limited to north of 4.5 S.

## Files

- `waypoints-2014-epoch.csv`: the table, with adopted and per-source coordinates, airways in each source, and offsets.
- `navdata-2013-10-fixes-extract.csv`, `navdata-2013-10-airways-extract.csv`: the 15S-12N, 85-100E part
  of the 2013.10 data, with the GPL attribution line.
