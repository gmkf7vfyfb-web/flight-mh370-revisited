for i,p in enumerate(doc):
    t=p.get_text()
    for m in re.finditer(r'(Uncorrected (Visual )?Sweep Widths? for [^\n]*|Weather Correction Factors[^\n]*|Correction Factors?[^\n]*|Search Facility Speed[^\n]*|Fatigue[^\n]*)', t):
        if '....' not in m.group(0): print(i, m.group(0)[:110])