i=t.find("4.7"); 
for m in re.finditer(r"4\.7\.|source level|source spectrum|signature|dB re", t):
    s=t[max(0,m.start()-150):m.start()+450].replace("\n"," ")
    print(m.group(), "::", s); print("---")