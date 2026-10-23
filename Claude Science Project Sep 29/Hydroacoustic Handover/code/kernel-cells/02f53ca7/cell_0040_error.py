import subprocess
for e in ["a274688a-14bb-45aa-be02-f8393e76a406","06bb426b-04c8-45be-a9c0-40f55ab2999b"]:
    p=host.exec_peek(e); print(e[:8], p.get("status"), (p.get("stdout") or "")[-300:])
W="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal"
print(open(W+"/tl.log").read()[-400:]); print(open(W+"/nx2d.log").read()[-400:])