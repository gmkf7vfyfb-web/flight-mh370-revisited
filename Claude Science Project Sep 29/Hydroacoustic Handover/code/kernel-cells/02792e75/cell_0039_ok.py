o=[]
for fn in ["mot2015_factual_information.pdf","sir2018.pdf"]:
    for i,p in enumerate(texts[fn]):
        if re.search(r"(?i)ULB|locator beacon",p) and re.search(r"(?i)expir|battery",p):
            # find printed page number: last short numeric line
            nums=re.findall(r"(?m)^\s*(\d{1,3})\s*$",p)
            o.append(f"=== {fn} pdf {i+1} printed? {nums[-3:]}\n"+re.sub(r"\s+"," ",p)[:2500])
open("ctx_ulb.txt","w").write("\n".join(o)); print(len(o),[x[:70] for x in o])