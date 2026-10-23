
import subprocess
for aid in ['91a17cd4-8d7a-4ece-b4fe-b5a08c3c8f14','d6e50fab-f436-4b94-9d07-c75f45c1a290']:
    r = host.artifacts(search=aid.split('-')[0])
    p = host.artifact_path(aid)
    out = subprocess.run(['python','-c',f"""
import pypdf;r=pypdf.PdfReader('{p}');print(len(r.pages));print(r.pages[0].extract_text()[:400])"""],capture_output=True,text=True)
    print(aid, p); print(out.stdout[:600], out.stderr[-300:])
