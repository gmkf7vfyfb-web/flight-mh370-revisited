scr = r'''
import struct, sys, collections
B={"ID-sumatra-west":[[95.0,106.2,-6.2,0.0]],"ID-java-south":[[105.1,108.0,-9.0,-6.65],[108.0,111.5,-9.0,-7.3],[111.5,114.7,-9.0,-8.0]],"ID-nusa-tenggara-south":[[114.4,125.5,-11.2,-8.0]],
   "AU-cocos-christmas":[[96.75,97.05,-12.45,-11.75],[105.35,105.85,-10.65,-10.35]]}
def seg(lo,la):
    for k,bs in B.items():
        for b in bs:
            if b[0]<=lo<=b[1] and b[2]<=la<=b[3]: return k
    return None
import os
for m in ("globcurrent","glorys12"):
    f=os.path.expanduser(f"~/mh370/drift/snap/full-{m}.bin"); R=48
    tot=collections.Counter(); cnt=collections.Counter(); first=collections.Counter()
    with open(f,"rb") as fh:
        while True:
            b=fh.read(R*100000)
            if not b: break
            for i in range(0,len(b),R):
                r,e,c,fate=b[i],b[i+1],b[i+2],b[i+3]; bt,blo,bla=struct.unpack_from("<fff",b,i+4)
                tot[(r,c)]+=1
                if bt==bt and bt<845.0:
                    s=seg(blo,bla)
                    if s: cnt[(r,c,s)]+=1
    print(m, dict(tot) if False else len(tot))
    for r in range(4):
        n=sum(tot[(r,c)] for c in range(3))
        print(m, "release", r, "n", n, {s: round(sum(cnt[(r,c,s)] for c in range(3))/n,5) for s in B}, {f"cls{c}": {s: round(cnt[(r,c,s)]/max(tot[(r,c)],1),5) for s in B} for c in range(3)})
'''
import base64
b=base64.b64encode(scr.encode()).decode()
r=c.call_command(f"echo {b} | base64 -d > /tmp/idcount.py && timeout 55 python3 /tmp/idcount.py; rm -f /tmp/idcount.py; head -c 300 ~/mh370/drift/snap/snap-spec.toml", intent='Count Indonesian-coast first beachings in existing drift snapshot runs (stdlib read only)')
print(r.stdout[-4000:], r.stderr[-500:])