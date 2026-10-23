res = host.collect(["e39ecd35-6803-46f5-9d70-35f665b6df17"], timeout=900)
r = res[0]
print(r.get("status"))
print("DEVIATIONS:", r.get("deviations"))
print("ARTIFACTS:", [a.get("filename") for a in (r.get("artifacts_created") or [])])
print((r.get("response") or "")[:6000])
