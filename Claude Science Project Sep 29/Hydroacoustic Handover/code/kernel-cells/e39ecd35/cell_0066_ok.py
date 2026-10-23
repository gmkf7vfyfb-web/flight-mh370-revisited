
for ln in ht.split("\n"):
    if re.search(r"(2,?501|\[−28|\[-28|28, \+18|1\.7 Hz|2\.8 Hz|per 100 fpm|elevation|20 previous flights)", ln):
        print(ln.strip()[:230])
