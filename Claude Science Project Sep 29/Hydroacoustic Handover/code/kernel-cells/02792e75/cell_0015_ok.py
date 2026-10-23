def ctx(fn, pat, w=900):
    out=[]
    for i,p in enumerate(texts[fn]):
        for m in re.finditer(pat,p):
            out.append(f"--- {fn} pdfpage {i+1} @{m.start()}\n"+p[max(0,m.start()-w):m.end()+w].replace("\r",""))
    return out
o=[]
o+=ctx("atsb2014_search_areas_30jul2015.pdf",r"Haixun",1200)
o+=ctx("amsa_reports_search.pdf",r"Haixun",800)
o+=ctx("icao_ai6_wp30.pdf",r"Haixun",800)
o+=ctx("ulich2018_north25S.pdf",r"Haixun",800)
o+=ctx("possible_debris_aerial_march2014.pdf",r"Haixun",800)
o+=ctx("mot2015_factual_information.pdf",r"37\.5|Echo",500)
o+=ctx("sir2018.pdf",r"37\.5",500)
open("ctx1.txt","w").write("\n".join(o)); print(len(o), sum(len(x) for x in o))