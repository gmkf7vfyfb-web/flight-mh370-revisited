
import csv, io, shutil
def rd(rel): return open(os.path.join(P,rel),encoding='utf-8',newline='').read()
def wr(rel,t): open(os.path.join(P,rel),'w',encoding='utf-8',newline='').write(t)
def sub(rel, old, new, count=1):
    t=rd(rel); n=t.count(old); assert n==count, f'{rel}: expected {count} of {old[:60]!r}, found {n}'; wr(rel,t.replace(old,new))
sub('coordination/architecture.md',
 "**Unchanged, because they are facts and not licence labels:** raw IMS waveforms (H01W, H08S, H08N) are data not retrieved — ask Pete; commercial\narchive logins and API keys are credentials; public documents",
 "**Reworded on Pete's instruction, 22 Oct 2026:** raw IMS waveforms (H01W, H08S, H08N) and the commercial archive logins and API keys now read\n\"not retrieved — ask Pete\" (the \"not held\" and \"blocked\" wording is gone from the notes; Scott Reef 3250 reads \"North West Shelf in the path\").\n**Kept on Pete's instruction:** the \"DO NOT USE: fig10-3-bfo-latitude-pdf.csv (superseded)\" lines and the \"Do not use these maps for a search\" captions.\n**Still true as notes:** public documents")
L='results/source-access-ledger-2026-10-22.csv'
rows=list(csv.DictReader(io.StringIO(rd(L).replace('\r\n','\n'))))
for r in rows:
    if r['id'] in ('D01','D02','D03'):
        r['copy_status']=APPROVED
        r['action_taken']='reworded on Pete\'s instruction, 22 Oct 2026'
buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=list(rows[0].keys()),lineterminator='\n'); w.writeheader(); w.writerows(rows); wr(L,buf.getvalue())
cnt=collections.Counter(r['copy_status'] for r in rows)
M='results/source-access-ledger-2026-10-22.md'; t=rd(M)
start=t.index('| copy status | rows |'); end=t.index('\n\n',start)
tbl='| copy status | rows |\n|---|---|\n'+'\n'.join(f'| {k} | {v} |' for k,v in cnt.most_common())
t=t[:start]+tbl+t[end:]
a=t.index('## Not labels (unchanged)'); b=t.index('## How the Metz label arose')
t=t[:a]+("## Reworded on Pete's instruction (22 Oct 2026)\n\n"
"- Raw IMS waveforms at H01W, H08S and H08N, and the commercial archive logins and API keys (Space-Track, USGS M2M, DLR, Maxar, Planet, SI Imaging, Bhoonidhi, CNES): now \"not retrieved — ask Pete\". IMS access is through the CTBTO vDEC or a national data centre; archive access needs an account or key (Customize > Credentials).\n"
"- Kept on Pete's instruction: the \"DO NOT USE: fig10-3-bfo-latitude-pdf.csv (superseded)\" lines in the coordination inboxes and the \"Do not use these maps for a search\" captions in the composer figure scripts.\n"
"- Not touched: generated products that carry \"not held\" as a category (arrival-window matrix and its README, run J levels table) and the module's own acoustic-path terms (\"blocked path\", \"blockage\"), because changing them means regenerating charts or changing a computed result.\n"
"- Copyrighted PDFs are used internally but not committed to the public repo; the restricted-source ledger (`results/restricted-sources-ledger.md`) is untouched.\n\n")+t[b:]
wr(M,t)
shutil.copy2(os.path.join(P,L),'source-access-ledger-2026-10-22.csv'); shutil.copy2(os.path.join(P,M),'source-access-ledger-2026-10-22.md')
print(cnt.most_common())
# confirm the two kept groups are untouched
d1=sum(len(re.findall(r"^- DO NOT USE: `fig10-3-bfo-latitude-pdf\.csv`",rd(f),re.M)) for f in ['coordination/CORE_STAGES.md','coordination/END_OF_FLIGHT.md','coordination/HYDROACOUSTICS.md','coordination/OCEAN_DRIFT.md','coordination/OCEAN_SETTLING.md','coordination/OCEAN_TRANSPORT.md','coordination/PAPER.md','coordination/PLEIADES.md','coordination/SEARCHED_AREAS.md','coordination/architecture.md'])
d2=sum(len(re.findall(r"Do not use (these maps for a search|them as a result)",open(os.path.join(P,f),encoding='utf-8').read())) for f in ['results/composer-pass0/report.py','results/composer-pass0/seabed_finish.py','results/composer-pass1-run-c/figures_c.py','results/composer-pass1-run-c/seabed_c.py','results/composer-pass2-run-i/figures_pass2.py'])
print('kept: superseded bullets =',d1,'| map captions =',d2)
