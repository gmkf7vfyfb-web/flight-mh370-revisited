
r = host.frames(pattern=r"Metz", roots_only=False, max_results=200, include_tool_results=False)
print(r.get('total_matches'), r.get('searched_frames'), r.get('regex_truncated'))
rows=[]
for m in r['matches']:
    rows.append((m.get('created_at'), m['frame_id'][:8], m.get('name'), m.get('agent_name'), m.get('status'), (m.get('parent_frame_id') or '')[:8], m.get('root_frame_id','')[:8] if m.get('root_frame_id') else ''))
rows.sort(key=lambda x: str(x[0]))
for x in rows: print(x)
