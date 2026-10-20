"""Finite-cell oracle and an independent sum over saved production selections."""
import sys,json,csv,math,argparse
from pathlib import Path
import numpy as np
sys.path.insert(0,'/jackbox/home/MH370/crates/reporting/scripts')
import posterior_search_context as report
B=Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--report',type=Path,default=B/'search-comparison')
parser.add_argument('--conditioned',type=Path,default=B/'terminal-conditioned-seed-37091811')
parser.add_argument('--comparison',type=Path)
parser.add_argument('--record',type=Path,default=B/'search-independent-verification.json')
args=parser.parse_args()
original_project=report.project
report.project=lambda latitude,longitude:(longitude,latitude)
p=np.array([[1.,1.],[2.,2.],[11.,1.],[11.,11.],[21.,21.]])
w=np.array([.2,.3,.25,.25,0.])
plan,mask=report.ranked_cells(p,w,10.,200.)
assert plan['selected_area_km2']==200. and plan['captured_probability']==.75
assert plan['tiles']==[[0,0,.5],[0,1,.25]]
assert math.isclose(report.evaluate_tiles(p,np.array([.05,.05,.2,.7,0.]),plan['tiles'],10.),.3,abs_tol=1e-15)
large,_=report.ranked_cells(p,w,10.,1000.)
assert large['selected_area_km2']==300. and large['captured_probability']==1.
geometry={'type':'Polygon','coordinates':[[[0,0],[4,0],[4,4],[0,4],[0,0]],[[1,1],[3,1],[3,3],[1,3],[1,1]]]}
assert report.polygon_membership(np.array([[.5,.5],[2.,2.],[5.,5.]]),geometry).tolist()==[True,False,False]
report.project=original_project
s=json.loads((args.report/'summary.json').read_text())
case=next(c for c in s['cases'] if c['terminal_family']=='openap26-positive-lift-3-targets' and c['contact_case']==report.DEFAULT_CASE and c['evidence_model']=='flight-fuel-final-contacts')
plan=next(p for p in case['plans'] if p['cell_size_km']==25.)
selected={(int(r[0]),int(r[1])) for r in plan['tiles']}
checks=[]
sources=[(args.conditioned,'captured_probability')]
if args.comparison:sources.append((args.comparison,'captured_in_independent_numerical_run'))
for directory,key in sources:
 summary=json.loads((directory/'summary.json').read_text())
 family=next(f for f in summary['families'] if f['name']==case['terminal_family'])
 c=next(c for c in family['cases'] if c['name']==case['contact_case'])
 path=directory/c['weights_file']
 rows=[r for r in csv.DictReader(path.open()) if r['impact_latitude_deg'] and float(r['conditional_weight'])>0]
 total=math.fsum(float(r['conditional_weight']) for r in rows);captured=[]
 for r in rows:
  x,y=original_project(np.array([float(r['impact_latitude_deg'])]),np.array([float(r['impact_longitude_deg'])]))
  if (math.floor(x[0]/25),math.floor(y[0]/25)) in selected:captured.append(float(r['conditional_weight']))
 actual=math.fsum(captured)/total
 assert abs(actual-plan[key])<2e-13
 checks.append({'source':str(directory),'reported':plan[key],'independent_sum':actual,'rows':len(rows)})
args.record.write_text(json.dumps({'finite_cell_reference':'0.75 design capture, 0.30 independent capture; zero-mass cells not charged; polygon hole excluded','production_checks':checks},indent=2)+'\n')
print(checks)
