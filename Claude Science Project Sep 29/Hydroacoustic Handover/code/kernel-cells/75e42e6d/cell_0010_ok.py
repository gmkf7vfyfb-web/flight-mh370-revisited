dl('1eXn_nXdxnIL2xDNEJIMJaQRmLc02iId5','SIR_2018_official.pdf')
r = host.mcp(S,"get_file_metadata",fileId='1eXn_nXdxnIL2xDNEJIMJaQRmLc02iId5',excludeContentSnippets=True); print(r.get('title'), r.get('description'))
for q in ["fullText contains 'Underwater Search Areas'", "fullText contains 'simulator' and fullText contains 'Zaharie'", "fullText contains 'Lepas'", "fullText contains 'Al-Qattan'", "fullText contains 'sonobuoy'", "fullText contains 'Haixun'"]:
    try:
        rr = host.mcp(S,"search_files",query=q,pageSize=25,excludeContentSnippets=True)
        print("==",q)
        for f in rr.get('files',[]): print(' ',f['id'],f.get('fileSize'),f['title'])
    except Exception as e: print(q,e)