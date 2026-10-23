
def rd(rel): return open(os.path.join(P,rel),encoding='utf-8',newline='').read()
def wr(rel,t): open(os.path.join(P,rel),'w',encoding='utf-8',newline='').write(t)
def sub(rel, old, new, count=1, regex=False):
    t=rd(rel)
    n=len(re.findall(old,t)) if regex else t.count(old)
    assert n==count, f'{rel}: expected {count} of {old[:70]!r}, found {n}'
    wr(rel, re.sub(old,new,t) if regex else t.replace(old,new))
sub('results/seabed-search-INDEX.md',"— blocked, not untried: five failed fetches.","— not retrieved — ask Pete: five failed fetches, and the Drive copy (41.7 MB) is over the connector's 10 MB limit; saving it from the Drive into ~/Downloads would settle it.")
sub('results/seabed-search-references.md',"**Treat this as blocked, not as untried** — the next useful move is a copy\nof the report obtained another way, not another fetch.","**Not retrieved — ask Pete:** the next useful move is a copy\nof the report saved from the Drive into ~/Downloads, not another fetch.")
S='results/settling-references.md'
sub(S,"chu2006 (calhoun.nps.edu refuses scripted requests, 403; the journal copy is closed)","chu2006 (calhoun.nps.edu refuses scripted requests, 403)")
sub(S,"andersen2005 is closed-access (JFM) with no open preprint found; it stays cited for form only, without pins.","andersen2005 (JFM): not retrieved — ask Pete (no open preprint found); it stays cited for form only, without pins.")
sub(S,r"Closed access \(Unpaywall and Semantic Scholar: no open copy; the publisher","Not retrieved — ask Pete (Unpaywall and Semantic Scholar: no open copy; the publisher",regex=True)
SS='results/kadri-haixun-conditional-2026-10-18/sources-sightings/sources-sightings-references.md'
sub(SS,"| news stories | not held | METADATA ONLY (search extract) |","| news stories | not retrieved — ask Pete | METADATA ONLY (search extract) |")
sub(SS,"| press | not held (sites not reachable from sandbox; read as search extracts) |","| press | not retrieved — ask Pete (sites not reachable from sandbox; read as search extracts) |")
SR='results/satellite-coverage-2014-03/coincidence/literature/satellite-literature-register.csv'
sub(SR,"these two 2014 editions have not retrieved — ask Pete","these two 2014 editions: not retrieved — ask Pete")
# ledger: neutral publisher-access wording; heading in md
import csv, io
L='results/source-access-ledger-2026-10-22.csv'
t=rd(L); eol='\r\n' if '\r\n' in t else '\n'
rows=list(csv.DictReader(io.StringIO(t.replace('\r\n','\n'))))
for r in rows:
    if r['publisher_access'].lower().startswith('closed'): r['publisher_access']='subscription journal'
buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=list(rows[0].keys()),lineterminator='\n'); w.writeheader(); w.writerows(rows); wr(L,buf.getvalue())
sub('results/source-access-ledger-2026-10-22.md',"## Still without a copy in the project store (no licence block; a PDF has to be supplied)","## Not retrieved — ask Pete (a PDF has to be supplied; this is not a licence block)")
# keep a repo-side copy for later artifact refresh
shutil.copy2(os.path.join(P,L),'source-access-ledger-2026-10-22.csv'); shutil.copy2(os.path.join(P,'results/source-access-ledger-2026-10-22.md'),'source-access-ledger-2026-10-22.md')
print('ok; ledger rows', len(rows), collections.Counter(r['copy_status'] for r in rows).most_common(4))
