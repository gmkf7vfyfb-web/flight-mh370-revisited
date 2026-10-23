for i,r in d.iterrows():
    a=str(r.discrepancy_assessment)
    if re.search(r"Chagos|Saya|as row", a, re.I): print(i, r.drive_row, "DISC" if "DISCREPANCY" in a else "", a[:140])