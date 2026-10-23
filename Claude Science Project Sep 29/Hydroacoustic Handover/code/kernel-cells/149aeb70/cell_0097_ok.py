import pandas as pd
m = kw[kw["event"].astype(str).str.contains("major")]
pd.set_option("display.width", 250)
print(m[["event","logger","file","win_a","win_b","covered_s","bearing","t_H01W","d1","d1_t","d2","d2_t","spl_max","snr_db","p_d1","p_d2","detected"]].to_string(index=False))
kp = pd.read_csv(host.artifact_path("8fa68f2f-64ed-4328-9ea8-cd4b7899420c"))
print("\nkadri_trace_pairs cols:", list(kp.columns))
print(kp.head(4).to_string(index=False))
print("\ntrace time span:", kp.filter(like="t_").describe().to_string() if any(c.startswith("t_") for c in kp.columns) else "n/a")
