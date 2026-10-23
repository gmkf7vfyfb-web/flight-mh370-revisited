cd cand && sed -n 53,58p candidates-A-F-charts-note-2026-10-22.md && python - <<'E'
f='candidates-A-F-charts-note-2026-10-22.md'; t=open(f).read()
m={'03e3638a-89a7-4466-a9db-3f2d3683c49d':'9e3ce907-f84a-4ef6-9004-9c8a4e158d08','a391dd15-03d9-42b8-9bc7-3508b68b7aa4':'a1889ae4-0f3f-44d2-80f0-44b5d5b1a4da',
'619e2716-f15a-4a2b-a137-ed535b047ea1':'41294bfb-3813-4947-973a-d24283d622cc','cf0a863d-35bc-409a-bbdd-68ef2bac4892':'6a42a841-8fe5-4bb8-92ed-0e4f3adef17a',
'96a6262e-8629-47a3-99d9-26d8baffa714':'4f5cfd0b-156b-46f6-898a-083fcb8bb08a','5aa7e664-e546-4f04-bb1a-15ad1ed5f5c9':'8c696a4e-c941-4040-bc70-f6d7a741007e'}
for a,b in m.items(): assert t.count(a)==1,a; t=t.replace(a,b)
a="PREDICTIVE, NOT CALIBRATED (C1, C2)."; assert t.count(a)==1; t=t.replace(a,"PREDICTIVE, NOT CALIBRATED against real arrivals.")
a="## Per-candidate charts and findings"; assert t.count(a)==1
add=("## Correction 2: there are no coincident signals in the raw records\n\n"
"The raw-record charts (chart 1 of each candidate) plot the 5-40 Hz broadband trace. Most member detections were made in a narrower band. "
"Measured in its own band, each member is only 1.6 to 7.6 dB above the median level of its 5-minute IMOS record (Portland 3275 for E: 11.8 dB). "
"Peaks of that size do not show in a broadband trace. So the members are weak detector outputs whose times agree with one impact point, not signals that can be seen. "
"Their timing agreement is at the chance level (permutation p 0.075 to 0.999).\n\n"
"Check made: the IMOS time base is correct. The Curtin (CMST 2014) event peaks on Perth Canyon 3315 at 01:33:43.4 UTC, 14 dB above the median, against the published time of about 01:33:42.\n\n")
t=t.replace(a,add+a)
open(f,'w').write(t); print('ok', t.count('C1, C2'))
E