import re
t = open(host.artifact_path("01fe3f65-9169-4fb0-948b-0fbf6b39dea8")).read()
for m in re.finditer(r"13597|sha256|checksum|b64|repair|superseded|Drive", t, re.I):
    pass
idx = [m.start() for m in re.finditer(r"b64|13597|repair", t, re.I)]
seen=set()
for i in idx:
    s=max(0,i-300); 
    if any(abs(s-x)<400 for x in seen): continue
    seen.add(s); print(repr(t[s:i+500])); print("---")