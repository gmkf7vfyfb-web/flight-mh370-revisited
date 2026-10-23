BASE = 1394236800  # 2014-03-08 00:00:00 UTC
def hhmm(s): return str(dt.timedelta(seconds=float(s)))[:-3] if np.isfinite(s) else "nan"
spd = np.sqrt(Y[:,ci["velocity_east_mps"]]**2+Y[:,ci["velocity_north_mps"]]**2+Y[:,ci["velocity_up_mps"]]**2)
ke  = 0.5*Y[:,ci["mass_kg"]]*spd**2
vke = 0.5*Y[:,ci["mass_kg"]]*Y[:,ci["velocity_up_mps"]]**2
fam4 = Y[:,ci["family4_code"]]; onm = Y[:,ci["latent:onset_mechanism"]]
print("family4_code counts:", dict(zip(*[a.tolist() for a in np.unique(fam4, return_counts=True)])))
print("onset_mechanism counts:", dict(zip(*[a.tolist() for a in np.unique(onm, return_counts=True)])))
print("onset_code counts:", dict(zip(*[a.tolist() for a in np.unique(Y[:,ci['onset_code']], return_counts=True)])))
print("control_code counts:", dict(zip(*[a.tolist() for a in np.unique(Y[:,ci['control_code']], return_counts=True)])))
print("\nonset_mechanism x family4 (row counts):")
print(pd.crosstab(onm, fam4))

print("\n=== weighted quantiles (q05/25/50/75/95) ===")
quant = {
 "t_impact (UTC)": Y[:,ci["t_impact_s"]],
 "onset->impact (s)": Y[:,ci["t_impact_s"]]-Y[:,ci["t_onset_s"]],
 "impact speed (m/s)": spd,
 "flight_path_angle (deg)": Y[:,ci["flight_path_angle_deg"]],
 "vertical speed (m/s)": Y[:,ci["velocity_up_mps"]],
 "total KE (GJ)": ke/1e9,
 "vertical KE (GJ)": vke/1e9,
 "impact bank (deg)": Y[:,ci["latent:impact_bank_deg"]],
 "max descent rate (fpm)": Y[:,ci["latent:max_descent_rate_fpm"]],
 "time descending (s)": Y[:,ci["latent:time_descending_s"]],
 "arc distance (NM)": Y[:,ci["arc_distance_nm"]],
 "latitude (deg)": Y[:,ci["latitude_deg"]],
}
rows=[]
for k,v in quant.items():
    for o in ["none","r600/no-offset","both/no-offset"]:
        rows.append([k,o]+[round(x,3) for x in wq(v,P[o])])
T = pd.DataFrame(rows, columns=["quantity","option","q05","q25","q50","q75","q95"])
print(T.to_string(index=False))
print("\nimpact time as clock, option none:", [hhmm(x) for x in wq(Y[:,ci['t_impact_s']],P['none'])])
print("impact time as clock, both/no-offset:", [hhmm(x) for x in wq(Y[:,ci['t_impact_s']],P['both/no-offset'])])
print("onset  as clock, option none:", [hhmm(x) for x in wq(Y[:,ci['t_onset_s']],P['none'])])
