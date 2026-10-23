r = host.collect(["95790ff1-95f1-4b29-b51a-bed538c1797b","43360090-fdd3-4918-a664-de9fef7e80f6"], timeout=5)
for x in r: print(x.get("name"), x.get("status"))