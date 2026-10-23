cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/43360090-fdd3-4918-a664-de9fef7e80f6/articles/ 2>/dev/null && python3 - <<'EOF'
import pypdfium2 as p, re
d=p.PdfDocument('10.1007_s00024-020-02625-7.pdf'); t='\n'.join(d[i].get_textpage().get_text_range() for i in range(len(d)))
open('vergoz.txt','w').write(t); print(len(d), len(t))
for kw in ['km from','ellipse','TNT','kg','energy','yield','13:5','H10N','H04S','dB','origin time','wreck','907','Rio Grande','celerity','1.48']:
    for m in list(re.finditer(re.escape(kw),t))[:4]:
        s=t[max(0,m.start()-200):m.end()+200].replace('\n',' ')
        print(f'[{kw}]',s); 
    print('---')
EOF