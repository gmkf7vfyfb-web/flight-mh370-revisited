t=open('handoff/aerial.txt').read()
print(t[:800])
for m in re.finditer(r'satellite imag|WorldView|DigitalGlobe|Gaofen|THEOS|Pleiades|Pléiades|Airbus|Japan',t,re.I):
    print('---',re.sub(r'\s+',' ',t[max(0,m.start()-300):m.end()+300]))