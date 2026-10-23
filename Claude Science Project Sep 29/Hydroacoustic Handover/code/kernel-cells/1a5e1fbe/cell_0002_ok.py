c=r['columns']
for row in r['rows']:
    d=dict(zip(c,row)); print(d['id'],'|',d['body']); print('---')