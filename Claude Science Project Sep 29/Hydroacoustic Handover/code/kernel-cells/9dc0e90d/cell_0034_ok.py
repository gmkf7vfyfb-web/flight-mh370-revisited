import shutil, os
dst = "repo/r/Claude Science Project Sep 29/results/evidence-sweep-2026-10-17"
os.makedirs(dst, exist_ok=True)
vids = {"evidence-register.md":"82247da9-021c-456d-b440-04bd0338763d",
        "research-surface-search-pod.md":"c0bf853d-9cbe-4184-af5e-46bcb69cf11b",
        "research-satellite-imagery-2014.md":"837df6c5-e49b-44a3-8ade-44591f8082ea",
        "research-radar-infrasound-ohasisbio.md":"84cfa187-919b-4706-b85b-910d3ec0fb2b",
        "research-beacons-tpl-simulator-barnacles.md":"ba454452-d2f9-441e-9024-b10652874bc4"}
for fn,v in vids.items():
    shutil.copy(host.artifact_path(v), os.path.join(dst, fn))
# radar geometry table
df.to_csv(os.path.join(dst,"radar-site-ranges-nm.csv"))
print(os.listdir(dst))