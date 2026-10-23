
src='results/kadri-haixun-conditional-2026-10-18/settling/'
K=lambda n,v,u='',b='',f='README.md':dict(name=n,value=v,unit=u,branch_or_case=b,source_file=src+f)
out={
 "summary":("Settling leg (pre-registration Q8) on run J, 00:19 option none (weight column only), settling physics PROVISIONAL. "
  "Seabed depth at the Haixun 01 first contact is 4,589 m (AusSeabed 150 m; GEBCO_2026 4,583 m, TID 11 multibeam), 4,558-4,619 m within 2 km; the second contact 2/3 km west is 4,578/4,573 m; the corrected bearing x 7th-arc crossing is 4,466 m (GEBCO_2026, gravity-predicted TID 40, no AusSeabed coverage). "
  "Beyond the arc along the 306.18 deg strip the depth is almost all GEBCO TID 40: about 3,750-3,900 m at 50-100 km, then 5,400-5,700 m at 150-250 km. "
  "Under GLORYS12V1, for run J rows in the locality L, a detached recorder rests 0.18/0.34/0.50 km (p50/p90/p99) from the impact, engines and gear within 0.44 km at p99, and a recorder retained in its aft fuselage section 0.38/2.49/10.27 km (intact family p99 13.9 km, driven by the float phase). "
  "Branches T (00:52:03) and C (00:54:30) give the same displacements within 0.06 km at p99 for dense parts. HYCOM GOFS 3.1 (53.X, 00Z-03Z, Haixun kernel only) raises the detached-recorder p90 from 0.36 to 0.46 km and the retained p99 from 11.7 to 12.9 km. "
  "Inverse: a beacon within 2 km of the Haixun contact needs an impact within 2.2 km (p99) of it for a detached recorder or 11.6 km (p99) for a retained one; that region is wholly inside the wide (1 deg) Kadri strip, about half inside the core strip, and never on or beyond the 7th arc (gap at least 18.9 km). "
  "No Kadri eq. 4 impact draw (0 of 40,000 per branch and class, both T and C) puts a recorder within 2 km of Haixun under the central sea-level geometry (P < 7.5e-5); with BTO and altitude spread at 00:19:29 the fraction is 2.2e-4 (T) and 7.5e-5 (C), so joint H_K and H_H depends on arc geometry, not on settling. "
  "Run J does reach the Haixun disc (1,084 rows within 2 km); settling changes the prior mass of 'recorder within 2 km' relative to the impact-point mass by 0.98-1.10 across route strata, so settling adds no information to H_H. Near-Haixun prior masses rest on ESS 5-60 and are provisional."),
 "key_numbers":[
  K("Seabed depth, Haixun 01 first contact (AusSeabed 150 m)","4589","m","Haixun",'seabed_depth_sites.csv'),
  K("GEBCO_2026 depth at Haixun first contact","4583 (TID 11)","m","Haixun",'seabed_depth_sites.csv'),
  K("Depth range within 2 km of Haixun contact","4558-4619","m","Haixun",'seabed_depth_sites.csv'),
  K("Depth, second contact 2 km / 3 km west","4578 / 4573","m","Haixun",'seabed_depth_sites.csv'),
  K("Depth at bearing x 7th arc (GEBCO_2026 TID 40)","4466","m","crossing",'seabed_depth_sites.csv'),
  K("Detached recorder seabed displacement p50/p90/p99","0.18 / 0.34 / 0.50","km","run J rows in L, GLORYS12V1",'settling_displacement_by_case_class_family.csv'),
  K("Recorder retained in aft fuselage displacement p50/p90/p99","0.38 / 2.49 / 10.27","km","run J rows in L, GLORYS12V1",'settling_displacement_by_case_class_family.csv'),
  K("Engine / landing gear displacement p99","0.43 / 0.44","km","run J rows in L, GLORYS12V1",'settling_displacement_by_case_class_family.csv'),
  K("Detached recorder p99, branch T / C","0.56 / 0.55","km","Kadri T, C",'settling_displacement_by_case_class_family.csv'),
  K("Detached recorder p90 GLORYS12V1 vs HYCOM","0.36 vs 0.46","km","Haixun kernel",'settling_ocean_sensitivity_at_haixun.csv'),
  K("Retained recorder p99 GLORYS12V1 vs HYCOM","11.65 vs 12.90","km","Haixun kernel",'settling_ocean_sensitivity_at_haixun.csv'),
  K("Inverse region radius p99 (detached / retained)","2.21 / 11.6","km","H_H",'settling_inverse_region_haixun.csv'),
  K("Min gap from inverse region to sea-level 7th arc","19.8 (detached) / 18.9 (retained)","km","H_H vs H_K",'settling_inverse_region_haixun.csv'),
  K("Kadri impacts min distance to Haixun (central geometry)","21.5 (T) / 21.7 (C)","km","T, C",'settling_kadri_branches_forward.csv'),
  K("Fraction of Kadri recorder rest points within 2 km of Haixun, BTO+altitude spread","2.2e-4 (T) / 7.5e-5 (C)","","T, C",'settling_kadri_locus_bto_altitude_sensitivity.csv'),
  K("Settling ratio P(recorder rests within 2 km)/P(impact within 2 km), route strata","0.98-1.10","","run J, 00:19 option none",'settling_prior_mass_rest_near_haixun_absolute.csv'),
  K("Run J prior P(detached recorder within 2 km of Haixun), route strata","1.3e-6 to 3.1e-6 (provisional, ESS 8-60)","","run J weight column, 00:19 option none",'settling_prior_mass_rest_near_haixun_absolute.csv'),
 ],
 "likelihood_terms":[
  {"hypothesis":"H_H","term":"settling ratio P(recorder rests within 2 km | run J)/P(impact within 2 km | run J)","log_bayes_factor_or_ratio":"ln ratio 0.0 to +0.1 (detached), 0.0 to +0.14 (retained); treat as 0","caveats":"transform, not evidence; ESS 5-60 near Haixun; 00:19 option none"},
  {"hypothesis":"H_K^T and H_H jointly","term":"P(recorder within 2 km of Haixun | Kadri eq.4 impact)","log_bayes_factor_or_ratio":"< 7.5e-5 central geometry; 2.2e-4 with BTO/altitude spread","caveats":"compatibility ratio, not a Bayes factor; geometry-driven"},
  {"hypothesis":"H_K^C and H_H jointly","term":"P(recorder within 2 km of Haixun | Kadri eq.4 impact)","log_bayes_factor_or_ratio":"< 7.5e-5 central geometry; 7.5e-5 with BTO/altitude spread","caveats":"compatibility ratio, not a Bayes factor; geometry-driven"},
 ],
 "artifacts":["README.md c92db8c7-22cf-48f4-b2c2-1c2a4c6d4737","fig_settling_haixun_map.png 95dbb823-bad0-42bb-85ce-7f9961effb7b","fig_settling_displacement.png fd29d4ca-ed38-4414-924f-60f934231d9f",
  "seabed_depth_sites.csv 41ae5fd2-f01b-4f70-aa3a-3d911b1d3ecb","seabed_depth_bearing_strip.csv 1b4e8058-25b4-44db-bf3d-fe5ecbadd662","settling_displacement_by_case_class_family.csv 68046978-b791-44b9-9a5d-0ff08d1664a4",
  "settling_inverse_region_haixun.csv a927619f-1079-4a09-bff3-8a97ea561ca1","settling_prior_mass_rest_near_haixun_absolute.csv 36088e21-7397-4411-9b58-44683409b334","settling_prior_mass_rest_near_haixun_given_L.csv 0f68238d-f2ba-44e3-8227-a56ac377df37",
  "settling_ocean_sensitivity_at_haixun.csv 3cbd6684-d61c-49aa-b59c-79df22cc6e38","settle_mc.py 934a76ee-a787-438f-92a1-32c79b1d7b6e"],
 "commit":"4ac41c8 on claude-science-sep29 (results/kadri-haixun-conditional-2026-10-18/settling/; entry in coordination/architecture.md)",
 "open_issues":[
  "G-S1: recorder detachment probability per breakup family not modelled; detached and retained modes reported separately.",
  "G-S2: HYCOM sensitivity limited to the Haixun kernel, 8 Mar 2014 00Z and 03Z, 24-27 S 100-102.6 E (NCSS did not respond; OPeNDAP slow).",
  "G-S3: current extrapolated 180-340 m below the ocean model bottom (hold deepest level).",
  "G-S4: run J prior mass near Haixun rests on ESS 5-60 (weight column) and 1-3 (with r600/no-offset loglik): provisional.",
  "00:19 option weights (option_table_0019.seed_terms, D{d} total q=0.333 C2 silent) not applied to prior-mass numbers; composer should apply them.",
  "Beacon-physics leg used 4,577 m (GEBCO 2020); AusSeabed 150 m gives 4,589 m.",
  "Driver cells (case set-up) live in session lineage, not yet a standalone script in the repo; settle_mc.py and extract_L.py are committed.",
 ],
}
r=host.submit_output(out,completion_bullets=["Sampled seabed depth at Haixun, second contact, arc crossing and along the bearing strip","Computed recorder and heavy-part seabed displacement on run J rows and Kadri T/C impacts, GLORYS12V1 with HYCOM sensitivity","Mapped the inverse impact region for a beacon within 2 km of Haixun and tested it against the Kadri strip, locus and run J","Committed note 4ac41c8 and saved figures and tables"],
 deviations=["Settling physics run as a vectorised Python port of physics.rs (9330d4c), not the Rust engine module.",
  "00:19 option weights not applied: run J 'weight' column only (labelled '00:19 option none'), plus one exp(loglik r600/no-offset) sensitivity for L-conditional numbers.",
  "HYCOM sensitivity run only at the Haixun kernel (20,000 draws), with 2 time steps (00Z, 03Z 8 Mar 2014) and a 3 x 2.6 deg box; not run for run J L rows or Kadri branches.",
  "Kadri synthetic impacts use sea-level arc and central BTO for the headline; impact conditions resampled from run J L rows independently of eq. 4 speed.",
  "Detached-recorder element class is a new declared educated estimate (grade C), not in breakup.toml; diffusivity K log-uniform 10-200 m2/s used as a stand-in for the shared provisional prior, which was not read.",
  "Per-row settling draws near Haixun: 50 per row within 4 km (detached), 8 per row within 20 km (retained); density profile from one GLORYS12V1 column."])
print(r)
