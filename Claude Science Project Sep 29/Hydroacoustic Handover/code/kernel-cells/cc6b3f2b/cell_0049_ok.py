
import pandas as pd, numpy as np, json
PD = pd.read_csv("out/injection/pd_vs_snr.csv"); S = json.load(open("out/injection/summary.json"))
pd.set_option("display.width", 250)
for a in (0.01, 0.001):
    t = PD[(PD.logger.astype(str)=="3376")&(PD.alpha==a)].pivot_table(index=["method","tau"], columns="snr_db", values="pd")
    print(f"--- 3376 alpha={a}"); print(t.round(2).to_string())
fits = pd.DataFrame([dict(key=k, **v) for k,v in S["fits"].items()])
fits[["logger","method","alpha","tau"]] = fits.key.str.split("|", expand=True)
f = fits[(fits.logger=="3376")].pivot_table(index="method", columns=["alpha","tau"], values="snr50")
print(f.round(1).to_string())
print(S["bg_median_level_db"], S["n_null_windows"])
