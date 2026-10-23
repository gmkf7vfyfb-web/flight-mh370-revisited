
import re
pats = {
 "closed_not_held": r"closed and not held|Metz[^\n]{0,80}(unobtainable|closed access|\(closed\)|closed,)|not held \(GAP\)",
 "in_hand": r"Metz et al\. 2023 is in hand|Metz[^\n]{0,60}in hand|Pete bought it|is purchasing it",
}
for k,p in pats.items():
    r = host.frames(pattern=p, roots_only=False, max_results=100, include_tool_results=False)
    print("=====", k, r.get('total_matches'))
    out=[]
    for m in r['matches']:
        out.append((m.get('created_at'), m['frame_id'][:8], m.get('name'), m.get('agent_name'), (m.get('parent_frame_id') or '')[:8]))
    out.sort(key=lambda x:str(x[0]))
    for o in out: print(o)
