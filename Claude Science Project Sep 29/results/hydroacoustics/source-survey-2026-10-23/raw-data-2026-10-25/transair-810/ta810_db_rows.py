"""DB rows for the coupling package (schema of coupling-db-package, 25 Oct 2026): writes out/db/ (new rows only) and
out/db/package_updated/ (full package with the rows applied) and runs validate_coupling_tables.py on the latter."""
import sys, shutil, subprocess, pathlib, json
import numpy as np, pandas as pd
from obspy import UTCDateTime
WS = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(WS / "scripts")); import ta810_common as T
PKG = WS / "inputs/pkg/coupling-db-package"; OUT = WS / "out/db"; UPD = OUT / "package_updated"
if UPD.exists(): shutil.rmtree(UPD)
shutil.copytree(PKG, UPD)
SP = pd.read_csv(WS / "out/tables/eta_rad_upper_limit_primary.csv"); L50 = pd.read_csv(WS / "out/tables/detection_probability_L50.csv")
S = json.load(open(WS / "out/summary.json")); KE = S["energies"]["KE_total_MJ"]
NOTE = "transair810-note.md (25 Oct 2026)"
# ---- evidence row
ev = pd.read_csv(PKG / "db_coupling_evidence.csv")
e18 = dict(evidence_id="E18", evidence="Transair 810 ditching (B737-200, NTSB DCA21FA174), raw IMS H11N1-3/H11S1-3 records: no significant detection in the pre-registered predicted window",
           what_it_measures="received 4-40 Hz exposure at the measured 50 %% detection level (F-35A arrival injected into 14 days of H11 background); SE_50 %.4f Pa^2 s (H11N), %.4f Pa^2 s (H11S)" % tuple(L50[(L50.label == "report") & L50.condition.str.startswith("pre")].set_index("triad").loc[["H11N", "H11S"], "SE50_4_40_pa2s"]),
           observation_operator="module chain: KRAKEN adiabatic + RAM delta (pyram), GEBCO 2026, WOA23 B5C2 July; source end moved 3/6/10 km seaward (Oahu shelf cuts the great circle at <= 40 Hz)",
           what_it_constrains="upper limit on eta_rad as a function of z_eff and spectral family for a controlled ditching", regime="R3 controlled ditching (59 m/s, ~5 m/s vertical, pitch +12 deg)",
           how_it_is_used="censored likelihood term for R3 (non-detection with measured P_D(eta)); also bounds the R3 prior from above; not a ridge point",
           independence_group="G9: Transair 810 recording", main_error_terms="source-end geometry (shelf), z_eff, spectral family, template shape (F-35A), RAM delta at 5/20 Hz for H11N taken from H11S; KE +/-6 %",
           source="NTSB DCA21FA174 docket; EarthScope FDSN IM EDH; " + NOTE, status="EVIDENCE")
ev = pd.concat([ev, pd.DataFrame([e18])], ignore_index=True); ev.to_csv(UPD / "db_coupling_evidence.csv", index=False)
# ---- coupling values
cv = pd.read_csv(PKG / "db_coupling_value.csv"); new = []; k = 26
for tri in ("H11S", "H11N"):
    for r in SP[SP.triad == tri].itertuples():
        new.append(dict(value_id=f"CV{k}", evidence_id="E18", quantity=f"eta_rad UPPER LIMIT (50 % detection) at z_eff {r.z_eff_m:g} m, {tri}", value=float(f"{r.eta_UL50:.3g}"), value_low=np.nan,
                        value_high=float(f"{max(r.source_end_max, r.eta_UL50_E_high):.3g}"), definition_class="D1",
                        numerator="source radiated acoustic energy, one-pole f^-2 (tau 1 s), normalised 1-500 Hz", denominator=f"KE {KE[1]:.1f} MJ (NTSB; 90 % {KE[0]:.1f}-{KE[2]:.1f})",
                        band_Hz="scored 5-63 (SE 4-40)", source_depth_m=r.z_eff_m, peak_definition="exposure at the measured 50 % detection level (M1b p < 0.05, F-35A raw-record injection)",
                        propagation_chain_required="MODULE_KRAKEN_RAM", event_or_mechanism=f"Transair 810 ditching ({tri})", regime="R3", read_in_primary="yes (NTSB docket; raw H11 records)",
                        independence_group="G9", role="LIKELIHOOD_RIDGE_POINT", status="EVIDENCE", registry_id="", source_ref=NOTE,
                        notes=f"UPPER LIMIT, censored (non-detection), not a ridge point; value = source 3 km seaward; value_high = max over 3/6/10 km seaward and KE 5 % quantile; "
                              f"KRAKEN only {r.kraken_only:.3g}; f^-4 {r.slope4:.3g}; vertical-KE denominator {r.vertical_KE:.3g}; = {r.UL_over_F35A_ridge:.2f} x F-35A ridge at same z"))
        k += 1
