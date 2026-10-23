
import urllib.request, os, shutil
urls = {
 "atsb_operational_search_2017.pdf": "https://www.atsb.gov.au/media/5773565/operational-search-for-mh370_final_3oct2017.pdf",
 "atsb_def_underwater_search_areas_2014.pdf": "https://www.atsb.gov.au/sites/default/files/media/5243942/ae-2014-054_mh370_-_definition_of_underwater_search_areas_18aug2014.pdf",
 "atsb_search_area_definition_update_dec2015.pdf": "https://www.atsb.gov.au/sites/default/files/media/5751600/ae2014054_mh370-searchareadefinitionupdate_3dec2015.pdf",
 "atsb_first_principles_review_2016.pdf": "https://www.atsb.gov.au/sites/default/files/media/5772131/ae-2014-054_mh370-firstprinciples-review.pdf",
 "atsb_flight_path_analysis_update_oct2014.pdf": "https://www.atsb.gov.au/sites/default/files/media/5243942/ae-2014-054_mh370_-_flight_path_analysis_update.pdf",
 "atsb_search_debris_exam_update_nov2016.pdf": "https://www.atsb.gov.au/sites/default/files/media/5772068/ae-2014-054_mh370-search-and-debris-examination-update.pdf",
}
for fn,u in urls.items():
    p = "src/"+fn
    if os.path.exists(p) and os.path.getsize(p)>100000:
        print("have", fn); continue
    try:
        with urllib.request.urlopen(u, timeout=900) as r, open(p,"wb") as f:
            shutil.copyfileobj(r, f, 1<<20)
        print("OK", fn, os.path.getsize(p))
    except Exception as e:
        print("FAIL", fn, type(e).__name__, str(e)[:160])
        if os.path.exists(p): os.remove(p)
