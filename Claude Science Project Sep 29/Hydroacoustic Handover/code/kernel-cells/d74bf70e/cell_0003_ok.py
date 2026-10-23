p = host.artifact_path("d17aa890-ec9c-41da-bcc9-cab8886af62b")
txt = open(p).read()
print(len(txt))
for i,l in enumerate(txt.splitlines()):
    if l.startswith("#") or l.strip().startswith("- [ ]") or l.lower().startswith("**"):
        print(i, l[:160])
