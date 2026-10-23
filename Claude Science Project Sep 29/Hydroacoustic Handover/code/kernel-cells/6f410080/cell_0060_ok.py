try:
    r=host.archive.search('contrail cloud Meteosat')
    print(str(r)[:3000])
except Exception as e: print('ERR',e)
try:
    q=host.query("SELECT entity, substr(text,1,400) AS t FROM memories WHERE lower(text) LIKE '%contrail%' LIMIT 20")
    print(q)
except Exception as e: print('ERRq',e)