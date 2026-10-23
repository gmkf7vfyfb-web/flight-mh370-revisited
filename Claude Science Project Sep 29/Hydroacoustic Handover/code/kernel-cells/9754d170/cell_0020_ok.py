
import os
os.makedirs('audit/lineage',exist_ok=True)
for name,vid in [('H01W','a63765ea-1eb7-4896-a699-66b8677dada0'),('scen','629b013f-496c-43a9-ae86-25218fc16f13'),('air9','1ec473e8-230d-486a-8697-b6a3e61ac2cd')]:
    lin=host.lineage[vid]
    open(f'audit/lineage/{name}.py','w').write(lin['code'] or '')
    print(name,len(lin['code'] or ''),lin['env'].get('environment_name') if lin['env'] else None,[i['filename'] for i in lin['inputs']][:10])
