cd /tmp && python - <<'EOF'
import requests,json
names={'WORLDVIEW-2':'35946','GAOFEN-1':'39150','PLEIADES 1A':'38012','PLEIADES 1B':'39019','THEOS':'33396','SPOT 6':'38755','SPOT 5':'27421','COSMO-SKYMED 1':'31598','COSMO-SKYMED 2':'32376','COSMO-SKYMED 3':'33412','COSMO-SKYMED 4':'37216','TERRASAR-X':'31698','WORLDVIEW-1':'32060','GEOEYE 1':'33331','TERRA':'25994','AQUA':'27424','SUOMI NPP':'37849','METEOSAT-7':'24932','ELEKTRO-L 1':'37344','RADARSAT-2':'32382','TANDEM-X':'36605','SENTINEL-1A':'39634'}
for n,c in names.items():
    try:
        r=requests.get('https://celestrak.org/satcat/records.php',params={'CATNR':c,'FORMAT':'JSON'},timeout=30)
        j=r.json()
        print(c, j[0]['OBJECT_NAME'], j[0]['LAUNCH_DATE'], j[0].get('DECAY_DATE'), j[0].get('OPS_STATUS_CODE'))
    except Exception as e: print(c,n,'ERR',str(e)[:100], r.status_code if 'r' in dir() else '')
for q in ['IGS','ALOS','ASNARO']:
    try:
        r=requests.get('https://celestrak.org/satcat/records.php',params={'NAME':q,'FORMAT':'JSON'},timeout=30)
        for x in r.json(): 
            if x['LAUNCH_DATE']<'2014-03-27' and x['OBJECT_TYPE']=='PAY': print(q,x['NORAD_CAT_ID'],x['OBJECT_NAME'],x['LAUNCH_DATE'],x.get('DECAY_DATE'))
    except Exception as e: print(q,'ERR',str(e)[:100])
EOF