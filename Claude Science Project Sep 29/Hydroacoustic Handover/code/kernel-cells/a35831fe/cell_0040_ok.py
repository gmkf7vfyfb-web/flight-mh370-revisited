sh=pd.read_csv(H+'h08s_template/h08s_template_shots.csv'); shots=np.sort(sh.t.values)
print(len(shots), fmt(shots.min()), fmt(shots.max()), np.median(np.diff(shots)))
h8=s[s.rx=='H08S'].copy(); h8['t']=h8.time_utc.map(hms)
h8['dt_shot']=[ (shots-t)[np.argmin(np.abs(shots-t))] for t in h8.t]
print((h8.dt_shot.abs()<=1.5).mean(), (h8.dt_shot.abs()<=2.5).mean())
print(h8[['time_utc','det','band','p','dt_shot']].sort_values('p').head(12).to_string())
# chance: fraction of time within 1.5 s of a shot (time stamps are whole seconds; shot cadence 10 s)
print('chance |dt|<=1.5 :', 3.0/10.0, ' <=2.5:', 5/10)