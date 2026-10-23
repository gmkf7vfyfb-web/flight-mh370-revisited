
import urllib.request, os
cands = {
 "atsb_operational_search_2017.pdf": "https://www.atsb.gov.au/media/5773565/operational-search-for-mh370_final_3oct2017.pdf",
}
for fn,u in cands.items():
    try:
        with urllib.request.urlopen(u, timeout=300) as r: b=r.read()
        open("src/"+fn,"wb").write(b); print("OK",fn,len(b))
    except Exception as e:
        print("FAIL",fn,type(e).__name__,str(e)[:200])
