"""Compare two saved flight estimates; no independent-particle ESS assumptions."""
from pathlib import Path
import csv, json, sys
import numpy as np

def compare(paths):
    values=[]; provenances=[]; summaries=[]; physical=[]
    for path in paths:
        rows=list(csv.DictReader((path/'posterior.csv').open()))
        w=np.array([float(r['weight']) for r in rows]); w/=w.sum()
        x=np.array([[float(r[k]) for k in ['latitude_deg','longitude_deg']] for r in rows])
        values.append((x,w,rows))
        provenances.append(json.loads((path/'provenance.json').read_text()))
        summaries.append(json.loads((path/'summary.json').read_text()))
        config=json.loads((path/'resolved-config.json').read_text())
        model=json.loads(json.dumps(config['model']))
        model.pop('proposal_guide',None)
        model['dynamics'].pop('marginalize_manoeuvre_rate',None)
        physical.append(dict(inputs=config['inputs'],model=model,modes=config['modes'],
                             mode_probabilities=config['mode_probabilities'],input_hashes=provenances[-1]['inputs']))
    diffs=[]; quantiles=[]; qdiff=[]
    for k in range(2):
        grid=np.sort(np.r_[values[0][0][:,k],values[1][0][:,k]]); fs=[]; qs=[]
        for x,w,_ in values:
            o=np.argsort(x[:,k]); c=np.cumsum(w[o]); sx=x[o,k]
            fs.append(np.r_[0,c][np.searchsorted(sx,grid,'right')])
            qs.append(sx[np.searchsorted(c,[.05,.5,.95]).clip(max=len(x)-1)].tolist())
        diffs.append(float(np.max(abs(fs[0]-fs[1]))));quantiles.append(qs)
        qdiff.append(float(np.max(abs(np.array(qs[0])-qs[1]))))
    mode_diffs={};mode_masses={}
    for field in ['initial_mode','final_mode']:
        labels=sorted(set(r[field] for _,_,rows in values for r in rows))
        masses=[{label:float(w[np.array([r[field]==label for r in rows])].sum()) for label in labels} for _,w,rows in values]
        mode_masses[field]=masses
        mode_diffs[field]=max(abs(masses[0][k]-masses[1][k]) for k in labels)
    hist=[np.histogram2d(x[:,0],x[:,1],bins=[np.arange(-90,90.5001,.5),np.arange(-180,180.5001,.5)],weights=w)[0] for x,w,_ in values]
    hd=abs(hist[0]-hist[1]);maxcell=float(hd.max())
    independent=summaries[0]['seed']!=summaries[1]['seed']
    source_equal=provenances[0]['scientific_source_sha256']==provenances[1]['scientific_source_sha256']
    physical_equal=physical[0]==physical[1]
    result=dict(runs=[p.name for p in paths],independent_seeds=independent,matching_scientific_source=source_equal,
        matching_physical_configuration=physical_equal,
        proposal_inputs=[p.get('proposal_inputs',{}) for p in provenances],
        elapsed_seconds=[s['elapsed_seconds'] for s in summaries],log_evidence=[s['log_evidence'] for s in summaries],
        coordinate_cdf_differences=diffs,coordinate_quantiles_deg=quantiles,coordinate_quantile_differences_deg=qdiff,
        mode_differences=mode_diffs,mode_masses=mode_masses,half_degree_maximum_cell_difference=maxcell,
        half_degree_total_variation=float(.5*hd.sum()),
        provisional_agreement=independent and source_equal and physical_equal and max(diffs)<.05 and max(qdiff)<.5 and max(mode_diffs.values())<.05 and maxcell<.05,
        limitation='A repeated-seed comparison is a numerical diagnostic, not proof of calibrated coverage or complete route exploration.')
    (paths[-1]/'independent-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(compare([Path(p) for p in sys.argv[1:3]]),indent=2))
