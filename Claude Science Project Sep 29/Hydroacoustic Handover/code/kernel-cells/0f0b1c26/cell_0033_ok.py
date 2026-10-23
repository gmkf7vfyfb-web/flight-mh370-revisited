r=host.mcp(S,"download_file_content",fileId='1ZxR_3Y6Ryn-OXyRJ0tjOPSjassZn8ioW')
print(type(r)); 
if isinstance(r,dict): print({k:(type(v).__name__, (len(v) if hasattr(v,'__len__') else v)) for k,v in r.items()})
else: print(len(r), str(r)[:300])