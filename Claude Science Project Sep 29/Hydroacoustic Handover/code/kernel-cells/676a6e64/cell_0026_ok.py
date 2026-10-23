a = host.agents.get('HYDROACOUSTIC_MODULE')
sp = a['systemPrompt']; desc = a['description']
new_desc = desc.replace('swept over three decades','swept over at least four decades')
old_lock = "Do not start a full-scale run without saying so first, and queue anything over ~10 minutes or ~4 GB behind `lockf -k /tmp/.mh370-heavy.lock`."
assert old_lock in sp and 'three decades' in desc
new_sp = sp.replace(old_lock, "Do not start a full-scale run without saying so first. The lockf heavy-lock rule was retired on 17 Oct 2026: anything over ~10 minutes or ~4 GB on the Mac needs a compute slot agreed with end of flight (post to coordination/END_OF_FLIGHT.md), or start at 4 threads and expand as cores free.")
new_sp = new_sp.replace("Your authoritative brief is the repo file `Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md`.",
 "Your authoritative brief is the repo file `Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md` (its section \"Refresh v2 — 21 October 2026\" governs where it differs from earlier text), and your current work order is `Claude Science Project Sep 29/threads/work-orders/hydroacoustics-order-2026-10-21.md`.")
assert new_sp != sp
r = host.agents.update('HYDROACOUSTIC_MODULE', {'description': new_desc, 'system_prompt': new_sp})
print({k: r[k] for k in r if k in ('name','enabled','unrestricted')} if isinstance(r, dict) else r)
b = host.agents.get('HYDROACOUSTIC_MODULE'); print(len(b['systemPrompt']), 'four decades' in b['description'], 'Refresh v2' in b['systemPrompt'], b['unrestricted'])
print(host.agents.switch('HYDROACOUSTIC_MODULE'))