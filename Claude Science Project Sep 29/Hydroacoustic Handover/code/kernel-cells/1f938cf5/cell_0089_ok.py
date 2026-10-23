
md=md.replace("(TID 40 94-95 %)","(TID 40 on 91-94 % of all rest points)")
md=md.replace("(horizontal speed 65-330 m/s, descent rate 1-310 m/s,","(weighted p05-p95 per stratum: horizontal speed 65-331 m/s, descent rate 1-313 m/s,")
open('out/README.md','w').write(md)
print(md[:1200])
