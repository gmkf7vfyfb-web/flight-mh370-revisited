
import json,re
for fid in ['7adf9568','02f53ca7','e6299cde','40a42702','1814d527','c1f32191','ab0373ea','43360090']:
    r = host.frames(frame_id=fid, include_tool_results=False, max_results=2)
    inp = r.get('input')
    t = inp if isinstance(inp,str) else json.dumps(inp)
    print('###', fid, '| name:', r.get('name'), '| created', r.get('created_at'), '| parent', (r.get('parent_frame_id') or '')[:8])
    print('   ', re.sub(r'\s+',' ',t)[:420])
