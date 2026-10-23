r = host.artifacts(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", limit=300)
import re
pats = ("station","logger","imos","site","coord","geom","noise","threshold","detect","window","air9","blackman","kadri")
hits = [a for a in r["artifacts"] if any(p in a["filename"].lower() for p in pats)]
print(r["count"], "artifacts in hydro frame;", len(hits), "matching")
for a in hits:
    print(a["filename"], "|", a.get("size_bytes"), "|", a["latest_version_id"])
