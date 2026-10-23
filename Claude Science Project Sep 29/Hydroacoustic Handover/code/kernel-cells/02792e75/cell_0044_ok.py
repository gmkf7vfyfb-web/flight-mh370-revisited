T="2014-03-08T00:00:00Z,2014-05-31T23:59:59Z"
for s,i in [x for x in sel if x[0] in ("WV01_Pan_L1B","WV02_Pan_L1B","GE01_Pan_L1B","QB02_Pan_L1B")]:
    a=gran_b(i,"90.5,-44.3,91.5,-43.7","2014-03-15T00:00:00Z,2014-03-18T00:00:00Z")
    b=gran_b(i,"85,-47,110,-18",T)
    c=gran_b(i,"98,-12,108,6","2014-03-08T00:00:00Z,2014-03-31T23:59:59Z")  # Malacca/Andaman/Gulf area
    print(s,"16Mar sighting",a,"| SE Indian Ocean box",b,"| Sumatra/Malacca",c)