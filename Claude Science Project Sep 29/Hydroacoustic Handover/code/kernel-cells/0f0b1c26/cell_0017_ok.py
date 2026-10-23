import json
out={}
for q in ["Kadri 2024 hydroacoustic figures","kadri published figures","Kadri 2017 scientific reports","41598_2024_60529","AF447 hydroacoustic","San Juan hydroacoustic Vergoz","Nielsen San Juan CTBTO","CMST 2014 passive acoustics","kadri2024 pdf"]:
    r=host.artifacts(search=q, limit=12)
    out[q]=[(a['filename'],a['latest_version_id'],a.get('size_bytes'),round(a.get('_score',0),2)) for a in r['artifacts']]
for k,v in out.items():
    print("##",k)
    for x in v: print("  ",x)