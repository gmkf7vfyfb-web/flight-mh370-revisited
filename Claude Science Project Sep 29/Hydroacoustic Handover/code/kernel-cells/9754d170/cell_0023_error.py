
lin=host.lineage['27a04503-0ab2-4be3-8c52-02cf57d653c9']
open('audit/lineage/markers.py','w').write(lin['code'] or ''); print(lin['filename'],len(lin['code'] or ''), [i['filename'] for i in lin['inputs']])
