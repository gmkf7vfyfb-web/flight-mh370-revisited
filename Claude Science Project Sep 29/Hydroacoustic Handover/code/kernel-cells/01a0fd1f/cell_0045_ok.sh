pip -q install pyproj 2>&1|tail -1; python - <<'EOF'
from pyproj import Geod
g=Geod(ellps='WGS84'); T=4.184e9
for m in (170e3,200e3):
    for v in (100,150,200,250):
        E=0.5*m*v*v; print(f"m={m/1e3:.0f} t v={v} m/s E={E:.3e} J = {E/T:.2f} t TNT; /500t threshold = 1/{500/(E/T):.0f}; /50t = 1/{50/(E/T):.0f}")
st={'IS06 (I06H1)':(-12.14645,96.82032),'IS04 (I04H1)':(-34.59761,116.356689),'IS07 (I07H1)':(-19.934851,134.329544),'IS52 (I52H1)':(-7.37781,72.484161)}
pts={'Royer D2 27.856S 93.460E':(-27.856,93.460),'Royer D1 25.404S 93.567E':(-25.404,93.567),'Royer B 35.224S 99.922E':(-35.224,99.922),'Royer C2 26.469S 80.952E':(-26.469,80.952)}
for pn,(la,lo) in pts.items():
    print(pn, {s:round(g.inv(slo,sla,lo,la)[2]/1e3) for s,(sla,slo) in st.items()})
# KLIA to I06 check vs CTBTO 1766 km
print('KLIA->I06', round(g.inv(96.82032,-12.14645,101.550,3.125)[2]/1e3))
EOF