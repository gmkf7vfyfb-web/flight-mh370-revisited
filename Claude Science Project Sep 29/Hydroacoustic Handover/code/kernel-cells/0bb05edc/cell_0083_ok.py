
rel='results/hydroacoustics-bibliography.csv'
raw=rd(rel); eol='\r\n' if '\r\n' in raw else '\n'
rows_=list(csv.DictReader(io.StringIO(raw.replace('\r',''))))
held_map['Metz2023']=('held','artifact 7e4d336f; exchange sources/','full text (artifact 7e4d336f; read 9 Oct 2026; digitised 22 Oct 2026 by track metz-f35a)')
held_map['Kadri2019']=('held','artifact 133c4968; exchange sources/open-access-fetched-2026-10-22/','full text (fetched 22 Oct 2026; extracted by track metz-f35a)')
out=[]
for r in rows_:
    k=r['key']; rl=r['read_level']
    if k in held_map:
        st,loc,rlo=held_map[k]
        if rlo: rl=rlo
    elif 'repo' in rl.lower() or rl.lower().startswith('full text'):
        st,loc='held','repo / exchange (see read_level)'
    else:
        st,loc='no copy in the project store yet','see source-access-ledger-2026-10-22.csv'
    out.append({'key':k,'authors':r['authors'],'year':r['year'],'title':r['title'],'venue':r['venue'],'doi_or_url':r['doi_or_url'],
                'copy_status':st,'copy_location':loc,'read_level':rl,'sections_used':r['sections_used'],'ground_truth_case':r['ground_truth_case']})
buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=list(out[0].keys()),lineterminator=eol,quoting=csv.QUOTE_MINIMAL); w.writeheader(); w.writerows(out)
wr(rel,buf.getvalue()); print('bibliography:',len(out),collections.Counter(o['copy_status'] for o in out))
# ledger tweaks: Metz / Kadri 2019 already digitised by the module track
for r in LED:
    if r['id']=='L01':
        r['next_step']='Done by track metz-f35a on 22 Oct 2026 (module branch 7dc315f, 6a718bf; note results/hydroacoustics-metz-f35a-anchor.md). Anchor ruling (eta 2.26e-3) is pending with architecture.'
        r['action_taken']='labels replaced in all notes found; copy registered; module track extracted the paper'
    if r['id']=='L03':
        r['next_step']='Extracted by track metz-f35a (it holds no amplitude and no San Juan data).'
with open('source-access-ledger-2026-10-22.csv','w',newline='') as f:
    wcsv=csv.DictWriter(f, fieldnames=list(LED[0].keys())); wcsv.writeheader(); wcsv.writerows(LED)
import shutil
shutil.copy2('source-access-ledger-2026-10-22.csv', os.path.join(P,LEDGER))
print('ledger rows', len(LED))
