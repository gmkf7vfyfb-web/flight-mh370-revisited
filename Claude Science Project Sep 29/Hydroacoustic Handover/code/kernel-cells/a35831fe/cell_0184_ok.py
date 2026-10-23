A2=pd.DataFrame(host.artifacts(frame_id='a35831fe-107a-4961-bc9f-e6fd6d255601',limit=500)['artifacts'])[['id','filename','latest_version_id']]
lk=lambda fn: (lambda r: f"[{fn}]({{{{!artifact:{r.latest_version_id.iloc[0]}}}}})")(A2[A2.filename==fn])
full=sorted([f for f in A2.filename if f.endswith('.png')])+['candidates-A-F-charts-note-2026-10-22.md','candidates-A-F-summary.csv',
      'module-singles-feasibility.csv','module-pairs-feasibility.csv','module-triples-feasibility.csv']
txt=["# Withdrawal notice: hydroacoustic candidates A-F (review session of 22 October 2026)","",
"*23 October 2026. Withdrawn at Pete's instruction. Nothing from this session was committed to the repository or sent to Kadri or Royer.*","",
"## Why the work is withdrawn","",reasons,
"## Withdrawn in full (each file now carries a WITHDRAWN banner, header or status column)",""]
txt+=[f"- {lk(f)}" for f in full]
txt+=["","## Withdrawn in part","",
f"- {lk('hydroacoustics-take2-critical-review-2026-10-22.md')}: section 1 item 8, the 'feasible' columns of the section 7 table, and the subsection 'Feasible candidates' with its 'Reading'. A header at the top lists what is kept and how far each kept item was checked.",
f"- {lk('potential-signals-register.csv')}: the 28 rows with verdict FEASIBLE (23) or WEAK (5) are withdrawn. The 45 exclusion rows (not feasible on time or place, known other event, airgun) are kept but were not re-checked after 22 October.","",
"## Not withdrawn","",
f"- {lk('royer-events-crossid-all-sites.csv')}: Royer's published events and their predicted arrivals at each receiver.",
f"- {lk('candA_raw_panel_checks.csv')}: the numerical checks of the candidate A record panels. They support this withdrawal.","",
"## What can be said instead","",
"No impact signal is identifiable in the records held. This is not a claim that no signal exists: detection limits can be stated only after the propagation and coupling model is calibrated on real arrivals (redo list, review section 8, waiting for Pete's ruling)."]
open(NOTICE_FN,'w').write('\n'.join(txt)); print(len(full)); print('\n'.join(txt)[:1500])