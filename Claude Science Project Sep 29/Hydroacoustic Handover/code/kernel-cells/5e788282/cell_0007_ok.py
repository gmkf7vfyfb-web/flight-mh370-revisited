import os
os.chdir("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6")
P="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/8713f33b-92dd-4026-b29d-18c6ec42e04a/v1dc5cd5c_art3A10.10072Fs00024-022-03117-6.pdf"
pg=pdf_pages(P, mode="text")
with open("metz_text.txt","w") as f:
    for p in pg: f.write(f"\n── page {p['page']} ──\n{p['text']}")
print(len(pg), os.path.getsize("metz_text.txt"))