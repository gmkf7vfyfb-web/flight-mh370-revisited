
MARK="STANDING RULE ON LABELS (Pete, 22 Oct 2026)"
BLOCK_TXT=("> **"+MARK+". Read this before anything else; it overrides any note below.**\n"
"> 1. **No label may be added without Pete's explicit approval.** This covers every label that stops, limits or discounts the use of a source, dataset or file: \"closed access\", \"paywalled\", \"not held\", \"unobtainable\", \"restricted\", \"blocked\", \"unusable\", \"GAP\" set because of access, and any new one of that kind.\n"
"> 2. Pete holds the right to use everything stored in the repo, the Google Drive and the project source folders. A publisher's access status is not a reason to avoid, discount or leave out a source.\n"
"> 3. If a source cannot be fetched: search the artifact store (filenames can be raw DOIs, such as `art%3A10.1007%2F...pdf`), the repo papers folders on both branches, ~/Downloads and the Drive; then write exactly **\"not retrieved — ask Pete\"**, record where you searched in `results/source-access-ledger-2026-10-22.csv`, tell Pete, and carry on. Nothing is left out of an analysis or a note because of it. (This replaces any instruction below to record gaps without asking: a source gap is still recorded, but never as a blocking label and never as a reason to leave the source out.)\n"
"> 4. To use any other label of this kind, ask Pete first and wait for his answer. Caveats Pete has already required (for example \"PREDICTIVE, NOT CALIBRATED\", C1/C2, \"digitised\", chart footnotes, provenance records) stay as written.\n\n")
saved={}
for fn in ['hydro-track-operating-note.md','thread-and-module-operating-guide.md']:
    a=[x for x in host.artifacts(search=fn.replace('.md',''), limit=20)['artifacts'] if x['filename']==fn][0]
    p=host.artifact_path(a['latest_version_id'])
    t=open(p,encoding='utf-8').read()
    if MARK in t: print(fn,'already'); continue
    # insert after first heading if present
    lines=t.split('\n'); idx=next((i for i,l in enumerate(lines[:10]) if l.startswith('# ')),None)
    new = (BLOCK_TXT+t) if idx is None else '\n'.join(lines[:idx+1])+'\n\n'+BLOCK_TXT+'\n'.join(lines[idx+1:])
    open(fn,'w',encoding='utf-8').write(new)
    saved[fn]=a['id']; print(fn, a['id'], len(t),'->',len(new))
print(saved)
