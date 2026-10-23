
import csv, json, io, re
LED=[]
def add(**k):
    base=dict(id='',category='paper',source='',year='',doi_or_url='',publisher_access='',copy_status='',copy_location='',previous_label='',flagged_in='',action_taken='',next_step='')
    base.update(k); LED.append(base)
DRV='Drive file id '
# ---- A. labels that were wrong: copy is held or was fetched today
add(id='L01',source='Metz, Obana & Fukao (2023) Remote hydroacoustic detection of an airplane crash, Pure Appl. Geophys. 180:1343-1351',year='2023',doi_or_url='10.1007/s00024-022-03117-6',publisher_access='subscription (Pete bought it)',copy_status='HELD',
    copy_location='artifact 7e4d336f-aeb4-4369-b709-570cf133c7a4 (since 9 Oct 2026); ~/Downloads/art%3A10.1007%2Fs00024-022-03117-6.pdf; ~/Downloads/mh370-exchange/hydroacoustics/sources/Metz_Obana_Fukao_2023_*.pdf',
    previous_label='closed; not held (GAP); unobtainable; secondary only',flagged_in='hydroacoustics-bibliography.csv; architecture.md; digitised-sources; blackman-validation; kadri-package-v2; overnight summary; digitise_brown_2026.py; tl_recal_block9.py; REQUESTS.txt',
    action_taken='labels replaced; copy registered; gap G4 reworded to a digitisation task',next_step='Digitise Metz Figs 2-3 (H11N/H11S spectrograms) for the F-35A spectral shape (gap G4). Paper prints no H11 pressure values.')
add(id='L02',source="Royer (2016) OHASISBIO report LDO-201608 (Search for the flight MH370 impact site in the Indian Ocean)",year='2016',doi_or_url='not obtained -> held',publisher_access='public report',copy_status='HELD',
    copy_location='artifact e6fa6f46 / 4a46c695 (royer-2016-LDO-201608.pdf); ~/Downloads/mh370-exchange/hydroacoustics/run-j-digitisation/sources/royer-2016-LDO-201608.pdf',
    previous_label='not obtained; not public in a citable repository; secondary only (news, blogs)',flagged_in='hydroacoustics-bibliography.csv; hydroacoustics-prior-work-critique.md',action_taken='labels replaced',next_step='Prior-work critique row 7 to be assessed against the held report.')
add(id='L03',source='Kadri (2019) Effect of sea-bottom elasticity on the propagation of acoustic-gravity waves from impacting objects, Sci. Rep. 9:912',year='2019',doi_or_url='10.1038/s41598-018-37626-z',publisher_access='gold open access',copy_status='FETCHED (22 Oct 2026)',
    copy_location='artifact 133c4968-4c14-4416-ace2-e44f16670a84; ~/Downloads/mh370-exchange/hydroacoustics/sources/open-access-fetched-2026-10-22/',
    previous_label="'Kadri 2019 JASA, closed access (G5)' - a misattribution: the JASA paper is Dall'Osto (2019); this Sci. Rep. paper is open",flagged_in='architecture.md; digitised-sources; kadri-package-v2; overnight summary; REQUESTS.txt; master prompt',
    action_taken='G5 reworded; misattribution corrected in all notes found',next_step='Extract its MH370 signal traces/tables if needed (it revisits the March 2014 signals).')
add(id='L04',source="Dall'Osto (2019) Source triangulation utilizing three-dimensional arrivals: application to the search for the ARA San Juan submarine, JASA 146(4):2104",year='2019',doi_or_url='10.1121/1.5125251',publisher_access='subscription',copy_status='NO COPY IN STORE',
    copy_location='abstract only (fetch 22 Oct 2026: no open location)',previous_label="filed as 'Kadri 2019 (ARA San Juan)', closed access, GAP G5",flagged_in='digitised-sources; architecture.md; kadri-package-v2; REQUESTS.txt; master prompt',
    action_taken='authorship corrected; label replaced',next_step='Pete: supply the PDF if the San Juan 3-D arrival calibration is wanted.')
