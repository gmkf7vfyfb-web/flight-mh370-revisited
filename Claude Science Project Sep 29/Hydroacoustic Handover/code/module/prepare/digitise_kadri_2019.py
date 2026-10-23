#!/usr/bin/env python
"""Extract the tabulated material and the figure rasters of Kadri (2019), 'Effect of sea-bottom elasticity on the
propagation of acoustic-gravity waves from impacting objects', Sci. Rep. 9:912, doi 10.1038/s41598-018-37626-z
(gold open access, CC BY 4.0; CrossRef verified 22 Oct 2026). Correction of record: the 22 Oct overnight note called
this paper 'closed access' (gap G5); that was wrong.

Contents (read in full, 7 pp.): MH370-window signals at HA01 (E1 301.4 +/- 0.4 deg, recorded 01:34:40 UTC, 1900 +/-
200 km, -23.662 96.676; E2 234.6 +/- 0.4 deg, recorded 00:50:00 UTC, 1940 +/- 200 km, -43.487 94.469; both from
Kadri 2017), the water/sea-bottom transmission-route alternatives for E1 and E2 (Tables 1-2), the HA08s signals of
interest (Table 3) and a 25-minute HA08s data gap from 03:07 UTC on 8 March 2014 (Fig. 5 and text). It holds NO
received amplitude, NO source level, NO San Juan data and NO aircraft calibration; data 'by direct inquiry'.
Figures 1-6 are embedded rasters (saved at native resolution; Fig. 4 signal/cross-correlation/bearings at HA08s and
Fig. 5 raw HA08s data are traceable later if needed).

Tables are typed from the 200 dpi page render (the text layer garbles the route subscripts) and checked against the
text layer for every number. Outputs (--out, default results-data/digitised/kadri-2019/): kadri2019_table1_E1_routes.csv,
kadri2019_table2_E2_routes.csv, kadri2019_table3_ha08s_signals.csv, kadri2019_text_values.json,
figures/kadri2019_p<page>_<w>x<h>.<ext>, METHOD.json.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os

T1 = [("no transmission", 1900, 200, "24 50 S", "98 06 E"), ("T16 -> T15", 2226, 234, "23 01 S", "95 38 E"),
      ("T15 -> T14 -> T12", 2234, 235, "22 56 S", "95 35 E"), ("T15", 2876, 303, "19 10 S", "90 55 E"),
      ("T16 -> T12", 3664, 386, "14 18 S", "85 28 E"), ("T17", 3918, 412, "12 43 S", "83 46 E"), ("T18", 4294, 452, "10 21 S", "81 18 E")]
T2 = [("no transmission", 1940, 204, "43 29 S", "94 30 E"), ("T23 -> T22", 2276, 271, "44 36 S", "90 35 E"),
      ("T25 -> T24 -> T23 -> T21", 3180, 335, "46 53 S", "79 25 E"), ("T24", 3222, 339, "46 58 S", "78 50 E"),
      ("T26", 4384, 461, "48 01 S", "63 31 E")]
T3 = [("HA_30", "11:57", 247.4, "585 +/- 276", "9 34 S", "67 36 E", "Fig. 1 label '247 recorded @ 23:57 UTC' and text 'March 7th': 11:57 is a 12-hour reading of 23:57 UTC 7 Mar"),
      ("HA_31", "12:11", 170.9, "2300 +/- 250", "28 08 S", "76 20 E", "Fig. 1 label '170 recorded @ 00:11': 12:11 is a 12-hour reading of 00:11 UTC 8 Mar"),
      ("HA_32", "01:58", 241.3, "2860 +/- 900", "19 05 S", "48 32 E", "8 Mar"),
      ("HA_34a", "03:47", 170.9, "", "", "", "8 Mar"), ("HA_34b", "03:50", 173.0, "", "", "", "8 Mar"),
      ("HA_34c", "03:55", 170.9, "", "", "", "8 Mar")]


def dm(s):
    d, m, h = s.split(); v = int(d) + int(m) / 60.0
    return -v if h in "SW" else v


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "kadri-2019"))
    a = ap.parse_args(); import fitz
    out = os.path.abspath(a.out); fig = os.path.join(out, "figures"); os.makedirs(fig, exist_ok=True)
    raw = open(a.pdf, "rb").read(); doc = fitz.open(a.pdf)
    for name, rows in (("kadri2019_table1_E1_routes.csv", T1), ("kadri2019_table2_E2_routes.csv", T2)):
        with open(os.path.join(out, name), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["transmission_route", "distance_from_HA01_km", "distance_sd_km", "location_printed_lat", "location_printed_lon", "lat_deg", "lon_deg"])
            for r in rows:
                w.writerow([r[0], r[1], r[2], r[3], r[4], round(dm(r[3]), 4), round(dm(r[4]), 4)])
    with open(os.path.join(out, "kadri2019_table3_ha08s_signals.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["signal", "time_utc", "bearing_from_HA08s_deg", "distance_km", "location_printed_lat", "location_printed_lon", "date_note"])
        for r in T3:
            w.writerow(r)
    tv = dict(E1=dict(bearing_deg="301.4 +/- 0.4", distance_km="1900 +/- 200", centre=[-23.662, 96.676], recorded_utc="01:34:40", source_window_utc="01:11-01:16"),
              E2=dict(bearing_deg="234.6 +/- 0.4", distance_km="1940 +/- 200", centre=[-43.487, 94.469], recorded_utc="00:50:00", source_window_utc="00:25-00:31"),
              HA08s_position_printed=[-65.5445, 32.4730], HA08s_position_note="printed as (-65.5445, 32.4730): order and sign inconsistent with H08S (~ -7.6 S, 72.5 E); recorded as printed, not used",
              time_convention_note="Table 3 and the Fig. 4 panel titles (11.00, 12.00, 1.00, 3.00 UTC) use a 12-hour reading; Fig. 1 labels give 23:57, 00:11, 01:58, 03:47-03:55 UTC",
              HA08s_gap="25 minutes of missing data on all three hydrophones from 03:07 UTC (8 Mar 2014), Fig. 5 and text",
              military_bearings_deg=[219.2, 309.7], band="high-pass 5 Hz (Butterworth IIR)", speeds=dict(c_water_m_s=1470, c_solid_m_s=3550, text_c_solid_m_s=3350),
              data_availability="by direct inquiry to the author", not_in_paper="received amplitudes, source levels, San Juan, aircraft calibration")
    json.dump(tv, open(os.path.join(out, "kadri2019_text_values.json"), "w"), indent=1)
    saved = []
    for i, pg in enumerate(doc):
        for im in pg.get_images(full=True):
            info = doc.extract_image(im[0])
            if info["width"] >= 600:
                fn = f"kadri2019_p{i + 1:02d}_{info['width']}x{info['height']}.{info['ext']}"; open(os.path.join(fig, fn), "wb").write(info["image"]); saved.append(fn)
    txt = "".join(p.get_text() for p in doc)
    chk = {str(v): (str(v) in txt.replace("\u2009", "").replace(",", "")) for r in T1 + T2 for v in (r[1], r[2])}
    json.dump(dict(source="Kadri (2019) Sci. Rep. 9:912, doi 10.1038/s41598-018-37626-z, CC BY 4.0", pdf_sha256=hashlib.sha256(raw).hexdigest(),
                   method="tables typed from the page render, numbers checked against the text layer", text_layer_number_check=chk,
                   all_numbers_found=all(chk.values()), rasters=saved), open(os.path.join(out, "METHOD.json"), "w"), indent=1)
    print(all(chk.values()), saved)


if __name__ == "__main__":
    main()
