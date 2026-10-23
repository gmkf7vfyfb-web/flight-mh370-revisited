r = host.query("SELECT id, text FROM memories WHERE id IN ('mem_5148b3147b50','mem_11121243c1de','mem_dad7288dfba4','mem_8731070e099c')")
for x in r: print(x)
r = host.query("SELECT id, text FROM memories WHERE text LIKE '%infrasound%' OR text LIKE '%Indonesia%' OR text LIKE '%OHASISBIO%' OR text LIKE '%Cocos%'")
for x in r: print(x['id'], x['text'][:600]); print('--')