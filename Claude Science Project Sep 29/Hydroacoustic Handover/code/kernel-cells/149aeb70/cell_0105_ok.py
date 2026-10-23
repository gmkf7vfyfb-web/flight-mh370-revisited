f = host.findings()
w = [x for x in f["findings"] if x["verdict"] == "warn"][0]
print(w["claim"]); print("---"); print(w["evidence"])
