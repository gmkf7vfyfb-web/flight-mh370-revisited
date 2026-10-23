import json
an=json.load(open(R+'analysis-runj-waypoints.json')); aus=json.load(open(R+'aus160-both.json'))
nsb=an['noise_sd_by_band']; print(type(nsb), list(nsb)[:3] if isinstance(nsb,dict) else nsb[:3])
k0=list(nsb)[0]; print(k0, str(nsb[k0])[:600])
for D in ['D0']:
    print({k:an['cells'][D][k]['transport_noise']['dlnZ_drift'] for k in an['cells'][D] if 'transport_noise' in an['cells'][D][k]})
