def cdx(q,limit=100):
    r=requests.get("http://web.archive.org/cdx/search/cdx",params={"url":q,"output":"txt","fl":"original,timestamp,mimetype","collapse":"urlkey","limit":limit},timeout=60)
    return [l.split() for l in r.text.splitlines() if l.strip()]
tr=cdx("jacc.gov.au/media/transcripts/2014/april/*")
im=cdx("jacc.gov.au/media/releases/2014/april/mr_01*")
for x in tr[:40]: print(x)
print('--'); 
for x in im: print(x)