add(id='L05',source='Williams et al. (2023) On the propagation of acoustic-gravity waves due to a slender rupture in an elastic seabed, JFM 956:A6',year='2023',doi_or_url='10.1017/jfm.2022.1091',publisher_access='hybrid open access',copy_status='FETCHED (22 Oct 2026)',
    copy_location='artifact c4f35150-c9c5-4d7b-bd70-53d98df38c19; exchange open-access-fetched-2026-10-22/',previous_label='gold OA; read level snippet',flagged_in='hydroacoustics-bibliography.csv',action_taken='copy fetched and registered',next_step='')
add(id='L06',source='Nosov et al. (2007) Elastic oscillations of water column in the 2003 Tokachi-oki tsunami source, NHESS 7:243',year='2007',doi_or_url='10.5194/nhess-7-243-2007',publisher_access='gold open access',copy_status='FETCHED (22 Oct 2026)',
    copy_location='artifact 1ca81b26-0a34-4444-87de-b24b84ea2800; exchange open-access-fetched-2026-10-22/',previous_label='read level abstract/secondary',flagged_in='hydroacoustics-bibliography.csv',action_taken='copy fetched and registered',next_step='')
add(id='L07',source='Chu & Fan (2024) Global climatological dataset of undersea acoustic parameters from WOA 2023, Sci. Data 11:1301',year='2024',doi_or_url='10.1038/s41597-024-04074-6',publisher_access='gold open access',copy_status='FETCHED (22 Oct 2026)',
    copy_location='artifact 95c75a93-ed7c-4dd4-a490-4940bfc46d2a; exchange open-access-fetched-2026-10-22/',previous_label='read level secondary (Brown2026)',flagged_in='hydroacoustics-bibliography.csv',action_taken='copy fetched and registered',next_step='')
add(id='L08',source='ATSB (Dec 2016) MH370 - First Principles Review / Search and debris examination update',year='2016',doi_or_url='atsb.gov.au',publisher_access='public report',copy_status='HELD',
    copy_location='artifact 5b08ea64 (atsb_first_principles_review_dec2016.pdf); Drive 1gHUVNMzjnh0LSD_LqOjzGGMiRuo_nzaq (Search and debris examination update, 2 Nov 2016)',
    previous_label='search snippet only; satellite register O13: not retrieved, not on Drive, ATSB site unreachable',flagged_in='hydroacoustics-bibliography.csv; satellite-literature-register.csv (O13)',action_taken='labels replaced',next_step='')
add(id='L09',source='ATSB Definition of Underwater Search Areas (AE-2014-054), later revisions',year='2015',doi_or_url='atsb.gov.au',publisher_access='public report',copy_status='HELD (later revisions only)',
    copy_location='artifacts 7203665a (3 Dec 2015) and 5af6ca76 (30 Jul 2015); Drive 1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw (30 Jul 2015)',previous_label='search snippet only',flagged_in='hydroacoustics-bibliography.csv; satellite-literature-register.csv (O10)',action_taken='labels replaced',next_step='The 26 Jun and 18 Aug 2014 editions have no copy in the store.')
add(id='L10',source='Durgadoo et al. (2021) J. Oper. Oceanogr. 14(1):1-12',year='2021',doi_or_url='10.1080/1755876X.2019.1602102',publisher_access='open access, CC BY 4.0 (NORA eprint 523313)',copy_status='OPEN; copy location not confirmed',
    copy_location='drift thread read it from nora.nerc.ac.uk (memory record); no file in the artifact store under that name',previous_label='not open access; not re-read',flagged_in='results/debris-drift-find-episodes.md:40',action_taken='label replaced',next_step='Drift thread: save the NORA PDF to the artifact store.')
