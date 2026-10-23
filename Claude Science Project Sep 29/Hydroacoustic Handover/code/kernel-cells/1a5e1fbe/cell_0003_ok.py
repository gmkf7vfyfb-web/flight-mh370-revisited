for s in ['surface_search','aerial','search_area_2014','pod','sweep','evidence-sweep']:
    try:
        a=host.artifacts(search=s)
        for x in a[:10]: print(s,'|',x)
    except Exception as e: print(s,e)