flags={'00:52:03':('Inside Royer event A pick bar 00:51:56.8-00:52:04.5 on Royer Fig. 4 (icequake 57.30 S 88.97 E, origin 00:16:29); Royer event 2 (uncertain) also reaches H01W within 4 s','1.1x F-35A at the 99th-percentile energy (module single 00:52:04, digitised trace)'),
       '00:51:50':('Royer event A / event 2 H01W table picks 00:51:38.6-00:51:43.0, +8 s; figure marks 14-16 s later','level not measured'),
       '00:54:30':('Royer appendix arrow at 00:54:24.1 = Royer event 5 (uncertain, 49.76 S 133.11 E, origin 00:28:51)','0.9x F-35A at the 99th-percentile energy (module single 00:54:29, digitised trace)')}
for d in reg:
    if d['id'].startswith('K-') and d['times'] in flags:
        d['known_event'],d['energy_test']=flags[d['times']]
R=pd.DataFrame(reg); R['verdict']=R.apply(verdict,axis=1)
print(R.groupby('group').verdict.value_counts().to_string())
print(R[R.verdict.str.startswith('FEASIBLE')][['id','receivers','times','implied_lat','implied_lon','implied_impact','prior_mass_1deg','energy_test']].to_string())