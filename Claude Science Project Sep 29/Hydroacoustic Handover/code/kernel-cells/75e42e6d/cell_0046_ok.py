for q in ["fullText contains 'australis'", "fullText contains 'De Deckker'", "fullText contains 'Mg/Ca' and fullText contains 'barnacle'", "fullText contains 'Appendix G' and fullText contains 'Geoscience Australia' and fullText contains 'organisms'"]:
    try:
        rr = host.mcp(S,"search_files",query=q,pageSize=20,excludeContentSnippets=True)
        print("==",q)
        for f in rr.get('files',[]): print(' ',f['id'],f.get('fileSize'),f['title'])
    except Exception as e: print(q,e)