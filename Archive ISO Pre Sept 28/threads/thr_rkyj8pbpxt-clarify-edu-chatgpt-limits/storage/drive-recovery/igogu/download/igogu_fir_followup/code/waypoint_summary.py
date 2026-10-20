"""Summarize saved weighted-resampling proximity with cached arrays."""
from pathlib import Path
import numpy as np,pandas as pd,json,time
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'output'
def summarize():
 start=time.monotonic();cat=pd.read_csv(HERE.parent/'inputs/waypoint_catalog.csv');z=np.load(OUT/'waypoint_resample_measure.npz')
 dist=z['distance_nm'];component=z['component'];counts=z['counts'];N=int(z['draws_per_measure']);weights=counts/N;records=[]
 for j,row in cat.iterrows():
  record=row.to_dict();near=dist[:,j]<999;ix=np.flatnonzero(near);order=ix[np.argsort(dist[ix,j])]
  for m,label in enumerate(['original','R600']):
   ww=weights[:,m]
   for d in [5,10,20]:
    prob=float(np.sum(ww*(dist[:,j]<=d)));record[f'{label}_within_{d}NM']=prob;record[f'{label}_MC_SE_{d}NM']=float(np.sqrt(prob*(1-prob)/N))
    record[f'{label}_boundary_mass_{d}NM']=float(np.sum(ww*(abs(dist[:,j]-d)<=.1)))
   cum=np.cumsum(ww[order]);ii=np.searchsorted(cum,[.025,.5,.975]);qq=[float(dist[order[a],j]) if a<len(order) else 999. for a in ii]
   for nm,v in zip(['q025','median','q975'],qq):record[f'{label}_distance_{nm}_nm']=v
   for rep in [0,1]:
    wr=ww*(component[:,0]==rep);wr/=wr.sum();record[f'{label}_rep{rep}_within_10NM']=float(np.sum(wr*(dist[:,j]<=10)))
  records.append(record)
 df=pd.DataFrame(records).sort_values('R600_within_20NM',ascending=False);df.to_csv(OUT/'waypoint_proximity.csv',index=False)
 summary={'draws_per_measure':N,'unique_evaluated_paths':len(dist),'raw_survivors_represented':1710701,'catalog_points':len(cat),'seeds':[20260919400,20260919401],
 'conditional_MC_SE_worst_case':float(.5/np.sqrt(N)),'method':'IID weighted resampling separately for original and R600 finite measures; multiplicity retained; piecewise local WGS84 metric projection on exact frozen engine paths. Censored beyond100NM. Counts are not independent physical-trajectory ESS.',
 'scope':'IGOGU turn start through fuel exhaustion; inbound conditioned-on waypoints excluded. No terminal extension.',
 'uncertainties':'Distance bands are sensitivity radii, not inferred navigation-error distributions. Model calibration, catalog epoch and original importance convergence remain unresolved.',
 'above_one_percent_10NM':df.loc[df.R600_within_10NM.gt(.01),'name'].tolist(),'summary_seconds':time.monotonic()-start}
 (OUT/'waypoint_audit_summary.json').write_text(json.dumps(summary,indent=2));print(df.head(16)[['name','original_within_5NM','R600_within_5NM','R600_within_10NM','R600_within_20NM','R600_distance_median_nm']].to_string(index=False));print(json.dumps(summary))
if __name__=='__main__':summarize()
