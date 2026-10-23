
rp20 = totext("src/rp_2020.html"); open("src/rp_2020.txt","w").write(rp20)
j = rp20.find("Search Recommendation for MH370")
blk = rp20[j:j+14000]
# print only lines with numbers relevant to EoF
for ln in re.split(r"\n", blk):
    s=ln.strip()
    if re.search(r"(NM|fpm|glide|descent|impact|arc|fuel exhaust|0\.\d+g|ft\b|knot|FL\d)", s) and len(s)>40:
        print(s[:300])
