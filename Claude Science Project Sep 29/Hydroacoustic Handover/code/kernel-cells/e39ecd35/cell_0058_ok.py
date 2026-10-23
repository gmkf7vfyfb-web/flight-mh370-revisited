
k = bank.find("MH370 End-of-Flight with Banked Descent")
blk = bank[k:k+11000]
for ln in blk.split("\n"):
    s=ln.strip()
    if len(s)>50 and re.search(r"(NM|fpm|g\b|bank|descent|simulat|impact|knot|ft\b)", s):
        print(s[:320])