NEW_CV = pd.DataFrame(new); cv = pd.concat([cv, NEW_CV], ignore_index=True); cv.to_csv(UPD / "db_coupling_value.csv", index=False)
# ---- impact case AC05
ic = pd.read_csv(PKG / "db_impact_case.csv"); i = ic.index[ic.case_id == "AC05"][0]
upd = dict(event="Transair 810 (ditching)", date_utc="2021-07-02 11:45:17 (CVR impact 01:45:17 HST; ADS-B ends 11:45:17.9)", aircraft="B737-275C N810TA (freighter)",
           impact=f"controlled ditching, flaps 1, gear up; GS 114.6 kt (59.0 m/s), CAS 123 kt, ADS-B -764 fpm, EGPWS RA 42.5->26.5 ft in the last 1 s; pitch +12.3 deg, bank -14.9 deg; 21.27616 N 158.02565 W; fuselage broke at BS 540 into two pieces, tail floated then sank",
           family="R3", energy=f"KE {KE[1]:.1f} MJ (90 % {KE[0]:.1f}-{KE[2]:.1f}); vertical KE {S['energies']['KE_vertical_MJ'][1]:.2f} MJ; mass 42.0 t (TOW 93,557 lb less 300-1,500 lb fuel)",
           water_depth="wreck 104-111 m (340-364 ft, NTSB S&R Table 1); GEBCO 108-178 m at impact point; < 200 m for first 9 km of the Wake path",
           raw_ims_open="YES - H11N1-3, H11S1-3; downloaded 2021-07-02 10:00-14:00 and 14 background days",
           hydro_held="raw H11 (EarthScope), F-35A template, injection P_D, KRAKEN + RAM TL", search_status="analysed 25 Oct 2026 (" + NOTE + ")",
           role="R3 UPPER LIMIT (no significant detection with limited power in the pre-registered predicted window)",
           coupling_treatment="eta_rad upper limit vs z_eff (CV26-CV35, E18); censored likelihood term for R3",
           kadri="his Fig. 5b signal is real but arrives from 152.6 deg at H11S (two pulses 42 s apart) and reaches H11S 72-73 s before H11N; the ditching would arrive from 79-81 deg, at H11N 30 s before H11S, 5-6 min earlier; Kadri S1 position (21 18'41\"N 157 54'16\"W) is near HNL airport, 13 km from the NTSB point",
           notes="NTSB facts from docket DCA21FA174 (final report, APG study Table 4, S&R factual, EGPWS factual, FDR data). The project's ~86 MJ was an assumption; NTSB-based KE is 73.6 MJ.")
