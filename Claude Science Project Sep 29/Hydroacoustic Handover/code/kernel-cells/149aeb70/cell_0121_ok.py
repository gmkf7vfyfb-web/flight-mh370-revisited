w = [x for x in host.findings()["findings"] if x["verdict"] == "warn"]
for x in w:
    print(x["id"]); print(x["claim"]); print("---"); print(x["evidence"][:1200]); print("===")
