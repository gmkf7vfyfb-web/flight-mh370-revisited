"""Freeze a symmetric joint-proposal bank from completed replay artifacts."""
from pathlib import Path
import json, hashlib, math, sys
output=Path(sys.argv[1]);paths=[Path(p) for p in sys.argv[2:]]
config=json.loads((paths[0]/'resolved-config.json').read_text());banks=[{} for _ in config['modes']];sources={}
for run in paths:
    p=run/'particles.json';data=json.loads(p.read_text());sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    for state,w in zip(data['replay_states'],data['log_weights']):
        if w is None or not math.isfinite(w):continue
        coords=tuple(state['tapes'][0]['prefix'][2:4]);k=state['particle']['stratum']
        banks[k][coords]=banks[k].get(coords,0)+math.exp(w)
coords=[[list(k) for k,v in sorted(bank.items(),key=lambda x:(-x[1],x[0]))[:512]] for bank in banks]
output.write_text(json.dumps(dict(schema_version=1,mode_names=config['modes'],coordinates_by_stratum=coords,source_artifacts=sources,selection='Aggregate positive posterior mass by the two initial random coordinates; retain up to512unique pairs per stratum. This is a fixed computational proposal bank, not evidence.'),indent=2)+'\n')
