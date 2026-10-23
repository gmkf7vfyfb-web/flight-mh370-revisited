cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/43360090-fdd3-4918-a664-de9fef7e80f6/articles/ && python3 - <<'EOF'
import pypdfium2 as p, re
for f in ['10.1038_s41598-017-14177-3.pdf','10.1038_s41598-018-37626-z.pdf']:
    d=p.PdfDocument(f); t='\n'.join(d[i].get_textpage().get_text_range() for i in range(len(d)))
    t=re.sub(r'\s+',' ',t); open(f+'.txt','w').write(t); print('#####',f,len(d),len(t))
    for kw in ['phase velocity','0.02%','error','km','Event','E1','E2','bearing','01:','00:','Hz','filter','earthquake','meteor','tank','frequency']:
        hits=[m.start() for m in re.finditer(re.escape(kw),t)][:3]
        for h in hits: print(f'[{kw}]', t[max(0,h-160):h+200])
EOF