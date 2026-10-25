"""db_coupling_value rows (D2 Arons-relative ratios from raw peaks, role MODEL_ERROR_MEASURE) + validator run on a package copy."""
import shutil, subprocess, numpy as np, pandas as pd
pk = pd.read_csv("out/d2_arons.csv"); pk = pk[pk.band_Hz == "1-60"].rename(columns={"D2_ratio": "ratio"})   # same aggregation as d2_arons.csv: ratio of the triad-median peak
DECL = {"sj_charge": 108.0, **{f"fsst16_{i}": 6759.0 for i in range(1, 6)}, **{f"fsst21_{i}": 18000.0 for i in range(1, 4)}}
pk = pk[pk.event.isin(DECL)]
pk["grp"] = pk.event.map(lambda e: "sj_charge" if e == "sj_charge" else e[:6])
NAME = {"sj_charge": ("San Juan calibration charge (108 kg TNT, ~33 m), raw IMS", "108 kg TNT declared (Vergoz 2021)"),
        "fsst16": ("US Navy FSST 2016, raw IMS", "6,759 kg TNT each (Brown 2026 Table A.4)"), "fsst21": ("US Navy FSST 2021, raw IMS", "18,000 kg TNT each (Brown 2026 Table A.4)")}
cv = pd.read_csv("inputs/pkg/coupling-db-package/db_coupling_value.csv"); rows = []; n = int(cv.value_id.str[2:].astype(int).max()) + 1
for (g, tri), d in pk.groupby(["grp", "triad"]):
    if g == "sj_charge":
        el = pd.read_csv("out/peaks_by_band.csv"); el = el[(el.event == "sj_charge") & el.station.str.startswith(tri) & (el.station != "H10S1")]
        er = (el.range_km * 1e3 * (el["peak_1-60_Pa"] / 52.4e6) ** (1 / 1.13)) ** 3 / 108.0
        v, lo, hi, nn = float(d.ratio.iloc[0]), float(er.min()), float(er.max()), f"triad-median peak; low/high = single-element range ({len(el)} elements)"
    else:
        v, lo, hi, nn = d.ratio.median(), d.ratio.min(), d.ratio.max(), f"{len(d)} shots at {tri}; value = median over shots of the triad-median-peak ratio; low/high = shot range"
    rows.append(dict(value_id=f"CV{n:02d}", evidence_id="E12", quantity=f"Arons-relative ratio at {tri} (raw re-measurement, {len(d) if g != 'sj_charge' else 1} {'shots' if g != 'sj_charge' else 'event'})", value=round(v, 4), value_low=round(lo, 4), value_high=round(hi, 4),
                     definition_class="D2", numerator="Arons-equivalent in-channel yield from measured instantaneous peak, 1-60 Hz (P = 52.4e6 (R/W^1/3)^-1.13)",
                     denominator=NAME[g][1], band_Hz="1-60", source_depth_m=33.0 if g == "sj_charge" else np.nan, peak_definition="instantaneous peak, 1-60 Hz band-pass (Vergoz Fig. 2 band)",
                     propagation_chain_required="ARONS_1954", event_or_mechanism=NAME[g][0], regime="propagation", read_in_primary="yes (raw EarthScope IM EDH, 25 Oct 2026)",
                     independence_group="G4", role="MODEL_ERROR_MEASURE", status="EVIDENCE", registry_id="", source_ref="propagation-level-check-note.md (25 Oct 2026)",
                     notes=f"not an impact coupling; path and site scatter; {nn}; low/high = range; H10S1 excluded; band-sensitive (4-9 Hz and 5-20 Hz values in d2_arons.csv)"))
    n += 1
new = pd.DataFrame(rows); new.to_csv("out/db_coupling_value_new_rows.csv", index=False); print(new[["value_id", "quantity", "value", "value_low", "value_high", "event_or_mechanism"]].to_string())
shutil.copytree("inputs/pkg/coupling-db-package", "work/pkg_check", dirs_exist_ok=True)
pd.concat([cv, new]).to_csv("work/pkg_check/db_coupling_value.csv", index=False)
shutil.copy("out/db_received_observation.csv", "work/pkg_check/db_received_observation.csv")
p = subprocess.run(["python", "validate_coupling_tables.py", "."], cwd="work/pkg_check", capture_output=True, text=True); print(p.stdout); open("out/validator_output.txt", "w").write(p.stdout + p.stderr)
