import base64, os
os.makedirs('pod',exist_ok=True)
files={'csiro1.pdf':'1JFy39Xsfjmw7-Px3yf2T-Mxzj3r5lelA','csiro2.pdf':'1S-WCMaRKt0lRlV0Uv3bfVSKZvEd8TjDf','csiro4.pdf':'1P2hMQUu4Pux3rah7sYccn1bboRf83umY','metron.pdf':'1_FpHT5nsRBMo9L2808j281wvBRKzQH9l','iannello.pdf':'1k1spe4FTmfO7bJfbY5we03Wl9pJeWlQn','amsa_reports.pdf':'1w6c_lgv8IKH5YXEDoETST5v2uoW9H8oD','griffin_web.pdf':'1St61jC0TmlxsO6BztYD5vpH_mqNTTDF6','stone2014.pdf':'1RVOgpgVKrAC1wDarH_VRUJQGjIv6Mf1Z'}
for fn,fid in files.items():
    try:
        r=host.mcp(S,"download_file_content",fileId=fid)
        b=None
        if isinstance(r,dict):
            for k in ('content','base64Content','data'):
                if k in r: b=r[k]; break
            if b is None: print(fn,'keys',list(r.keys())[:5]); continue
        else: b=r
        open('pod/'+fn,'wb').write(base64.b64decode(b)); print(fn,os.path.getsize('pod/'+fn))
    except Exception as e: print(fn,'ERR',str(e)[:200])
try:
    r=host.mcp(S,"read_file_content",fileId='1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4')
    open('pod/atsb2017.txt','w').write(r.get('fileContent','')); print('atsb', len(r.get('fileContent','')))
except Exception as e: print('atsb ERR',str(e)[:200])