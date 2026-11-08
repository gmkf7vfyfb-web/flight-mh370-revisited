"""Source check of the method-1 a_bar range (work order 2026-11-08 section 2 item 3).

Transcription of the transport-airplane summary tables of NACA Report 1347 (Fisher and Hoffman 1958,
'Ditching investigations of dynamic models and effects of design parameters on ditching characteristics',
NTRS 19930092335, Tables 26-37, pp. 21-28). Calm water, Langley tank no. 2, all values full scale.
Columns: transport, table, configuration, damaged (1 = scale-strength bottom / parts), landing attitude deg,
flap deg, landing speed kt, run length ft, printed maximum longitudinal deceleration g (None = not given),
printed average longitudinal deceleration g. Report 1347 p. 1 (printed): 'Average decelerations were derived
from the landing speeds and lengths of run', i.e. a = v^2 / (2 s), the same definition as the constant-deceleration
run-out of method 1 (s = v^2 / (2 a_bar)). The script recomputes a from v and s, checks it against the printed
value (printed values are rounded to 1/2 g), and summarises the range.
Also NACA RM SL9H05a Table I (Constellation with Speedpak, scale-strength bottom, flaps down; NTRS 20050071552).
Transcribed by the ocean settling module, 8 Nov 2026, from page images; check against the PDF before quoting.
"""
import csv, sys
KT = 0.514444; FT = 0.3048; G0 = 9.80665
N = None
T = {  # transport: (table, gross weight lb, model scale, rows (config, damaged, att, flap, v_kt, s_ft, gmax, gavg))
 "A": ("26", 130000, "0.043", [("standard", 0, 6, 0, 146, 1100, 2.5, 1), ("standard", 0, 6, 50, 113, 1040, 2.5, .5), ("standard", 0, 9, 0, 127, 1090, 2.5, .5),
        ("standard", 0, 9, 50, 104, 850, 1.5, .5), ("standard", 0, 12, 0, 119, 890, 1.5, .5), ("standard", 0, 12, 50, 100, 640, 2, .5),
        ("standard", 1, 6, 0, 146, 700, 6.5, 1.5), ("standard", 1, 6, 50, 113, 450, 6, 1.5), ("standard", 1, 9, 0, 127, 500, 5.5, 1.5),
        ("standard", 1, 9, 50, 104, 420, 5, 1), ("standard", 1, 12, 0, 119, 480, 6.5, 1.5), ("standard", 1, 12, 50, 100, 470, 5, 1)]),
 "B": ("27", 83000, "1/18", [("standard", 0, 4, 0, 148, 900, 6, 1), ("standard", 0, 4, 40, 91, 250, 4, 1.5), ("standard", 0, 9, 0, 115, 600, 2, 1),
        ("standard", 0, 9, 40, 79, 400, 4, .5), ("standard", 0, 12, 0, 102, 600, 1, 1), ("standard", 0, 12, 40, 74, 250, 3, 1),
        ("standard", 1, 4, 40, 91, 200, 4, 2), ("standard", 1, 9, 40, 79, 350, 3, 1), ("standard", 1, 12, 40, 74, 200, 4, 1),
        ("cargo container", 0, 4, 40, 95, 650, N, .5), ("cargo container", 0, 9, 40, 85, 500, 1.5, .5), ("cargo container", 0, 12, 40, 78, 250, 2, 1),
        ("hydro-ski", 0, 4, 40, 91, 1220, .5, .5), ("hydro-ski", 0, 9, 40, 79, 720, N, .5)]),
 "C": ("28", 43500, "1/15", [("standard", 0, 1, 0, 164, 850, 4, 1.5), ("standard", 0, 1, 39, 100, 350, 5, 1.5), ("standard", 0, 5, 0, 122, 650, 3, 1),
        ("standard", 0, 5, 39, 88, 400, 1.5, 1), ("standard", 0, 9, 0, 105, 600, 3.5, 1), ("standard", 0, 9, 39, 82, 400, 1, .5),
        ("standard", 1, 5, 0, 122, 250, 8, 2.5), ("standard", 1, 5, 39, 88, 300, 3.5, 1), ("standard", 1, 9, 0, 105, 300, 6, 1.5),
        ("standard", 1, 9, 39, 82, 300, 3, 1)]),
 "D": ("29", 50000, "1/15", [("standard", 0, 2, 40, 109, 700, 1, 1), ("standard", 0, 7, 40, 90, 300, 2, 1), ("standard", 0, 12, 40, 78, 350, 1, 1),
        ("standard", 1, 2, 40, 109, 450, 2.5, 1), ("standard", 1, 7, 40, 90, 350, 2, 1), ("standard", 1, 12, 40, 78, 300, 1, 1)]),
 "E": ("30", 44000, "1/14", [("standard", 0, 4, 45, 80, 385, N, .5), ("standard", 0, 9, 45, 71, 350, N, .5), ("standard", 0, 14, 45, 65, 350, N, .5),
        ("standard", 1, 4, 45, 80, 450, 2, .5), ("standard", 1, 9, 45, 71, 450, 1.5, .5), ("standard", 1, 14, 45, 65, 415, 1, .5)]),
 "F": ("31", 175000, "1/24", [("standard", 0, 2, 40, 109, 750, 2, .5), ("standard", 0, 7, 0, 157, 1150, 2, 1), ("standard", 0, 7, 40, 96, 800, 1, .5),
        ("standard", 0, 12, 0, 123, 900, 2, .5), ("standard", 0, 12, 40, 91, 700, 2.5, .5),
        ("standard", 1, 2, 40, 109, 550, 4, 1), ("standard", 1, 7, 40, 96, 500, 2.5, 1), ("standard", 1, 12, 40, 91, 500, 4.5, 1)]),
 "G": ("32", 35123, "1/14", [("standard", 0, 0, 55, 64, 150, 2.5, 1), ("standard", 0, 4, 0, 102, 200, 5, 2.5), ("standard", 0, 4, 55, 60, 200, 2, 1),
        ("standard", 0, 8, 0, 87, 150, 4, 2), ("standard", 0, 8, 55, 56, 150, 2, 1),
        ("standard", 1, 0, 55, 64, 150, 4, 1), ("standard", 1, 4, 55, 60, 150, 2, 1), ("standard", 1, 8, 55, 56, 150, 2, 1)]),
 "H": ("33", 255000, "1/25", [("standard", 0, 1, 45, 120, 1270, 2, .5), ("standard", 0, 5, 0, 155, 1400, 2.5, 1), ("standard", 0, 5, 45, 110, 690, 1.5, 1),
        ("standard", 0, 10, 0, 137, 1490, 2.5, .5), ("standard", 0, 10, 45, 102, 980, 1.5, .5),
        ("standard", 1, 1, 45, 120, 570, 2, 1), ("standard", 1, 5, 0, 155, 810, 5, 1.5), ("standard", 1, 5, 45, 110, 580, 3, 1),
        ("standard", 1, 10, 0, 137, 740, 5.5, 1), ("standard", 1, 10, 45, 102, 550, 3, 1),
        ("hydroflap", 1, 5, 45, 110, 690, 2, 1), ("hydroflap", 1, 10, 45, 102, 610, 2.5, 1)]),
 "I": ("34", 72000, "1/16", [("standard", 0, 2, 50, 98, 650, 2, .5), ("standard", 0, 7, 50, 87, 600, 1, .5), ("standard", 0, 12, 50, 79, 450, 1.5, .5),
        ("standard", 1, 7, 50, 87, 200, 6, 1.5), ("standard", 1, 12, 50, 79, 250, 4.5, 1),
        ("hydro-ski", 0, 2, 50, 95, 1300, N, .5), ("hydro-ski", 0, 7, 50, 88, 750, N, .5)]),
 "J": ("35", 84000, "1/16", [("standard", 0, 2, 50, 106, 700, 3, .5), ("standard", 0, 7, 50, 94, 600, 1, .5), ("standard", 0, 12, 0, 109, 550, 2, 1),
        ("standard", 0, 12, 50, 85, 450, 1.5, .5), ("standard", 1, 7, 50, 94, 250, 5, 1.5), ("standard", 1, 12, 50, 85, 250, 3.5, 1.5)]),
 "K": ("36", 160000, "1/24", [("standard", 0, 1, 45, 90, 450, 1, 1), ("standard", 0, 5, 0, 115, 800, 2, .5), ("standard", 0, 5, 45, 79, 450, .5, .5),
        ("standard", 0, 9, 0, 96, 600, 1, .5), ("standard", 0, 9, 45, 72, 450, 1, .5),
        ("standard", 1, 1, 45, 90, 300, 2.5, 1), ("standard", 1, 5, 45, 79, 300, 2, 1), ("standard", 1, 9, 45, 72, 300, 2, 1)]),
 "L": ("37", 130000, "1/20", [("standard", 0, 3, 45, 109, 650, 2, 1), ("standard", 0, 6, 45, 102, 500, 2, 1), ("standard", 0, 9, 0, 129, 800, 3, 1),
        ("standard", 0, 9, 45, 97, 450, 2, 1), ("standard", 1, 3, 45, 109, 400, 3, 1.5), ("standard", 1, 6, 45, 102, 400, 4, 1),
        ("standard", 1, 9, 45, 97, 350, 4, 1)]),
}
# NACA RM SL9H05a Table I, scale-strength Speedpak bottom, flaps down (speeds in mph; max g at 9 deg 1 1/2, at 12 deg 2; text p. 5)
SL9H05A = [(4, 110, 670, N), (9, 98, 490, 1.5), (12, 90, 270, 2)]


