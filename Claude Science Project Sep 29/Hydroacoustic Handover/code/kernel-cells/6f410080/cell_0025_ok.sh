cd /tmp && python - <<'EOF'
import requests,json
cats=['35946','39150','38012','39019','33396','38755','27421','31598','32376','33412','37216','31698','32060','33331','25994','27424','37849','24932','37344','32382','36605','28937','38038','37813']
rows=[]
for c in cats:
    try:
        r=requests.get('https://celestrak.org/satcat/records.php',params={'CATNR':c,'FORMAT':'JSON'},timeout=30)
        j=r.json()[0]
        print(c, j['OBJECT_NAME'], j['OBJECT_ID'], j['LAUNCH_DATE'], j.get('DECAY_DATE'), j.get('OPS_STATUS_CODE'), j.get('INCLINATION'), j.get('APOGEE'), j.get('PERIGEE'))
        rows.append(j)
    except Exception as e: print(c,'ERR',str(e)[:120])
for q in ['IGS','ALOS','ASNARO','DAICHI']:
    try:
        r=requests.get('https://celestrak.org/satcat/records.php',params={'NAME':q,'FORMAT':'JSON'},timeout=30)
        for x in r.json():
            if x['LAUNCH_DATE']<'2014-03-27' and x['OBJECT_TYPE']=='PAY' and not x.get('DECAY_DATE'): print(q,x['NORAD_CAT_ID'],x['OBJECT_NAME'],x['OBJECT_ID'],x['LAUNCH_DATE'],x.get('OPS_STATUS_CODE'),x.get('INCLINATION'),x.get('PERIGEE'))
    except Exception as e: print(q,'ERR',str(e)[:120])
json.dump(rows,open('/tmp/satcat.json','w'))
EOF