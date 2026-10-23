cd src; mkdir -p mdl; python - <<'EOF'
import json, subprocess
ids={'Isotope temperature':'b50c1760-89a0-4650-86df-742ef3798320','Supplemental files':'6d8cd198-fa57-41f3-82fe-e2955b239b74'}
files=json.load(open('mdl_root.json'))
for n,i in ids.items():
    out=subprocess.run(['curl','-s','--max-time','30',f'https://data.mendeley.com/public-api/datasets/nr4vt4h8gt/files?folder_id={i}&version=4'],capture_output=True,text=True).stdout
    files+= [x for x in json.loads(out) if not x['filename'].endswith('.mp4')]
for x in files:
    u=x['content_details']['download_url']; fn='mdl/'+x['filename'].replace(' ','_')
    r=subprocess.run(['curl','-s','-L','--max-time','60','-o',fn,'-w','%{http_code} %{url_effective}',u],capture_output=True,text=True)
    print(fn, r.stdout[:160])
EOF
ls -la mdl