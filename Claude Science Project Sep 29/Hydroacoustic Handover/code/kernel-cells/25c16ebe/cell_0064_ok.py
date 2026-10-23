rows = [
 ["handoff_fuel_state_live","711648 distinct","realised flame-out times in one stratum-seed; fallback_fuel_kg=2000 not in use","core request 1 has landed"],
 ["require_power_until","m0011","core rejects loss of the second engine before 00:11","hard_reject = true; first-engine loss permitted"],
 ["core_tanks_single_engine","tanks=2, single_engine=true","core models the single-engine fuel and performance phase","inop_flow_scale 0.5; hold-taper driftdown 207-227 KCAS"],
 ["engines_at_onset_none","0.5687","weight share with no engine thrusting at descent onset","held-out weighting"],
 ["engines_at_onset_one","0.3694","weight share with exactly one engine thrusting at onset",""],
 ["engines_at_onset_both","0.0619","weight share with both engines thrusting at onset",""],
 ["flameout_col_is_final","+288 s median","final flame-out minus takeover for A-family rows with one engine running at takeover","n=85,018; q95 +1,113 s"],
 ["flameout_col_at_takeover","-2.4 s median","same, for A-family rows with no engine running at takeover","n=325,071"],
 ["single_engine_phase_share_A","0.2248","A-family weight taking over more than 60 s before its final flame-out","a real single-engine phase inside the EoF stage"],
 ["eof_asymmetric_params","none","asymmetric-thrust / yaw / rudder parameters in the EoF envelope","only windmilling_per_engine, a symmetric drag increment"],
 ["already_dry_at_handoff","0.0547","weight share taking over at the 00:11 hand-off epoch itself",""],
 ["flameout_between_arcs","0.5436","weight share running dry between 00:11 and 00:19:37","model output, not an assumption"],
 ["never_dry_before_impact","0.0656","weight share that impacts with fuel remaining","ditchings under power"],
 ["mass_at_impact_q05_q95","174194 / 174782","mass at impact (kg) against zero-fuel weight 174,196 kg","almost all impacts are dry"],
]
with open("eof-audit-measurements.csv","a",newline="") as f: csv.writer(f).writerows(rows)
print(sum(1 for _ in open("eof-audit-measurements.csv")), "rows")
