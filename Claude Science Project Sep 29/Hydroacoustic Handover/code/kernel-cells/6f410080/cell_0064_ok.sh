python - <<'EOF'
import requests
for u in ['https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/35946/EPOCH/2014-03-15--2014-03-17/format/tle',
          'https://celestrak.org/NORAD/elements/gp.php?CATNR=35946&FORMAT=TLE']:
    try:
        r=requests.get(u,timeout=30); print(u[:60],r.status_code,r.text[:300].replace('\n',' | '))
    except Exception as e: print(u[:60],'ERR',str(e)[:150])
EOF