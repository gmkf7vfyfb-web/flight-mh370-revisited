
import re
ht = open("src/holland.txt").read()
pat = re.compile(r"(fpm|ft/min|Hz/s|descent rate|bound|Hypothesis|hypothesis|warm-up|start-up|transient|g\b)", re.I)
# print pages 6-10 where section VI lives
for i,blk in enumerate(ht.split("===PAGE ")[1:]):
    n = blk.split("===")[0].strip()
    if n in {"6","7","8","9"}:
        print(f"\n######## PAGE {n} ########\n")
        print(blk[:200])
print(len(ht))
