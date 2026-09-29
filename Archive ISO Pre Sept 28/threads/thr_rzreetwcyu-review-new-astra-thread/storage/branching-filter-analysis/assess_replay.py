"""Report actual full-history motion and density accounting from saved runs."""
from pathlib import Path
import json, sys
import numpy as np

def assess(run):
    data=json.loads((run/'particles.json').read_text())
    traces=data.get('replay_progress')
    if not traces:return None
    stages=[]
    for j in range(len(traces[0])):
        rows=[t[j] for t in traces]
        stages.append(dict(iteration=rows[0]['iteration'],
          latitude_quantiles_deg=np.quantile([r['latitude_deg'] for r in rows],[.05,.5,.95]).tolist(),
          longitude_quantiles_deg=np.quantile([r['longitude_deg'] for r in rows],[.05,.5,.95]).tolist(),
          initial_mode_mass={mode:sum(r['initial_mode']==mode for r in rows)/len(rows) for mode in sorted(set(r['initial_mode'] for r in rows))},
          mean_log_path_density=float(np.mean([r['log_path_density'] for r in rows]))))
    a=np.array([[t[0][k] for k in ['latitude_deg','longitude_deg']] for t in traces])
    z=np.array([[t[-1][k] for k in ['latitude_deg','longitude_deg']] for t in traces])
    changes=np.abs(z-a)
    errors=[r['log_density']-(r['particle']['cumulative_proposal_log_correction']+r['particle']['cumulative_satcom_log_likelihood']+(r['particle']['fuel_log_factor'] or 0)) for r in data['replay_states']]
    result=dict(run=run.name,terminal_chains=len(traces),stages=stages,
       absolute_coordinate_motion_quantiles_deg=np.quantile(changes,[.1,.5,.9],axis=0).tolist(),
       fraction_with_latitude_motion_at_least_point_one_deg=float(np.mean(changes[:,0]>=.1)),
       maximum_density_accounting_error=float(np.max(np.abs(errors))),
       limitation='Movement and within-run stationarity are diagnostics; independent runs and larger effort are still required. Ancestral chains are not independent posterior draws.')
    (run/'replay-assessment.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    for argument in sys.argv[1:]:print(json.dumps(assess(Path(argument)),indent=2))
