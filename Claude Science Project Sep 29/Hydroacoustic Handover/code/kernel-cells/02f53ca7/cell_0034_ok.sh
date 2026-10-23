mkdir -p papers; cd papers; curl -sL -o brown2026.pdf "https://arxiv.org/pdf/2604.12723" ; ls -la brown2026.pdf; file brown2026.pdf | cut -c1-100
python -c "
import pypdfium2 as p; d=p.PdfDocument('brown2026.pdf'); print('pages', len(d))
import re
for i in range(len(d)):
    t=d[i].get_textpage().get_text_range()
    for m in re.finditer(r'(?i)(F-35|spectrum|spectrogram|power spectral)', t):
        pass
    hits=[m.group(0) for m in re.finditer(r'(?i)F-35A?', t)]
    if hits: print(i+1, len(hits), [l for l in t.split('\n') if re.search(r'(?i)^Fig(ure)?\.? ?\d+', l.strip())][:3])
"
ls "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/02f53ca7-66d6-4371-9a5a-275163236205/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/digitised" 2>/dev/null; cd ../hydro && git fetch -q origin hypothesis/hydroacoustics 2>/dev/null; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "digitised/" | head