import os, textwrap
ids = {
 "end-of-flight.md":"6e62b876-a3eb-4618-85c4-0b1205b54747",
 "impact-interface-requirements.md":"353c4df7-18b8-437e-a7da-21539113430a",
 "eof-dynamics-notes.md":"aeb545a0-58c8-4ec8-8cb0-9120f127310f",
 "eof-run-i-oct12-README.md":"005d01d7-0a48-4284-8cf3-474370389b7f",
 "eof-run-i-dive-oct13-README.md":"b62164ea-ccd7-4afa-a97f-35e7df0faed5",
 "COLUMNS.txt":"4a7aa3ce-bf52-40fe-b316-6eb4eee3608c",
 "run.json":"d8fef912-c00e-4389-b036-0fa4fcfc39f0",
}
os.makedirs("audit", exist_ok=True)
for name, vid in ids.items():
    p = host.artifact_path(vid)
    txt = open(p, encoding="utf-8", errors="replace").read()
    open(f"audit/{name}", "w").write(txt)
    print(name, len(txt))