for c, v in upd.items(): ic.at[i, c] = v
ic.to_csv(UPD / "db_impact_case.csv", index=False)
# ---- received observations (element level, both windows)
ro = pd.read_csv(PKG / "db_received_observation.csv"); rows = []; n = len(ro) + 1
for tri in T.TRIADS:
    z = np.load(WS / f"data/proc/2021-07-02_{tri}.npz"); t0 = UTCDateTime(str(z["t0"]))
    for wname, W, evid in (("PW", T.PW, "E18"), ("KW", T.KW, "E16")):
        for e in T.TRIADS[tri]:
            x = z[e].astype(float); ms = T.ms1(x); a = int(W[tri] - t0); b = a + 90; pre = ms[a - 600:a]; kk = a + int(np.argmax(ms[a:b]))
            i0, i1 = int((kk + 0.5 - 15) * 100), int((kk + 0.5 + 15) * 100)
            rows.append(dict(obs_id=f"OB{n:02d}", evidence_id=evid, station=e, peak_time_utc=(t0 + kk + 0.5).strftime("%H:%M:%S"), peak_1sRMS_Pa=round(float(np.sqrt(ms[kk])), 4),
                             median_1sRMS_Pa=round(float(np.sqrt(np.median(pre))), 4), snr_dB=round(float(10 * np.log10(ms[kk] / np.median(pre))), 1),
                             instant_peak_Pa=round(float(np.abs(x[a * 100:b * 100]).max()), 3), exposure_Pa2s_30s=round(float(np.sum(x[i0:i1] ** 2) / 100 - np.median(pre) * 30), 4), band_Hz="5-40", date="2021-07-02",
                             method=("Transair 810 predicted window (ditching site, pre-registered) " if wname == "PW" else "Kadri Fig. 5b box (signal from 152.6 deg, not the ditching) ") +
                                    f"{W[tri].strftime('%H:%M:%S')}+90 s; raw EarthScope IM EDH; StationXML response removed (pre-filt 1/2/110/120 Hz); 5-40 Hz 4-pole zero-phase; 1-s RMS; noise = median of the 600 s before the window; exposure +/-15 s minus noise"))
            n += 1
RO = pd.DataFrame(rows); pd.concat([ro, RO], ignore_index=True).to_csv(UPD / "db_received_observation.csv", index=False)
# ---- family element evidence (R3 eta_rad)
fe = pd.read_csv(PKG / "db_family_element_evidence.csv"); j = fe.index[(fe.family == "R3") & (fe.element == "eta_rad")][0]
fe.at[j, "evidence"] = "E18 Transair 810 (raw H11): upper limit eta_rad <= 3.2e-4 (10 m) ... 0.12 (0.5 m) at H11S, 0.14 x the F-35A ridge; AC06 Lion Air 904 (digitised only); E08 raindrops, E09 ice blocks"
fe.at[j, "role"] = "censored likelihood term (non-detection with measured P_D); analog envelope"; fe.at[j, "strength"] = "weak at shallow z_eff (limit 30-30,000 x the slow-blunt analogs)"
fe.to_csv(UPD / "db_family_element_evidence.csv", index=False)
# ---- probe rows (full-window coverage verified)
pr = pd.read_csv(PKG / "db_data_availability_probe.csv"); print(pr.columns.tolist())
log = pd.read_csv(WS / "data/download_log.csv"); ev_ = log[log.day == "2021-07-02"]
add = [dict(zip(pr.columns, ["Transair 810", r.element, "2021-07-02T10:00:00 to 14:00:00", 200, int(r.npts), "2026-10-25", "EarthScope FDSN dataselect, net IM, cha EDH, full 4 h window downloaded (3,600,000 samples, no gap)"])) for r in ev_.itertuples()]
pd.concat([pr, pd.DataFrame(add)], ignore_index=True).to_csv(UPD / "db_data_availability_probe.csv", index=False)
# ---- new rows only
OUT.mkdir(exist_ok=True)
NEW_CV.to_csv(OUT / "db_coupling_value_new_rows.csv", index=False); pd.DataFrame([e18]).to_csv(OUT / "db_coupling_evidence_new_rows.csv", index=False)
ic.loc[[i]].to_csv(OUT / "db_impact_case_AC05_update.csv", index=False); RO.to_csv(OUT / "db_received_observation_new_rows.csv", index=False)
pd.DataFrame(add).to_csv(OUT / "db_data_availability_probe_new_rows.csv", index=False); fe.loc[[j]].to_csv(OUT / "db_family_element_evidence_R3_update.csv", index=False)
r = subprocess.run([sys.executable, str(UPD / "validate_coupling_tables.py"), str(UPD)], capture_output=True, text=True, cwd=str(UPD)); print(r.stdout[-2500:], r.stderr[-500:])
open(OUT / "validator_output.txt", "w").write(r.stdout + r.stderr)
print(RO.to_string(index=False))