add(id='L11',source='Renzi & Dias (2014) Hydro-acoustic precursors of gravity waves, JFM 754:250-262',year='2014',doi_or_url='10.1017/jfm.2014.398',publisher_access='subscription',copy_status='LANDING PAGE ONLY',
    copy_location='Drive 1nHzJ3h-IcsCkTzvTJwYK0V7-A20F-BHE (Cambridge abstract page printout, not the paper)',previous_label='closed; metadata only',flagged_in='hydroacoustics-bibliography.csv',action_taken='status set to landing page only',next_step='Pete: supply the paper if wanted.')
# ---- B. paywalled, no copy located (flagged rows from the hydroacoustics bibliography not already covered)
done={'Metz2023','Royer2016','Kadri2019','DallOsto2019','Williams2023','Nosov2007','ChuFan2024','ATSB2016FP','ATSB2014DUSA','Renzi2014'}
fetched_noOA={'DuncanDallOsto2023':'fetch 22 Oct 2026: no open location (abstract only; the lay-language paper is held)','Prario2023':'fetch 22 Oct 2026: no open location','Heaney2017':'fetch 22 Oct 2026: no open location','Wang2024':'gold open access, but the fetch tool could not download it (publisher refuses scripted requests)'}
important={'DuncanDallOsto2023','Prario2023','Blackman2004JASA','Heaney2017','Arons1954','Chapman1988','Koper2001','Upton2008','Heaney2009'}
n=12
for r in bib:
    k=r['key']
    if k in done: continue
    oa=r['open_access'].lower(); rl=r['read_level']
    flagged = oa.startswith(('closed','unknown','not public')) or re.search(r'metadata|abstract|snippet|secondary',rl,re.I)
    if not flagged: continue
    held_repo = 'repo' in rl.lower() or rl.lower().startswith('full text')
    if held_repo:
        st='HELD'; loc=rl
    else:
        st='NO COPY IN STORE'; loc=fetched_noOA.get(k,'not searched beyond the 22 Oct matching (Drive, Downloads, artifact store, repo)')
    add(id=f'B{n:02d}',source=f"{r['authors']} ({r['year']}) {r['title']}, {r['venue']}",year=r['year'],doi_or_url=r['doi_or_url'],publisher_access=r['open_access'],copy_status=st,copy_location=loc,
        previous_label=f"open_access={r['open_access']}; read_level={rl}",flagged_in='hydroacoustics-bibliography.csv',
        action_taken='column open_access replaced by copy_status',next_step=('Pete: supply PDF if wanted (cited for values)' if k in important else 'Background reference; supply only if a note starts to rely on it'))
    n+=1
