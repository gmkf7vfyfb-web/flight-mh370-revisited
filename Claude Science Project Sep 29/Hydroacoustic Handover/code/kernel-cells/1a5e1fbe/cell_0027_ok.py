for n in names:
    if n.startswith('27032014') or 'Update22' in n:
        dd=pymupdf.open(stream=z.read(n),filetype='pdf'); t=re.sub(r'\s+',' ',' '.join(p.get_text() for p in dd))
        print('==',n); print(t[:1500])