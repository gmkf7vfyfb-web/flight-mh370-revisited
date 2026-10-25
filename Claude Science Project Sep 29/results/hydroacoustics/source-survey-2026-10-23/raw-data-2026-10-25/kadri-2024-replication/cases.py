"""Case definitions for the Kadri (2024, Sci. Rep. 14:10102) crash-panel replication (track 4, 25 Oct 2026).

Every value has a source string. 'kadri_*' = what Kadri states (S1 text, Fig. 2 map labels, Figs. 4-6 panel axes).
'off_*' = official / primary report (or the best public source found; flagged where not official).
Times UTC. Positions decimal degrees (N/E positive).
"""
from datetime import datetime, timezone

def dms(d, m, s, sign=1):
    return sign * (d + m / 60 + s / 3600)

def T(s):
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)

CASES = {
 "F35A": dict(
    label="JASDF F-35A, off Misawa, 9 Apr 2019",
    kadri_t=T("2019-04-09T10:26:30"), kadri_t_src="Kadri S1 p.1 'at 10:26:30 UTC (1)' (JASDF press release)",
    kadri_pos=(dms(40, 30, 10), dms(142, 4, 37)), kadri_pos_src="Kadri S1 p.1 '40o30'10\"N 142o04'37\"E'",
    off_t=T("2019-04-09T10:26:30"), off_t_lo=-30, off_t_hi=30,
    off_t_src="Kadri S1 / JASDF; module convention (Metz et al. 2023). Not re-verified against the JASDF report in this track (track 1 owns F-35A).",
    off_pos=(40.64, 142.96), off_pos_src="module working point (Metz et al. 2023, ~135 km E of Misawa)",
    panels=[("H11N", "2019-04-09T10:58:00", "4a"), ("H11S", "2019-04-09T10:59:00", "4a")],
    own_stations=["H11N", "H11S"]),
 "SJ182": dict(
    label="Sriwijaya Air 182, Java Sea, 9 Jan 2021",
    kadri_t=T("2021-01-09T07:40:00"), kadri_t_src="Kadri S1 p.2 'at 07:40 UTC'",
    kadri_pos=(dms(5, 54, 54, -1), dms(107, 7, 6)), kadri_pos_src="Kadri S1 p.2 '5o54'54\" S, 107o07'06\" E'",
    off_t=T("2021-01-09T07:40:28"), off_t_lo=-5, off_t_hi=15,
    off_t_src="KNKT final report KNKT.21.01.01.04: 'At 07:40:28 UTC, the FDR stopped recording.'",
    off_pos=(dms(5, 57, 56.21, -1), dms(106, 34, 24.86)), off_pos_src="KNKT preliminary report: last FDR coordinate 5°57'56.21\" S 106°34'24.86\" E",
    panels=[("H08S", "2021-01-09T08:06:00", "4c")],
    own_stations=["H08S"]),
 "TA810": dict(
    label="Transair 810 ditching, Mamala Bay, 2 Jul 2021",
    kadri_t=T("2021-07-02T11:46:00"), kadri_t_src="Kadri S1 p.2 'around 11:46 UTC'",
    kadri_pos=(dms(21, 18, 41), dms(157, 54, 16, -1)), kadri_pos_src="Kadri S1 p.2 '21o18'41\" N, 157o54'16\" W'",
    off_t=T("2021-07-02T11:45:18"), off_t_lo=-60, off_t_hi=60,
    off_t_src="NTSB DCA21FA174: 'about 0145 HST' (= 11:45 UTC); ADS-B data end 11:45:17.902 UTC (NTSB performance study). ±60 s assumed.",
    off_pos=(21.275, -158.026), off_pos_src="Wikipedia infobox 21°16'30\"N 158°01'34\"W (NOT official; NTSB final report coordinates not read)",
    panels=[("H11N", "2021-07-02T12:28:00", "5b"), ("H11S", "2021-07-02T12:27:00", "5b")],
    own_stations=["H11N", "H11S"]),
 "QZ8501": dict(
    label="Indonesia AirAsia 8501, Karimata Strait, 27/28 Dec 2014",
    kadri_t=T("2014-12-28T07:37:00"), kadri_t_src="Kadri S1 p.3 'December 28, 2014 ... around 07:37 UTC' (his Fig. 6b panel starts 23:51 UTC, i.e. 27 Dec)",
    kadri_pos=(dms(5, 50, 36.0, -1), dms(111, 2, 33.0)), kadri_pos_src="Kadri S1 p.3 '05o50'36.0\" S, 111o02'33.0\" E'",
    off_t=T("2014-12-27T23:20:35"), off_t_lo=0, off_t_hi=10,
    off_t_src="KNKT final report KNKT.14.12.29.04: 'The last data recorded by FDR was at 2320:35 UTC ... radio altitude was 118 feet'",
    off_pos=(dms(3, 37, 19, -1), dms(109, 42, 41)), off_pos_src="KNKT final report title-page coordinate 3°37'19\"S 109°42'41\"E (as cited by a secondary source; ASN/Wikipedia 3°37'23\"S 109°42'43\"E)",
    panels=[("H01W", "2014-12-27T23:51:00", "6b")],
    own_stations=["H01W", "H08S"]),
 "AB1103": dict(
    label="AB Aviation 1103 (Cessna 208B), off Moheli, 26 Feb 2022",
    kadri_t=T("2022-02-26T09:30:00"), kadri_t_src="Kadri S1 p.3 'at around 09:30 UTC'",
    kadri_pos=(dms(12, 14, 36.3552, -1), dms(43, 46, 50.6886)), kadri_pos_src="Kadri S1 p.3 '12o14'36.3552'S 43o46'50.6886\"E'",
    off_t=T("2022-02-26T09:30:00"), off_t_lo=0, off_t_hi=600,
    off_t_src="NO OFFICIAL REPORT FOUND. ASN: last contact 12:30 LT (EAT=UTC+3) = 09:30 UTC; Aviation24/The Citizen: last contact 12:40 LT = 09:40 UTC. Window 09:30-09:40 UTC assumed.",
    off_pos=(dms(12, 14, 36.3552, -1), dms(43, 46, 50.6886)), off_pos_src="Kadri S1 (no official position found; ASN: 2.5 km NW off Moheli airport)",
    panels=[("H08S", "2022-02-26T09:36:00", "6a")],
    own_stations=["H08S"]),
 "JT610": dict(
    label="Lion Air 610, Java Sea, 28/29 Oct 2018 (out-of-sample; not used by Kadri)",
    kadri_t=None, kadri_t_src="not in Kadri 2024", kadri_pos=None, kadri_pos_src="not in Kadri 2024",
    off_t=T("2018-10-28T23:31:54"), off_t_lo=0, off_t_hi=15,
    off_t_src="KNKT final report KNKT.18.10.35.04: 'MCAS activated until the DFDR stopped recording at 23:31:54'",
    off_pos=(-5.8156, 107.1231), off_pos_src="KNKT preliminary report: first floating debris 'N5.8156 E107.1231' (sic; S implied), as quoted by AvHerald",
    panels=[],
    own_stations=["H08S"]),
}
