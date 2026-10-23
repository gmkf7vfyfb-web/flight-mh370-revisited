b = host.frames(after='2026-10-21', roots_only=False, max_results=200)
for f in b['frames']:
    print(f['id'][:8], (f.get('parent_frame_id') or '')[:8], f['status'], f.get('agent_name'), f['created_at'], (f.get('name') or '')[:50], '|', (f.get('task_summary') or '')[:80].replace('\n',' '))