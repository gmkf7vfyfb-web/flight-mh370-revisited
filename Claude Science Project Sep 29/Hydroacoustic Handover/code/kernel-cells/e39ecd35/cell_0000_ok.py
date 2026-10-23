
import os, urllib.request, pathlib
pathlib.Path("src").mkdir(exist_ok=True)
targets = {
 "holland_arxiv_v3.pdf": "https://arxiv.org/pdf/1702.02432v3",
 "davey_bayesian_mh370.pdf": "https://library.oapen.org/bitstream/20.500.12657/27976/1/1002023.pdf",
}
for fn,url in targets.items():
    p = os.path.join("src",fn)
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=120) as r, open(p,"wb") as f:
            f.write(r.read())
        print(fn, os.path.getsize(p))
    except Exception as e:
        print(fn, "FAIL", type(e).__name__, str(e)[:200])
