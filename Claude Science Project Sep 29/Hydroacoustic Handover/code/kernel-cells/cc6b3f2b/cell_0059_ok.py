
E = json.load(open("out/injection_ext/summary_ext.json")); PDU = pd.read_csv("out/injection_ext/pd_vs_snr_union.csv")
fu = pd.DataFrame([dict(key=k, **v) for k,v in E["fits_union"].items()]); fu[["logger","method","alpha","tau"]] = fu.key.str.split("|", expand=True)
for lg in ("3376","3274","3250"):
    print("---", lg, "SNR_50 (union grid)"); print(fu[fu.logger==lg].pivot_table(index="method", columns=["alpha","tau"], values="snr50").round(1).to_string())
print(PDU[(PDU.logger==3376)&(PDU.alpha==0.01)&(PDU.tau==1.0)].pivot_table(index="method", columns="snr_db", values="pd").round(2).to_string())
