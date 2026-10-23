for q in ["jacc.gov.au/media/interviews/*","jacc.gov.au/media/transcripts/*","jacc.gov.au/media/releases/2014/april/*.pdf"]:
    try:
        x=cdx(q,200); print(q,len(x)); 
        for y in x[:60]:
            if re.search(r"2014/april|0[4-9]0?4|april",y[0],re.I): print("  ",y)
    except Exception as e: print(q,e)