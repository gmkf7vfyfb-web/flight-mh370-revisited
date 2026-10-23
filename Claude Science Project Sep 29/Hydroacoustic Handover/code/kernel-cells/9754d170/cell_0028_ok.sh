cd audit/lineage; python3 -c "
import json;m=json.load(open('msg_1961.json'))
for c in m['content']:
  if c.get('type')=='tool_use': print(c['input'].get('code') or c['input'].get('command'))
  elif c.get('type')=='text': print(c['text'][:2000])
"