cd src; python - <<'EOF'
import json, subprocess, io
fo={'Dynamic time-warping results':'39b81c94-bfef-4f47-9fe2-67d37a525eee','Isotope temperature':'b50c1760-89a0-4650-86df-742ef3798320','Simulated_Trajectories':'141c5a47-a74d-4482-a5f9-c2d8afa8ed7f','Supplemental files':'6d8cd198-fa57-41f3-82fe-e2955b239b74'}
for n,i in fo.items():
    out=subprocess.run(['curl','-s','--max-time','30',f'https://data.mendeley.com/public-api/datasets/nr4vt4h8gt/files?folder_id={i}&version=4'],capture_output=True,text=True).stdout
    try:
        L=json.loads(out); print('==',n,len(L))
        for x in L[:15]: print('  ',x['filename'], x['content_details'].get('size'))
        if len(L)>15: print('   ... +',len(L)-15)
    except Exception as e: print(n,'ERR',out[:200])
f=json.load(open('mdl_files.json'))
json.dump(f,open('mdl_root.json','w'))
for x in f: print(x['filename'], x['content_details'].get('download_url','')[:120])
EOF