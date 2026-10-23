for fn,pp in [("mot2015_factual_information.pdf",[77,78]),("sir2018.pdf",[182,183,410,411])]:
    for i in pp:
        p=re.sub(r"\s+"," ",texts[fn][i-1])
        for m in re.finditer(r"(?i)[^.]*\b(expir|battery|SC26210|Dec(ember)? 2012|June 2014)[^.]*\.",p):
            print(fn,i,"|",m.group(0).strip()[:300])