for e in [
 ('X01',"Taylor (1921) Diffusion by continuous movements, Proc. LMS s2-20:196",'1921','10.1112/plms/s2-20.1.196','subscription','NO COPY IN STORE','not located','closed access (Pleiades citation ledger; architecture.md)','coordination/architecture.md:5915; PLEIADES.md','label replaced','Pete: library copy (Pleiades equation location)'),
 ('X02',"LaCasce (2008) Statistics from Lagrangian observations, Prog. Oceanogr. 77:1-29",'2008','10.1016/j.pocean.2008.02.002','subscription','NO COPY IN STORE','not located','closed access','coordination/architecture.md:5915','label replaced','Pete: library copy'),
 ('X03',"Chapman (1988) Source levels of shallow explosive charges, JASA 84:697",'1988','10.1121/1.396849','subscription','NO COPY IN STORE','not located','behind a paywall','coordination/architecture.md:8874','label replaced','Background reference'),
 ('X04',"Blackman et al. (2004) Testing low/very low frequency acoustic sources for basin-wide propagation in the Indian Ocean, JASA 116:2057",'2004','10.1121/1.1786711','subscription','NO COPY IN STORE','companion report UCRL-TR-207323 IS held (artifact 3b556efc; repo inputs/papers/hydroacoustics/)','paywalled; closed access','hydroacoustics-references.md; research-radar-infrasound-ohasisbio.md; engine data/blackman/*','labels replaced','Pete: supply the JASA PDF if the Drive claim on air6 at H08S is to be verified'),
 ('X05',"Gu et al. (2015) / Li et al. (2020) / Shang et al. (2020), three Journal of Navigation particle-filter papers",'2015-2020','10.1017/S0373463314000496; 10.1017/S0373463319000845; 10.1017/S0373463320000077','subscription','NO COPY IN STORE','metadata and abstracts only','all closed access','paper/JON-MODEL-PAPERS.md','labels replaced','Pete: supply the three PDFs if the Introduction is to say anything about their structure'),
 ('X06',"Chu & Fan (2006) Prediction of falling cylinder through air-water-sediment columns, J. Appl. Mech. 73:300",'2006','NPS Calhoun','host refuses scripted requests (403)','NO COPY IN STORE','public author copy at calhoun.nps.edu; browser download needed','refuses scripted requests','results/settling-references.md','recorded','Pete: save the PDF from a browser into ~/Downloads'),
 ('X07',"Anderson (2018) Western Australian Museum reports on wrecks W1/W2",'2018','museum.wa.gov.au','host refuses scripted requests (403)','NO COPY IN STORE','public; browser download needed','refuses scripted requests','results/settling-references.md','recorded','Pete: save the PDFs from a browser'),
 ('X08',"NTSC Indonesia (2008) PK-KKW report DKI574",'2008','knkt.go.id','host unreachable from the sandbox','NO COPY IN STORE','public; browser download needed','refuses scripted requests','results/settling-references.md','recorded','Pete: save the PDF from a browser'),
 ('X09',"DNV-RP-F107 Risk assessment of pipeline protection",'2010/2017','dnv.com / standards.dnv.com','free DNV account needed for the PDF','NO COPY IN STORE','page reachable; PDF behind a free account','needs a free account','results/settling-references.md','recorded','Pete: free DNV download'),
 ('X10',"Hao et al. (2024) Remote Sensing 16(13):2392; (2025) Remote Sensing 17(16):2918",'2024-25','10.3390/rs16132392; 10.3390/rs17162918','gold open access; MDPI refuses scripted requests','NO COPY IN STORE','public; browser download needed','abstract only (satellite register A01, A02)','satellite-literature-register.csv','recorded','Pete: save the PDFs from a browser'),
]:
    add(id=e[0],source=e[1],year=e[2],doi_or_url=e[3],publisher_access=e[4],copy_status=e[5],copy_location=e[6],previous_label=e[7],flagged_in=e[8],action_taken=e[9],next_step=e[10])
# ---- C. data and credentials (facts, not labels; unchanged)
for e in [
 ('D01','data','IMS raw waveforms H01W, H08S, H08N (2014)','2014','CTBTO vDEC / national data centre','DATA NOT HELD','EarthScope serves metadata only; request outstanding','raw not held','several hydroacoustics notes','unchanged: physical data gap, not a licence label','Pete: CTBTO vDEC or national data centre request'),
 ('D02','data','Kadri raw station data; Royer raw 2014 OHASISBIO data','2014','authors','DATA NOT HELD','published traces and tables only (digitised)','not held','kadri package v2; Royer letter','unchanged','Authors; letters drafted, nothing sent without Pete'),
 ('D03','credential','Space-Track historical TLEs; USGS M2M; DLR EOWEB; Maxar; Planet; SI Imaging; Bhoonidhi; CNES SPOT (account or API key needed)','2014','provider accounts','CREDENTIAL NEEDED','none configured','login needed; not held','satellite-coverage-2014-03/archive-catalogue-report.md; research-satellite-imagery-2014.md','unchanged: not a licence label','Pete: add credentials in Customize > Credentials where wanted'),
]:
    add(id=e[0],category=e[1],source=e[2],year=e[3],publisher_access=e[4],copy_status=e[5],copy_location=e[6],previous_label=e[7],flagged_in=e[8],action_taken=e[9],next_step=e[10])
import collections
print(len(LED), collections.Counter(r['copy_status'] for r in LED))
with open('source-access-ledger-2026-10-22.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(LED[0].keys())); w.writeheader(); w.writerows(LED)
json.dump(LED, open('handoff/ledger.json','w'))
