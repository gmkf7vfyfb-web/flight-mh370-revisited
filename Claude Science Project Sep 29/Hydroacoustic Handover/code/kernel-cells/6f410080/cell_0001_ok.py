import os
os.makedirs('handoff',exist_ok=True)
ids={'ga_summary':'1C7sduA8i4AH1uaMPZ3zv2Bqb8qU0e9QI','opsearch':'1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4','amsa':'1w6c_lgv8IKH5YXEDoETST5v2uoW9H8oD','sir':'1eXn_nXdxnIL2xDNEJIMJaQRmLc02iId5','factual':'1HG3CC8jpmV1HmD5YwrhFfR2ZcvijDfzv','marghany':'1CTux2bzw0EB9f7bgfIBnz2XzFzw2aZW1','guardian':'1FG2KX7dVpWvmG6refoHeAO5ob-Zpd1HR','aerial':'1k1spe4FTmfO7bJfbY5we03Wl9pJeWlQn'}
for k,i in ids.items():
    try:
        r=host.mcp(S,"read_file_content",fileId=i)
        t=r.get('fileContent','')
        open(f'handoff/{k}.txt','w').write(t)
        print(k,len(t),r.get('viewUrl'))
    except Exception as e:
        print(k,'ERR',str(e)[:200])