
import hashlib
LOGH=[]
E='engine/hypotheses/hydroacoustics'
def subh(rel, old, new, count=1):
    t=rd(rel); n=t.count(old)
    assert n==count, f'{rel}: expected {count} of {old[:70]!r}, found {n}'
    wr(rel, t.replace(old,new)); LOGH.append(rel)
subh(f'{E}/prepare/digitise_brown_2026.py',
 "doi 10.1007/s00024-022-03117-6, closed access). The F-35A source\nspectrum therefore has to come from Metz et al., which is NOT held (GAP). What this paper does render, and what is",
 "doi 10.1007/s00024-022-03117-6; Pete holds a copy, artifact 7e4d336f). The F-35A source\nspectrum therefore has to come from Metz et al. (held; digitised later on 22 Oct by track metz-f35a). What this paper does render, and what is")
subh(f'{E}/results-data/digitised/brown-2026/METHOD.json',
 r"doi 10.1007/s00024-022-03117-6, closed access). The F-35A source\nspectrum therefore has to come from Metz et al., which is NOT held (GAP).",
 r"doi 10.1007/s00024-022-03117-6; Pete holds a copy, artifact 7e4d336f). The F-35A source\nspectrum therefore has to come from Metz et al. (held; digitised later on 22 Oct by track metz-f35a).")
json.loads(rd(f'{E}/results-data/digitised/brown-2026/METHOD.json'))  # still valid JSON
subh(f'{E}/prepare/tl_recal_block9.py',"no full text or figures (closed access); route 2 is recorded as gap G4",
     "no full text or figures (the fetch tool cannot reach the purchased copy, held as artifact 7e4d336f); route 2 is recorded as gap G4")
RQ=f'{E}/prepare/kadri_package/v2-2026-10-22/REQUESTS.txt'
subh(RQ,"(Metz, Obana & Fukao 2023; the paper is closed access to us — gap G4)","(Metz, Obana & Fukao 2023; we hold the paper, so only the waveform is requested — gap G4)")
subh(RQ,"(his own 2019 paper is\n   closed to us — gap G5)","(Dall'Osto 2019, JASA, treats this event; we hold no copy — gap G5)")
subh(f'{E}/data/blackman/extraction_method.txt',"The JASA 2004 paper (doi 10.1121/1.1786711) is closed access and could not be fetched. Nothing here is taken from it.",
     "There is no copy of the JASA 2004 paper (doi 10.1121/1.1786711) in the project store; the companion report UCRL-TR-207323 is the source here. Nothing here is taken from the JASA paper.")
subh(f'{E}/data/blackman/receiver_observations_diff_vs_drive.csv',"Drive claim probably from JASA 2004 (closed access, not verified).","Drive claim probably from JASA 2004 (no copy in the project store, not verified).")
# MANIFEST.txt sha for REQUESTS.txt
mf=f'{E}/prepare/kadri_package/v2-2026-10-22/MANIFEST.txt'
m=rd(mf); newb=open(os.path.join(P,RQ),'rb').read(); newh=hashlib.sha256(newb).hexdigest()
mlines=m.split('\n'); hit=[i for i,l in enumerate(mlines) if re.search(r'\bREQUESTS\.txt\b',l)]
print('manifest lines for REQUESTS.txt:', [mlines[i][:140] for i in hit])
