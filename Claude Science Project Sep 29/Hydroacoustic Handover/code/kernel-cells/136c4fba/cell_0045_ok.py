r=host.exec_peek("81925b8f-4819-444b-9364-145a41aa12f9")
print(r.get("status"))
print((r.get("stdout") or "")[-2500:])
