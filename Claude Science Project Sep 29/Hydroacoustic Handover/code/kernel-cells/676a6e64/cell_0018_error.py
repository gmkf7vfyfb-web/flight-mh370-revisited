print(st[:600])
import re
m = re.search(r'H01W[^\n]*', st); print(m.group(0))
nums = [float(x) for x in re.findall(r'-?\d+\.\d+', m.group(0))]
lat, lon = [v for v in nums if -90<=v<=90 and v<0][0], [v for v in nums if 100<=v<=130][0]
print('H01W', lat, lon)
for k,(la,lo) in arc.items():
    d=gc(lat,lon,la,lo); print(f"{k}: {d:.0f} km, delay {d/1.48/60:.1f} min")
for a,b in boxes:
    t0=27+a; t1=27+b
    print(f"box {int(t0):02d}:{int((t0%1)*60):02d}-{int(t1):02d}:{int((t1%1)*60):02d} UTC(00:) -> max range for impact >= 00:19:30: {(t1-19.5)*60*1.48:.0f} km")