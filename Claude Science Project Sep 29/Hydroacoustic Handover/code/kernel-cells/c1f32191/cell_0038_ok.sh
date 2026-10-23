cd /tmp/b11test && python - <<'EOF'
import pandas as pd, json
pd.set_option("display.width",250); pd.set_option("display.max_columns",30)
ul=pd.read_csv("upper_limits.csv"); print(ul[(ul.option=="D0")&(ul.p==0.5)&(ul.alpha==0.05)][["receivers","lat_lo","lat_hi","share","ess","eta95_bayes_logu_1e-6_1e-2","eta_excl95_classical","pnd_at_1e-2","pnd_at_1e-3","pnd_at_anchor","L_at_anchor","L_marg","posterior_median_eta"]].round(4).to_string())
ev=pd.read_csv("evidence_three_ways.csv"); print(ev[(ev.alpha==0.05)][["option","p","receivers","lnZ_hydro","median_lat_core","median_lat_combined","median_lat_alone","shift_median_deg","mass_north_33S_core","mass_north_33S_combined","mass_north_33S_alone","KL_core_vs_combined_nats"]].round(4).to_string())
print(pd.read_csv("holland_p1_vs_p0.csv").round(3).to_string())
bf=pd.read_csv("bayes_factors_conditionals.csv"); print(bf[["hypothesis","t_impact_utc","implied_impact_vs_0019","scored_receivers","prior_D0_mass_within_100km","L_imos_a0.05","L_ims_a0.05","Pnd_imos_marg_a0.05","lnBF_imos_a0.05","lnBF_ims_proxy_a0.05"]].round(3).to_string())
print(json.dumps({k:v for k,v in json.load(open("coincidence_summary.json")).items() if k!="loci"}, indent=0)); print(pd.read_csv("coincidence_locus.csv").round(4).T.to_string())
EOF