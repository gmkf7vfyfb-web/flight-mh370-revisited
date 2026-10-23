scr2 = scr.replace('print(m, dict(tot) if False else len(tot))','').replace('print(m, "release", r, "n", n, {s: round(sum(cnt[(r,c,s)] for c in range(3))/n,5) for s in B}, {f"cls{c}": {s: round(cnt[(r,c,s)]/max(tot[(r,c)],1),5) for s in B} for c in range(3)})',
  'print(m, r, n, " ".join(f"{s}={sum(cnt[(r,c,s)] for c in range(3))}" for s in B))')
b=base64.b64encode(scr2.encode()).decode()
r=c.call_command(f"echo {b} | base64 -d > /tmp/idcount.py && timeout 55 python3 /tmp/idcount.py; rm -f /tmp/idcount.py", intent='Count Indonesian-coast first beachings in existing drift snapshot runs (stdlib read only)')
print(r.stdout)
open('out/indonesia-proxy-raw.txt','w').write(r.stdout)