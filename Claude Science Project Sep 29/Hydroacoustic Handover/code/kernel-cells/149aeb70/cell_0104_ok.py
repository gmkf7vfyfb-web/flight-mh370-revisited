f = host.findings()
print([(x["id"], x["verdict"], x["claim"][:60]) for x in f["findings"]])
