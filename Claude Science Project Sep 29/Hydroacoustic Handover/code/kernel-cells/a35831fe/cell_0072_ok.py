out={}
for fid in ['0f0b1c26','5e788282','31b10b13','77d06157','1fcb15df','72504aac']:
    d=host.frames(frame_id=fid, include_tool_results=False, max_results=1)
    N=d['total_messages']
    p=host.frames(frame_id=fid, include_tool_results=False, max_results=3, offset=max(0,N-3))
    txt=''
    for mm in p['messages']:
        c=mm['content']
        if isinstance(c,list): txt+='\n'.join(b.get('text','') or json.dumps(b.get('input',''))[:4000] for b in c if isinstance(b,dict))
        else: txt+=str(c)
    out[fid]=(d.get('input') or '')[:300]+'\n-----\n'+txt[-6000:]
json.dump(out,open('child_reports.json','w'))
for k,v in out.items(): print(k, len(v))