d = host.frames(frame_id='676a6e64', include_tool_results=False, max_results=1)
print(d['total_messages'])
N=d['total_messages']
msgs=[]
off=0
while off<N:
    p=host.frames(frame_id='676a6e64', include_tool_results=False, max_results=500, offset=off)
    msgs+=p['messages']; off+=len(p['messages'])
    if not p['messages']: break
print(len(msgs), msgs[0].keys())
json.dump(msgs, open('thread676.json','w'))