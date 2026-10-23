
pan=pd.read_csv(HB+"results-data/blackman_noise/blackman_noise_panels.csv")
print(pan.groupby(['page','image']).agg(rows=('row','max'),n=('row','size')).to_string())
txt=open("audit/hb/ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.txt").read().split('\n')
for i,l in enumerate(txt):
    if l.startswith('Figure B') or 'Figure B' in l[:12]: print(i, l[:160])
