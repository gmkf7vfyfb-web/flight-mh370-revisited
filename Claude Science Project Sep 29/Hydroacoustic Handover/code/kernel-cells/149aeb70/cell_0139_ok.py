p = host.artifact_path("e975137c-9237-4688-ae7c-cc6ca38df08c")
t = open(p).read()
print("chars:", len(t))
import re
for m in re.finditer(r"^#{1,3} .*$", t, re.M):
    print(m.group(0))
