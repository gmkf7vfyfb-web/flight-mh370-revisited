
sub('results/hydroacoustics-prior-work-critique.md',"| Not assessable: report not obtained |","| Report held (`royer-2016-LDO-201608.pdf`, artifact e6fa6f46; digitised in block 1); to be assessed in the next update of this critique |")
sub('results/hydroacoustics-literature-review.md',"Metz2023, Prario2023,","Prario2023,")
sub('results/hydroacoustics-literature-review.md',"and most of the theory papers in §4. **No load-bearing","and most of the theory papers in §4. Metz2023 was bought by Pete on 9 Oct 2026 and read in full after this review (artifact 7e4d336f). **No load-bearing")
sub('results/debris-drift-find-episodes.md',"Durgadoo's full text is not open access and was not re-read tonight.","Durgadoo's full text is open access (CC BY 4.0, NORA eprint 523313) and was not re-read tonight.")
RR='results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md'
sub(RR,"- Blackman et al. (2004, JASA) is paywalled. I used the abstract,","- Blackman et al. (2004, JASA): no copy in the project store. I used the abstract,")
sub(RR,"(most open access; JASA 2004 is paywalled)","(most open access; no copy of the JASA 2004 paper in the project store)")
sub(RR,"- **Blackman et al. 2004 JASA:** paywalled (publisher). The companion","- **Blackman et al. 2004 JASA:** no copy in the project store. The companion")
JP='paper/JON-MODEL-PAPERS.md'
sub(JP,"3 identified, **all closed access**. Metadata and publisher abstract only; listed in §3, excluded from the detailed table","3 identified; no copy in the project store (metadata and publisher abstract only); listed in §3, excluded from the detailed table until a copy is supplied")
sub(JP,"All\nthree are closed access; the Cambridge Core landing pages","No copy of the\nthree is in the project store; the Cambridge Core landing pages")
SR='results/satellite-coverage-2014-03/coincidence/literature/satellite-literature-register.csv'
sub(SR,"ATSB site does not answer from sandbox; not on Drive","Later revisions held (artifacts 7203665a and 5af6ca76; Drive 1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw); these two 2014 editions have no copy in the store")
sub(SR,"MH370 - First Principles Review,https://www.atsb.gov.au/,not retrieved,","MH370 - First Principles Review,https://www.atsb.gov.au/,artifact 5b08ea64 (atsb_first_principles_review_dec2016.pdf),")
sub(SR,"Not retrieved; O01 PDF p.4 says the Pleiades re-analysis complements the First Principles Review.","Held (artifact 5b08ea64) but not yet read for this register; O01 PDF p.4 says the Pleiades re-analysis complements the First Principles Review.")
sub(SR,"Not on Drive; ATSB site unreachable","Held as an artifact (5b08ea64); not on the Drive")
MP='threads/master-prompts/hydroacoustics.md'
t=rd(MP); print('master prompt: ask-Metz count', t.count("ask Metz's group for the F-35 paper and waveforms"), '| Kadri 2019 in San Juan list', t.count("Vergoz 2021, Kadri 2019;"))
sub(MP,"ask Metz's group for the F-35 paper and waveforms","ask Metz's group for the H11 waveforms (the paper is held, artifact 7e4d336f)", count=t.count("ask Metz's group for the F-35 paper and waveforms"))
sub(MP,"Vergoz 2021, Kadri 2019;","Vergoz 2021, Dall'Osto 2019;")
# ---------- bibliography CSV: replace blocking column with copy status
rel='results/hydroacoustics-bibliography.csv'
raw=rd(rel); eol='\r\n' if '\r\n' in raw else '\n'
rows_=list(csv.DictReader(io.StringIO(raw.replace('\r',''))))
led={}
for r in json.load(open('handoff/ledger.json')): led[r['source'][:40]]=r
held_map={ # key -> (copy_status, location, read_level override)
 'Metz2023':('held','artifact 7e4d336f; exchange sources/','full text (artifact 7e4d336f; read 9 Oct 2026)'),
 'Royer2016':('held','artifact e6fa6f46; exchange run-j-digitisation/sources/','full text (artifact e6fa6f46; digitised in block 1)'),
 'Kadri2019':('held','artifact 133c4968; exchange sources/open-access-fetched-2026-10-22/','full text (fetched 22 Oct 2026)'),
 'Williams2023':('held','artifact c4f35150; exchange sources/open-access-fetched-2026-10-22/','full text (fetched 22 Oct 2026)'),
 'Nosov2007':('held','artifact 1ca81b26; exchange sources/open-access-fetched-2026-10-22/','full text (fetched 22 Oct 2026)'),
 'ChuFan2024':('held','artifact 95c75a93; exchange sources/open-access-fetched-2026-10-22/','full text (fetched 22 Oct 2026)'),
 'ATSB2016FP':('held','artifact 5b08ea64; Drive 1gHUVNMzjnh0LSD_LqOjzGGMiRuo_nzaq','full text (artifact; not yet re-read for this table)'),
 'ATSB2014DUSA':('held (later revisions)','artifacts 7203665a, 5af6ca76; Drive 1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw','full text of the 2015 revisions (artifacts)'),
 'Renzi2014':('landing page only','Drive 1nHzJ3h-IcsCkTzvTJwYK0V7-A20F-BHE (abstract page, not the paper)',None),
}
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
wr(rel,buf.getvalue())
print('bibliography rewritten:', len(out),'rows;', collections.Counter(o['copy_status'] for o in out))
print('remaining label hits in bibliography:', len(re.findall(r'closed|paywall|not held|unobtainable',buf.getvalue(),re.I)))
