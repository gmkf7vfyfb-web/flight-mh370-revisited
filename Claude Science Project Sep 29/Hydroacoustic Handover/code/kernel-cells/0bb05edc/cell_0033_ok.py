
import re, json
def show(fid, pat, n=12, width=260):
    r = host.frames(frame_id=fid, pattern=pat, include_tool_results=True, max_results=100)
    print("###", fid, r.get('name'), r.get('agent_name'), 'total_msgs', r.get('total_messages'), 'returned', len(r.get('messages',[])))
    k=0
    for m in r.get('messages',[]):
        c = m.get('content')
        txt = c if isinstance(c,str) else json.dumps(c)
        for mm in re.finditer(pat, txt):
            s = max(0, mm.start()-110); e = min(len(txt), mm.end()+width)
            print(' ', m.get('role'), m.get('created_at') or m.get('timestamp'), '|', txt[s:e].replace('\\n',' ')[:width+130])
            k+=1
            break
        if k>=n: break
show('d74bf70e', r"Metz[^\"]{0,90}(unobtainable|closed|in hand|buying|purchas|bought|not held)", n=14)
