import json, pandas as pd
J = json.load(open("hydro/sct/synthetic-composer-test.json"))
df = pd.DataFrame(J["rows"])
b = df[df.config=="base"][["stations","bearing","info_bits_q10","info_bits_median","info_bits_q90","sd_ratio_median","shift_over_post_sd_median","err_prior_km_median","err_post_km_median","ess_median","verdict"]]
print(b.to_string(index=False, float_format="%.2f"))
print("prior along-arc sd km:", df.prior_along_sd_km.unique())
# range of info over all configs per station set / bearing
g = df.groupby(["stations","bearing"]).info_bits_median.agg(["min","max"]); print(g.to_string(float_format="%.2f"))
print(df.groupby(["stations","bearing"]).verdict.agg(lambda v: dict(v.value_counts())).to_string())
df.to_csv("hydro/sct/synthetic-composer-test.csv", index=False)
