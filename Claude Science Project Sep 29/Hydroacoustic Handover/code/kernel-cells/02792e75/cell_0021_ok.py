for k in ["mr010","mr011","mr012","mr013","mr014","mr015"]:
    ts,u,t=jacc[k]
    # trim nav boilerplate: start at 'Media Release' or date
    s=t.find("Joint Agency Coordination Centre Media")
    print("=====",k,ts); print(re.sub(r"\n+"," | ",t)[:1900])