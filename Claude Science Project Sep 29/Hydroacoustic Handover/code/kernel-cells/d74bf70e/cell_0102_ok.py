d = pd.read_csv(host.artifact_path("394044c8-eab0-430e-b22a-93d52e39a45c"), comment="#")
print(d.columns.tolist()); 
txt = d.astype(str).agg(" ".join, axis=1)
bank = txt.str.contains("Chagos|Saya de Malha", case=False)
disc = txt.str.contains("DISCREPANCY")
print("bank rows:", list(d.index[bank]), "disc rows:", list(d.index[disc]), "bank & not disc:", int((bank & ~disc).sum()), "disc:", int(disc.sum()))