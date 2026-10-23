
MARK="STANDING RULE ON LABELS (Pete, 22 Oct 2026)"
BLOCK=f"""> **{MARK}. Applies to every agent, thread, track and sub-agent.**
> 1. **No label may be added without Pete's explicit approval.** This covers every label that stops, limits or discounts the use of a source, dataset or file: "closed access", "paywalled", "not held", "unobtainable", "restricted", "blocked", "unusable", "GAP" set because of access, and any new one of that kind.
> 2. Pete holds the right to use everything stored in the repo, the Google Drive and the project source folders. A publisher's access status is not a reason to avoid, discount or leave out a source.
> 3. If a source cannot be fetched: search the artifact store (filenames can be raw DOIs, such as `art%3A10.1007%2F...pdf`), the repo papers folders on both branches, ~/Downloads and the Drive; then write exactly **"not retrieved — ask Pete"**, record where you searched in `results/source-access-ledger-2026-10-22.csv`, tell Pete, and carry on. Nothing is left out of an analysis or a note because of it.
> 4. To use any other label of this kind, ask Pete first and wait for his answer. Caveats Pete has already required (for example "PREDICTIVE, NOT CALIBRATED", C1/C2, "digitised", chart footnotes, provenance records) stay as written.

"""
def insert_after_h1(rel):
    t=rd(rel)
    if MARK in t: return 'already'
    lines=t.split('\n'); eol_cr = '\r' if lines and lines[0].endswith('\r') else ''
    idx=None
    for i,l in enumerate(lines[:15]):
        if l.startswith('# '): idx=i; break
    blk=BLOCK.replace('\n', eol_cr+'\n') if eol_cr else BLOCK
    if idx is None: new=blk+t
    else: new='\n'.join(lines[:idx+1])+('\n' if True else '')+('\n' if not lines[idx+1].strip()=='' else '')+blk+'\n'.join(lines[idx+1:])
    wr(rel,new); return 'inserted' if idx is not None else 'prepended'
top_files=['ARCHITECTURE.md','README.md','coordination/README.md','engine/AGENTS.md']+['threads/master-prompts/'+f for f in ['composer.md','end-of-flight.md','filter-audit.md','fuel-audit.md','fuel-model.md','hydroacoustics.md','ocean-drift.md','ocean-transport.md','paper-drafting.md','pleiades.md','searched-areas.md','settling.md']]
res_top={f:insert_after_h1(f) for f in top_files}
print(res_top)
ENTRY=f"""## 2026-10-22 — {MARK}: no label added without approval -> ALL MODULES, ALL TRACKS

Pete's instruction, 22 Oct 2026, after the overnight hydroacoustics run left sources out because of "closed access / not held" labels that were wrong:

1. **No label may be added without Pete's explicit approval.** This covers every label that stops, limits or discounts the use of a source, dataset or file ("closed access", "paywalled", "not held", "unobtainable", "restricted", "blocked", "unusable", "GAP" set because of access, and any new one of that kind).
2. Pete holds the right to use everything stored in the repo, the Google Drive and the project source folders.
3. A source that cannot be fetched is written as **"not retrieved — ask Pete"** after the artifact store (raw-DOI filenames included), the repo papers folders on both branches, ~/Downloads and the Drive have been searched. Record where you searched in `results/source-access-ledger-2026-10-22.csv`, tell Pete, and carry on. Nothing is left out of an analysis or a note because of it.
4. To use any other label of this kind, ask Pete first and wait for his answer. Caveats Pete has already required (C1/C2, "PREDICTIVE, NOT CALIBRATED", "digitised", chart footnotes, provenance records) stay as written.

The same text is at the top of `ARCHITECTURE.md`, `README.md`, `coordination/README.md`, `engine/AGENTS.md` and every file in `threads/master-prompts/`, and in the system prompt of every module profile and in the operating note given to sub-agents. Sessions that are idle will meet it the next time they read their brief or inbox; Pete can paste "read the STANDING RULE ON LABELS at the top of your brief and your inbox" to wake one.
-- OPERON session (for Pete)
"""
inbox=['END_OF_FLIGHT.md','OCEAN_DRIFT.md','OCEAN_SETTLING.md','OCEAN_TRANSPORT.md','PLEIADES.md','SEARCHED_AREAS.md','HYDROACOUSTICS.md','PAPER.md','CORE_STAGES.md','COMPOSER.md','architecture.md']
for f in inbox:
    rel='coordination/'+f; t=rd(rel)
    if MARK in t: print(f,'already'); continue
    if not t.endswith('\n'): t+='\n'
    wr(rel,t+'\n'+ENTRY)
print('inbox entries appended:', len(inbox))
# tidy the earlier ruling entry's rule sentence so it matches the approved phrase
sub('coordination/architecture.md','A source with no copy is "not retrieved — ask Pete"; say who has to supply it.','A source with no copy is written "not retrieved — ask Pete" (see the standing rule on labels below).')
