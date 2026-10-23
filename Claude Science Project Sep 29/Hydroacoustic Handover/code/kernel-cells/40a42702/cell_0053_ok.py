
d=json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs/inputs.json'))
print('rows',d['n_rows'],'seeds',d['n_seeds']); print('tau',{k:[round(x,2) for x in v] for k,v in d['tau'].items() if k.endswith('p0.5')})
print('E_j D0/p0.5 (GJ)',[round(x/1e9,2) for x in d['E_j']['D0/p0.5']]); print('ess',{k:round(v) for k,v in d['ess'].items()})
print({r:[round(x) for x in v] for r,v in d['range_km']['D0/p0.5'].items()})
