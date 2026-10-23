i=a.find("acoustic search for the underwater locator",91500); 
j=[m.start() for m in re.finditer(r"underwater locator beacon",a)]; print(j[:30])
s=a.find("Haixun",95500); print(a[s-9000:s+6000])