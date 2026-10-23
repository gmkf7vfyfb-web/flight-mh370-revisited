cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/43360090-fdd3-4918-a664-de9fef7e80f6/articles/ && python3 - <<'EOF'
import pypdfium2 as p, re
d=p.PdfDocument('10.1007_s00024-020-02445-9.pdf'); t=re.sub(r'\s+',' ','\n'.join(d[i].get_textpage().get_text_range() for i in range(len(d))))
open('nielsen.txt','w').write(t)
seen=set()
for kw in ['ellipse','km²','km2','TNT','yield','energy equivalent','origin time','13:5','error','uncertaint','bearing','backazimuth','dB re']:
    for m in list(re.finditer(re.escape(kw),t))[:3]:
        s=t[max(0,m.start()-180):m.end()+180]
        if s[:60] in seen: continue
        seen.add(s[:60]); print(f'[{kw}]',s)
EOF