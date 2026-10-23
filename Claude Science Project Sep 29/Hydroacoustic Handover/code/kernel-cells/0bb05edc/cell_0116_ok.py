
MARK="STANDING RULE ON LABELS (Pete, 22 Oct 2026)"
RULE=("\n\n" + MARK + ". Applies to you in every thread, track and sub-agent you start.\n"
"1. No label may be added without Pete's explicit approval. This covers every label that stops, limits or discounts the use of a source, dataset or file: \"closed access\", \"paywalled\", \"not held\", \"unobtainable\", \"restricted\", \"blocked\", \"unusable\", \"GAP\" set because of access, and any new one of that kind.\n"
"2. Pete holds the right to use everything stored in the repo, the Google Drive and the project source folders. A publisher's access status is not a reason to avoid, discount or leave out a source.\n"
"3. If a source cannot be fetched: search the artifact store (filenames can be raw DOIs, such as art%3A10.1007%2F...pdf), the repo papers folders on both branches, ~/Downloads and the Drive; then write exactly \"not retrieved — ask Pete\", record where you searched in results/source-access-ledger-2026-10-22.csv, tell Pete, and carry on. Nothing is left out of an analysis or a note because of it.\n"
"4. To use any other label of this kind, ask Pete first and wait for his answer. Caveats Pete has already required (for example \"PREDICTIVE, NOT CALIBRATED\", C1/C2, \"digitised\", chart footnotes, provenance records) stay as written.\n"
"The same rule is at the top of ARCHITECTURE.md and of every file in threads/master-prompts/.")
names=['END_OF_FLIGHT_MODULE','HYDROACOUSTIC_MODULE','MH370_ARCHITECTURE','OCEAN_DRIFT_MODULE','OCEAN_SETTLING_MODULE','PAPER_CITATIONS_MODULE','PLEIADES_MODULE','SEARCHED_AREAS_MODULE']
out={}
for n in names:
    a=host.agents.get(n)
    sp=a.get('systemPrompt') or a.get('system_prompt') or ''
    if MARK in sp: out[n]='already'; continue
    host.agents.update(n, {'system_prompt': sp.rstrip()+RULE})
    b=host.agents.get(n); sp2=b.get('systemPrompt') or b.get('system_prompt') or ''
    out[n]= 'updated, readback ok, grew %d -> %d chars' % (len(sp), len(sp2)) if (MARK in sp2 and sp2.startswith(sp[:200])) else 'READBACK PROBLEM'
for k,v in out.items(): print(k,'|',v)
