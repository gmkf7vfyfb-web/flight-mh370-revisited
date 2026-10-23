rep = open("eof-audit-2026-10-13.md").read()
print("before:", re.findall(r"^## \d+\..*$", rep, re.M))
rep = rep.replace("## 9. The published-benchmark check, assembled independently",
                  "## 8. The published-benchmark check, assembled independently")
rep = rep.replace("## 10. Two things to decide", "## 9. Two things to decide")
open("eof-audit-2026-10-13.md","w").write(rep)
print("after: ", re.findall(r"^## \d+\..*$", rep, re.M))
nums = [int(re.match(r"## (\d+)\.", h).group(1)) for h in re.findall(r"^## \d+\..*$", rep, re.M)]
assert nums == list(range(1, len(nums)+1)), nums
print("\ncontiguous 1..%d — OK" % len(nums))
# confirm the column count in the artifact was always right
print("'110 columns' in report:", rep.count("110 columns"), "| '113' anywhere:", rep.count("113"))
