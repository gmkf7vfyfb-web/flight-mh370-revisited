"""Rows for db_coupling_value.csv and db_received_observation.csv from the raw F-35A analysis (track 1, 25 Oct 2026),
then the package validator on the package tables plus these rows. Usage (from t1/): python scripts/make_db_rows.py"""
import sys, pathlib, pickle, shutil, subprocess
import numpy as np, pandas as pd, obspy
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "out"; PKG = ROOT / "inp/pkg/coupling-db-package"
sys.path.insert(0, str(ROOT / "scripts")); import raw_lib as RL  # noqa
DEPTHS = [1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0]
RD = pd.read_csv(OUT / "f35a-raw-ridge.csv"); D4 = pd.read_csv(OUT / "f35a-raw-d4.csv"); D2 = pd.read_csv(OUT / "f35a-raw-d2.csv")
A = pickle.load(open(OUT / "analysis.pkl", "rb"))
def hms(s): s = float(s); h = int(s // 3600); m = int((s - h * 3600) // 60); return f"{h:02d}:{m:02d}:{s - h * 3600 - m * 60:06.3f}"
FAM = {"F2": "one-pole f^-2, corner 1/tau with tau 3.30 s (module form)", "Ffit_c": "fitted power law above a fitted corner (post hoc)",
       "Ffit": "fitted power law f^-n (n from the implied source ESD slope 5-40 Hz), corner 1/tau with tau 3.30 s", "F4": "f^-4, corner 1/tau with tau 3.30 s"}
CH = {"KRAKEN_RAM": "MODULE_KRAKEN_RAM", "KRAKEN_ONLY": "MODULE_KRAKEN_ONLY"}
REF = "f35a-raw-ridge-note.md (track 1, 25 Oct 2026); f35a-raw-ridge.csv; pre-registration artifact 493a290e"
rows = []; n = 26; excluded = []
def g3(v): return float(f"{v:.3g}")
for fam in ("F2", "Ffit_c", "Ffit", "F4"):
    for chn, rdl in (("KRAKEN_RAM", "module"), ("KRAKEN_ONLY", "none"), ("KRAKEN_RAM", "own_new")):
        if rdl == "own_new" and fam not in ("F2", "Ffit_c"):
            continue
        for zs in DEPTHS:
            r = RD[(RD.family == fam) & (RD.chain == chn) & (RD.ram_delta == rdl) & (RD.src_depth_m == zs) & (RD.score_band_hz == "5-63")].iloc[0]
            if r.eta_pooled >= 1.0:
                excluded.append((fam, chn, rdl, zs, round(r.eta_pooled, 3))); continue
            ramtxt = {"module": "; RAM delta = module H11S delta (results-data/ram_check, 5-40 Hz) for both triads; z<=10 m uses 10 m, z>=30 m uses 30 m, 20 m the mean",
                      "own_new": "; RAM delta = new pyram run per triad (H11N and H11S own deltas, 5-40 Hz, z 10/20/30/50 m; z<10 m uses 10 m); sensitivity to the module convention",
                      "none": "; epistemic-switch alternative to KRAKEN+RAM"}[rdl]
            rows.append(dict(value_id=f"CV{n}", evidence_id="E01", quantity=f"eta_rad at z_eff {zs:g} m, S = {fam}" + (", per-triad RAM delta" if rdl == "own_new" else ""),
                value=g3(r.eta_pooled), value_low=g3(r.eta_low_68), value_high=g3(min(r.eta_high_68, 1.0)), definition_class="D1",
                numerator=f"source radiated acoustic energy, spectral family {fam}: {FAM[fam]}; normalised 1-500 Hz", denominator="KE 900 MJ (Brown et al. 2026; +/-200 MJ in range)",
                band_Hz="scored 5-63 (SE_obs 4-64)", source_depth_m=zs, peak_definition="exposure (module operator obs.py on raw 1-s RMS, Metz frame)", propagation_chain_required=CH[chn],
                event_or_mechanism="F-35A far field (Wake), raw records", regime="R1", read_in_primary="yes (raw EarthScope IM EDH waveforms, 6 elements)", independence_group="G1",
                role="MODEL_ERROR_MEASURE" if rdl == "own_new" else "LIKELIHOOD_RIDGE_POINT", status="EVIDENCE", registry_id="", source_ref=REF,
                notes=(f"ridge point, not a parameter; geometric mean of triads H11N {r.eta_H11N:.3g} / H11S {r.eta_H11S:.3g}; elements {r.eta_element_min:.3g}-{r.eta_element_max:.3g}; "
                       f"68 % range = energy, element, station and location terms in quadrature (Metz-consistent point P gives {r.eta_at_P:.3g}); corner {r.corner_hz:.3g} Hz, exponent {r.exponent:.3g}; "
                       f"family/F2 ratio {r.ratio_family_over_F2:.3g}" + ramtxt + ("; corner fit post hoc (not pre-registered)" if fam == "Ffit_c" else "")
                       + ("; raw-record counterpart of CV01-CV03 / CV10-CV12" if fam == "F2" and rdl != "own_new" and zs in (2, 10, 30) else ""))))
            n += 1
for chn in ("KRAKEN_RAM", "KRAKEN_ONLY"):
    for zs in DEPTHS:
        r = D4[(D4.chain == chn) & (D4.src_depth_m == zs)].iloc[0]
        rows.append(dict(value_id=f"CV{n}", evidence_id="E01", quantity=f"in-band radiated energy fraction 4-64 Hz at z_eff {zs:g} m", value=g3(r.eta_D4_4_64),
            value_low=g3(min(r.triad_min_4_64, r.eta_D4_4_64 * 900 / 1100)), value_high=g3(max(r.triad_max_4_64, r.eta_D4_4_64 * 900 / 700)), definition_class="D4",
            numerator="in-band 4-64 Hz source radiated energy (observed band shares x SE_obs, TL inverted per band)", denominator="KE 900 MJ", band_Hz="4-64", source_depth_m=zs,
            peak_definition="exposure", propagation_chain_required=CH[chn], event_or_mechanism="F-35A far field (Wake), raw records", regime="R1", read_in_primary="yes (raw waveforms)",
            independence_group="G1", role="CONSISTENCY_CHECK", status="EVIDENCE", registry_id="", source_ref=REF,
            notes=f"lower bound of D1 at the same depth; low/high = triad range and E 1100/700 MJ; RAM delta module convention; measured bands 2-100 Hz give {r.eta_D4_measured_2_100:.3g}"))
        n += 1
for lab, band in (("4-64 Hz instantaneous", "4-64"), ("4-40 Hz instantaneous", "4-40"), ("2-100 Hz instantaneous", "2-100"), ("4-64 Hz 1-s RMS peak", "4-64 (1-s RMS)")):
    r = D2[D2.peak_definition == lab].iloc[0]
    rows.append(dict(value_id=f"CV{n}", evidence_id="E05", quantity=f"Arons-equivalent coupling recomputed from raw {lab} peak", value=g3(r.eta_gmean), value_low=g3(r.eta_lo_E1100),
        value_high=g3(r.eta_hi_E700), definition_class="D2", numerator="Arons-equivalent in-channel TNT energy, P = 52.4e6 (R/W^(1/3))^-1.13 Pa, 4.184 MJ/kg", denominator="KE 900 MJ (range 700-1100)",
        band_Hz=band, source_depth_m=np.nan, peak_definition=f"{lab} |p| max over peak +/-15 s, {r.P_min_pa:.3g}-{r.P_max_pa:.3g} Pa over 6 elements; R = 3248.8 / 3341.5 km",
        propagation_chain_required="ARONS_1954", event_or_mechanism="F-35A, raw records", regime="R1", read_in_primary="yes (raw waveforms)", independence_group="G1",
        role="CONSISTENCY_CHECK", status="EVIDENCE", registry_id="", source_ref=REF,
        notes=f"geometric mean of 6 elements (element range {r.eta_min:.3g}-{r.eta_max:.3g} at 900 MJ); low/high = element extremes at E 1100/700 MJ; same recording as E01, never combined with a TL model; Brown's 0.7 Pa (band not stated) gives 2.08e-4"))
    n += 1
cv0 = pd.read_csv(PKG / "db_coupling_value.csv"); CV = pd.DataFrame(rows)[cv0.columns]
inv = obspy.read_inventory(str(ROOT / "data/H11_resp_2019-04-09.xml")); OB = []
for i, el in enumerate(RL.ELS):
    o = A["OBS"][el]; tr = RL.to_pa(obspy.read(str(ROOT / f"data/{el}_event.mseed"))[0], inv); ts = tr.stats.starttime - RL.DAY
    x = RL.bp(tr.data, 4, 64); i0 = int((o["peak_t"] - 15 - ts) * RL.FS); i1 = int((o["peak_t"] + 15 - ts) * RL.FS)
    tc, ms = RL.ms_1s(x); tabs = ts + tc; nsm = (tabs >= RL.NOISE_SEG[0] - RL.DAY) & (tabs <= RL.NOISE_SEG[1] - RL.DAY); med = float(np.sqrt(np.median(ms[nsm])))
    OB.append(dict(obs_id=f"OB{7 + i:02d}", evidence_id="E01", station=el, peak_time_utc=hms(o["peak_t"])[:8], peak_1sRMS_Pa=round(10 ** (o["peak_db"] / 20) * 1e-6, 4),
        median_1sRMS_Pa=round(med, 4), snr_dB=round(o["peak_db"] - 20 * np.log10(med / 1e-6), 1), instant_peak_Pa=round(o["ipk_4_64_pa"], 3),
        exposure_Pa2s_30s=round(float(np.sum(x[i0:i1] ** 2) / RL.FS - med ** 2 * 30), 4), band_Hz="4-64", date="2019-04-09",
        method=("raw EarthScope IM EDH 10:30-11:40 UTC (track 1, 25 Oct 2026); full StationXML response removed (pre-filt 0.5/1/110/120 Hz); 4-pole zero-phase 4-64 Hz (Metz band); "
                "1-s moving RMS, 0.02 s step; median 1-s RMS over 10:45-11:01 UTC; exposure = sum x^2 dt over peak +/-15 s minus median-noise^2 x 30 s. Module operator (obs.py, Metz frame): "
                f"SE {o['se_pa2s']:.4f} Pa^2 s, SNR {o['snr_db']:.1f} dB, -6 dB width {o['w6_s']:.2f} s, 5-95 % span {o['span_5_95_s']:.2f} s; onset {hms(o['onset_t'])}; "
                f"instantaneous peak 2-100 Hz {o['ipk_2_100_pa']:.3f} Pa")))
ob0 = pd.read_csv(PKG / "db_received_observation.csv"); OBd = pd.DataFrame(OB)[ob0.columns]
CV.to_csv(OUT / "f35a-raw-coupling-rows.csv", index=False); OBd.to_csv(OUT / "f35a-raw-received-observation-rows.csv", index=False)
V = OUT / "validate"; shutil.rmtree(V, ignore_errors=True); shutil.copytree(PKG, V)
pd.concat([cv0, CV]).to_csv(V / "db_coupling_value.csv", index=False); pd.concat([ob0, OBd]).to_csv(V / "db_received_observation.csv", index=False)
res = subprocess.run([sys.executable, "validate_coupling_tables.py", "."], cwd=V, capture_output=True, text=True)
open(OUT / "validator_output.txt", "w").write(res.stdout + res.stderr)
print(len(CV), "coupling rows; excluded (eta >= 1, energy limit):", excluded); print(OBd.drop(columns="method").to_string()); print(res.stdout[-900:])
