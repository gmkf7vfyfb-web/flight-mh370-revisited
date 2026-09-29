"""Freeze a proposal from one saved pilot; this is not additional evidence."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np

def make(run, output, centres=256, prior_fraction=.2, mach_half_width=.0075, altitude_radius=2):
    config=json.loads((run/'resolved-config.json').read_text())
    data=json.loads((run/'particles.json').read_text())
    states=data['replay_states']
    if not states or not 1 <= centres <= 512:
        raise ValueError('A retained replay population and 1–512 centres are required')
    weights=np.exp(np.array([x if x is not None else -np.inf for x in data['log_weights']]))
    banks=[]
    for mode in config['modes']:
        ids=np.array([i for i,s in enumerate(states) if s['particle']['flight']['initial_mode']==mode and weights[i]>0])
        if not len(ids):raise ValueError(f'No positive pilot mass for {mode}')
        w=weights[ids];w/=w.sum()
        chosen=ids[np.searchsorted(np.cumsum(w),(np.arange(centres)+.5)/centres).clip(max=len(ids)-1)]
        banks.append([[states[i]['initial_mach'],states[i]['initial_altitude_ft']] for i in chosen])
    bank={'proposal':{'mode_names':config['modes'],'prior_fraction':prior_fraction,
          'mach_half_width':mach_half_width,'altitude_radius_levels':altitude_radius,
          'centres_by_mode':banks,'retain_guidance_until_final':True},
          'sources':{'run':run.name,
              'particles_sha256':hashlib.sha256((run/'particles.json').read_bytes()).hexdigest(),
              'summary_sha256':hashlib.sha256((run/'summary.json').read_bytes()).hexdigest()},
          'selection':'Equal cumulative-mass midpoints within each navigation family; frozen proposal only; exact initial p/q retains the physical prior.'}
    output.write_text(json.dumps(bank,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--centres',type=int,default=256)
    p.add_argument('--prior-fraction',type=float,default=.2)
    p.add_argument('--mach-half-width',type=float,default=.0075)
    p.add_argument('--altitude-radius',type=int,default=2)
    a=p.parse_args();make(a.run,a.output,a.centres,a.prior_fraction,a.mach_half_width,a.altitude_radius)
