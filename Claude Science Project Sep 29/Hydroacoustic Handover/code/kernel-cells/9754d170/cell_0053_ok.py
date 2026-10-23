
r3s=r3[r3.event_id.str.contains('sus')]
pv=r3s.pivot_table(index='event_id',columns='receiver',values='status',aggfunc='first')
pd.set_option('display.width',250); print(pv.to_string())
