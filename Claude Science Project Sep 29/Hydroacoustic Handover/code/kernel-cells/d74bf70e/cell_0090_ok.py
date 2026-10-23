import re, shutil
R = "repo/Claude Science Project Sep 29/results/"
lf = {"hydroacoustics-literature-review.md":"3ec5a245-6b74-4c6b-a77d-b6da79ca294d","hydroacoustics-prior-work-critique.md":"3e54b2a4-3827-413c-bfb6-b4785027eb60",
      "hydroacoustics-bibliography.csv":"c61b643f-3d50-4afb-8e6c-97e6495a530d","hydroacoustics-ground-truth-cases.csv":"235e172d-2f4b-4d5c-a280-b77679a5c87b"}
for fn,v in lf.items():
    t = open(host.artifact_path(v)).read()
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", t)
    fund = len(re.findall(r"funding|grant application|budget", t, re.I))
    print(fn, len(t), "emails:", emails[:3], "funding-words:", fund)
    shutil.copy(host.artifact_path(v), R+fn)
t = open(R+"hydroacoustics-literature-review.md").read()
i = t.find("Implications"); print(t[i:i+5000])