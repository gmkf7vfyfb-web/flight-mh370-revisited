NOTICE_FN='hydroacoustics-candidates-withdrawal-2026-10-23.md'
reasons=("1. The candidates come from detector outputs at noise level: 1.6-7.6 dB above the record median in their own bands (Portland 3275 for E: 11.8 dB, energy at 20-40 Hz, not impact-like). No record shows an impact signal at the predicted times.\n"
"2. Four member detections used a 2-5 Hz band. That band is below the IMOS 8 Hz high-pass. Candidate F had only such members.\n"
"3. The members of candidate A do not fit one impact at one coupling (provisional model: H01W +5.7 dB, Portland 3274 -8.3 dB at the F-35A coupling).\n"
"4. Statements that candidates lie on searched sea floor used point estimates only. With bearing, timing and speed errors included, 33-49 % of candidate A's impact probability is on sea floor that is not searched.\n"
"5. The permutation p-values used the invalid 2-5 Hz members and stand-in noise references, so 'chance level' is not established either.\n"
"6. The first map versions used the flight-only Pleiades layer as if it were conditional on the objects (corrected in later versions; the charts are withdrawn for reasons 1-5).\n")
hdr_full=(f"> **WITHDRAWN 23 October 2026. Do not use.** See {NOTICE_FN}.\n>\n> "+reasons.replace('\n','\n> ').rstrip('> ').rstrip()+"\n\n---\n\n")
os.makedirs('withdrawn',exist_ok=True)
# 1 note
note=open(host.artifact_path('9dffe2a1-8d13-4a24-ae2f-29309384d0af')).read()
open('withdrawn/candidates-A-F-charts-note-2026-10-22.md','w').write(hdr_full+note)
# 2 tables: full withdrawal column
stat='WITHDRAWN 2026-10-23: built from noise-level detections, no band check; see '+NOTICE_FN
for fn,vid in [('candidates-A-F-summary.csv','3d369b1b-0a16-41b3-afb6-088e184b4367'),('module-singles-feasibility.csv','6061dbb8-4086-46c6-907c-9f4ac39e074e'),
               ('module-pairs-feasibility.csv','eda089ea-2ebd-41a8-bcdf-a1c467201259'),('module-triples-feasibility.csv','3f2be3fb-d4d2-4c02-b377-fcf6982e3b77')]:
    d=pd.read_csv(host.artifact_path(vid)); d.insert(0,'status',stat); d.to_csv(f'withdrawn/{fn}',index=False); print(fn,d.shape)
# 3 register: per-row status
reg=pd.read_csv(host.artifact_path('e80ab18e-2296-4d13-98b6-7c7ed411df9d'))
wd=reg.verdict.str.startswith('FEASIBLE')|reg.verdict.str.startswith('WEAK')
reg.insert(0,'status',np.where(wd,'WITHDRAWN 2026-10-23: not a candidate (noise-level detections, no band check); see '+NOTICE_FN,
                               'kept: exclusion verdict, not re-checked after 22 Oct'))
reg.to_csv('withdrawn/potential-signals-register.csv',index=False); print('register withdrawn rows',wd.sum(),'kept',(~wd).sum())
# 4 review: partial
rv=open(host.artifact_path('17b39438-4234-4068-a2a0-213cafd12d9c')).read()
hdr_part=(f"> **PARTLY WITHDRAWN 23 October 2026.** See {NOTICE_FN}.\n>\n"
"> Withdrawn: section 1 item 8; the 'feasible' columns of the section 7 table; the whole subsection 'Feasible candidates' with its 'Reading'; the location, time and coupling chart; the three module feasibility tables. Reason: the candidates come from detector outputs at noise level, four members used a 2-5 Hz band below the IMOS 8 Hz high-pass, and the p-values used stand-in noise references.\n>\n"
"> Kept, checked in this review: items 2, 3, 4, 5 and 10 (airgun shots at Diego Garcia, Royer event matches, Scott Reef, unused event tables).\n"
"> Kept, computed once and not independently checked (provisional): items 6 and 7 (coupling anchor, detection power) and section 2.\n"
"> Item 1 must not be read as 'no impact signal exists'. It means only that no signal in these records is a supported impact.\n"
"> Section 8 (redo list) remains a proposal that waits for Pete's ruling.\n\n---\n\n")
a8="8. About 23 candidates are feasible"; assert rv.count(a8)==1; rv2=rv.replace(a8,"8. **[WITHDRAWN 23 Oct 2026]** About 23 candidates are feasible")
a7="### Feasible candidates: where, when, what supports them, what questions them"; assert rv2.count(a7)==1
rv2=rv2.replace(a7,a7+"\n\n> **WITHDRAWN 23 October 2026: this subsection and its 'Reading' paragraph.** See "+NOTICE_FN+".")
open('withdrawn/hydroacoustics-take2-critical-review-2026-10-22.md','w').write(hdr_part+rv2)
print('ok')