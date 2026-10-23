for nm,vid in [("eof-a-vs-b-2241-run-d-standin.md","8896215e-b349-4c02-9d4d-7e512c4f4e70"),
               ("eof-impact-tau-method-oct11.md","091e4fbe-f919-47d1-b16e-ad7e49b25dde"),
               ("impact-interface-requirements.md","353c4df7-18b8-437e-a7da-21539113430a")]:
    t = open(host.artifact_path(vid),encoding="utf-8",errors="replace").read()
    open(f"audit/{nm}","w").write(t); print(nm, len(t))
print(open("audit/eof-a-vs-b-2241-run-d-standin.md").read()[:4000])
