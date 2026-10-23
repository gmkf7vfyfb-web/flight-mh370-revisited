for k in ['fluid','sightings','csiro3']:
    t=open(f'handoff/{k}.txt').read()
    print('#####',k,t[:300].replace('\n',' '))
    for m in re.finditer(r'satellite imag|WorldView|DigitalGlobe|Digital Globe|Gaofen|THEOS|Thai|Japan|Pleiades|Pléiades|Airbus|Tomnod|122|SPOT|overpass|UTC',t,re.I):
        print('---',re.sub(r'\s+',' ',t[max(0,m.start()-250):m.end()+300]))