def rows():
    out = []
    for tr, (tab, wt, sc, rr) in T.items():
        for cfg, dmg, att, flap, vkt, sft, gmax, gavg in rr:
            v = vkt * KT; s = sft * FT; a = v * v / (2 * s) / G0
            out.append(dict(source="NACA Report 1347", table=tab, transport=tr, gross_weight_lb=wt, model_scale=sc, configuration=cfg,
                            damaged=dmg, landing_attitude_deg=att, flap_deg=flap, landing_speed_kt=vkt, landing_speed_mps=round(v, 2),
                            run_length_ft=sft, printed_max_g=gmax, printed_average_g=gavg, recomputed_average_g=round(a, 3),
                            rounding_check=int(abs(a - gavg) <= 0.25 + 1e-9 or (gavg == 0.5 and a < 0.75))))
    for att, vmph, sft, gmax in SL9H05A:
        v = vmph * 0.44704; s = sft * FT; a = v * v / (2 * s) / G0
        out.append(dict(source="NACA RM SL9H05a", table="I", transport="Constellation + Speedpak", gross_weight_lb=93000, model_scale="1/18",
                        configuration="scale-strength Speedpak bottom, flaps down", damaged=1, landing_attitude_deg=att, flap_deg="full down",
                        landing_speed_kt=round(vmph * 0.868976, 1), landing_speed_mps=round(v, 2), run_length_ft=sft, printed_max_g=gmax,
                        printed_average_g=N, recomputed_average_g=round(a, 3), rounding_check=""))
    return out


if __name__ == "__main__":
    r = rows()
    with open(sys.argv[1], "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(r[0])); w.writeheader(); w.writerows(r)
