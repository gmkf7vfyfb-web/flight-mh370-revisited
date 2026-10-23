t = host.frames(frame_id='561e720b-' if False else [r['id'] for r in rows if r['id'].startswith('561e720b')][0])
print(type(t), list(t.keys()) if isinstance(t, dict) else len(t))
import json
s = json.dumps(t, default=str)
print(len(s))
open('handoff_review_thread.json','w').write(s)
