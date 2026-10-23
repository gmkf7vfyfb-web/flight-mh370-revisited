bm = open(host.artifact_path("b191a581-7ba8-4520-b5b5-6bca2fc47f5c"),encoding="utf-8",errors="replace").read()
import re
i = bm.lower().find("contradict")
print(bm[max(0,i-2500):i+1500])
