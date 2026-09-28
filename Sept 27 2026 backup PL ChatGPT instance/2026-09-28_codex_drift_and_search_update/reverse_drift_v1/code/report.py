from pathlib import Path
import json,hashlib,csv,platform
import numpy as np,pandas as pd
B=Path(__file__).resolve().parents[1];R=B/'results'
s=pd.read_csv(R/'summary.csv');c=pd.read_csv(R/'sensitivity_comparisons.csv');v=json.loads((R/'validation.json').read_text());cv=pd.read_csv(R/'seed_convergence.csv')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def table(frame,cols):
    lines=['| '+' | '.join(cols)+' |','|'+'|'.join(['---']*len(cols))+'|']
    for _,r in frame.iterrows():
        cells=[]
        for k in cols:
            val=r[k];cells.append(f'{val:.3f}' if isinstance(val,(float,np.floating)) else str(val))
        lines.append('| '+' | '.join(cells)+' |')
    return '\n'.join(lines)
main=s[(s.model=='equal_models')&~s.scenario.str.startswith('combined_objects')&~s.scenario.str.startswith('F4')]
lines=['# Recovered and extended conditional imagery-origin results','',
'The complete three-family transport bundle was recovered and rerun. Iannello used **21 March 2014**, while the supplied Malaysian briefing slide labels the four points **23 March 2014**. The attribution/date discrepancy remains unresolved; both dates are carried separately. See `PROVENANCE_AND_METHODS.md` for verified sources, exact settings and interpretation.','',
'The 21-to-23 March change shifts the equal-model Possible COSMO-SkyMed Radar mean by **29.4 km for three points** and **30.5 km for four**, with total variation about **0.29**. Adding F4 shifts the mean about **64 km westward** and approximately doubles the 90% region. The expanded grid places **13.0% of the Pléiades mixture mass west of the original -100 NM source boundary**. This is why the expanded Pléiades 90% area is larger than the recovered original value, despite reproducing all overlapping transport scores. Individual grid-cell modes are substantially noisier than means.','',
'Display labels now use **Possible COSMO-SkyMed Radar**. Historical slide wording and existing `french4`/F1-F4 machine identifiers are retained for traceability. See the sensor-nationality and handoff note in the atlas and provenance document. Numerical results are unchanged.', '',
'## Equal-model results on the expanded source support','',
'Coordinates below are signed decimal degrees (negative latitude = south). Areas are discrete highest-density region areas, not confidence in debris identity. These are normalized conditional source distributions.','',
table(main,['scenario','mode_lat','mode_lon','mean_lat','mean_lon','hpd90_km2','hpd95_km2']), '',
'`combined50` means a 50:50 pool of Pléiades and Possible COSMO-SkyMed Radar conditional PDFs. The three transport families have fixed equal weights. The date suffix applies only to the Possible COSMO-SkyMed Radar detections; Pléiades is always 23 March.', '',
'## Date and fourth-object sensitivity','',
table(c[(c.model=='equal_models')&c.kind.isin(['date','fourth_object'])],['first','second','kind','tv','mean_shift_km','mode_shift_km']), '',
'Total variation ranges from 0 (same cell masses) to 1 (disjoint support). A mean shift can be modest even when the PDF changes appreciably or gains another lobe.', '',
'## Pléiades versus Possible COSMO-SkyMed Radar spatial overlap','',
table(c[(c.model=='equal_models')&(c.kind=='sensor_overlap')],['first','second','overlap','mean_shift_km','mode_shift_km']), '',
'Overlap is sum(min(p_i,q_i)) over the common source grid. It describes these two conditional spatial distributions; it is not a Bayes factor, a probability of shared identity, or independent validation.', '',
'## Original-support truncation','',
table(main,['scenario','outside_original_strip_mass','edge_mass']), '',
'`outside_original_strip_mass` counts centers west of -100 NM on the expanded grid. `edge_mass` counts the outer two along/cross bands. The old boundary half-cell is corrected to an interior cell when merging. The new support spans -250 to +100 NM; probability outside it has not been evaluated.', '',
'## Reproduction and Monte Carlo checks','',
f'The original nine Pléiades model/seed score arrays reproduce with maximum absolute error **{v["max_reproduction_absolute_error"]:.3g}**. Every new trajectory returned a valid endpoint. The expanded grid has {v["source_cells"]:,} cells, with 192 trajectories per cell per seed and three seeds for each of six model/date combinations. Total new trajectories: **{v["source_cells"]*192*3*6:,}** (both date windows). The 21 March Pléiades scores are retained as a diagnostic computation but are not used as the Pléiades observation in any delivered PDF.', '',
table(cv.groupby(['model','scenario'],as_index=False)[['tv','mean_shift_km','mode_shift_km']].max().query('model=="equal_models"'),['model','scenario','tv','mean_shift_km','mode_shift_km']), '',
'The table shows the largest pairwise difference among individual seed PDFs, not an uncertainty interval for the three-seed average. Grid modes may be noisier than means and broad regions. This sample count reproduces the prior study; it does not establish fully converged point maxima.', '',
'## Reusable deliverables','',
'- `conditional_origin_atlas.pdf`: numerical overview, observation map, component and mixed PDF maps, date/subset overlays and latitude marginals.\n- `results/summary.csv`: every component/pool, mean/mode, marginal quantiles, HPD areas and edge diagnostics.\n- `results/sensitivity_comparisons.csv`: date, fourth-object, sensor overlap and weighting comparisons.\n- `results/response_sensitivity.csv`: new 5/20 km kernel and separate windage sensitivities.\n- `results/seed_convergence.csv` and `reproduction_checks.csv`: numerical audits.\n- `results/source_grid.csv` plus `conditional_pdfs.npz` or `probability_masses.csv.gz`: portable cell probability masses; divide by cell area for density.\n- `results/relative_likelihoods.csv.gz`: prior-free transport scores for explicit conditional reuse.\n- `runs/`: per-seed source scores, sufficient to rebuild all pools and plots without rerunning transport.\n- `code/`: new rerun, aggregation, plotting and audit code.\n- `recovered/`: unchanged recovered prior code, arrays, results and provenance.\n- `FILE_MANIFEST.csv`: hashes for the complete delivered package.', '',
'The principal limitations are unknown sensor provenance/acquisition UTC, uncalibrated identity and response weights, inherited daily-wind timing and boundary clamping, a finite source prior, and lack of the background false-detection denominator. GLORYS12 includes WAVERYS; differences cannot be attributed solely to current-model choice. No probability that these objects are MH370 debris is assigned.']
(B/'RESULTS.md').write_text('\n'.join(lines))
audit=[]
manifest=json.loads((B/'recovered/data/input-manifest.json').read_text())
for ds in manifest['datasets']:
    p=B/'recovered/data'/ds['binary_file'];actual=digest(p)
    audit.append({'path':str(p.relative_to(B)),'expected_sha256':ds['sha256'],'actual_sha256':actual,'matches':actual==ds['sha256']})
    assert actual==ds['sha256']
(R/'forcing_hash_audit.json').write_text(json.dumps(audit,indent=2))
# Verify the four-point score is the intended arithmetic 3+1 pool for every cell.
maxerr=0.
for path in (B/'runs').glob('*.json'):
    data=pd.DataFrame(json.loads(path.read_text()))
    e=np.max(np.abs(data.likelihood_french4_sigma10_mixture-(.75*data.likelihood_eastern3_sigma10_mixture+.25*data.likelihood_F4_sigma10_mixture)))
    maxerr=max(maxerr,e);assert e<1e-12
v['max_four_point_score_identity_error']=maxerr
(R/'validation.json').write_text(json.dumps(v,indent=2))
provenance={'date':'2026-09-28','archive':'/Users/pete/Downloads/MH370-review-research-03.zip','archive_sha256':digest(Path('/Users/pete/Downloads/MH370-review-research-03.zip')),'numerical_status':'completed; conditional diagnostic, not identity posterior','original_member_prefix':'project/.sources/pleiades-bran2016-forward-inversion/','source_support_cross_nm':[-250,100],'seed_index_outer_offset':5289,'python':platform.python_version(),'validation':v,'observation_time_warning':'Possible COSMO-SkyMed Radar 04:00 UTC is assumed on both dates','mixture_warning':'Fixed equal model weights; primary sensor weights 1/2; no false-detection denominator'}
(B/'RUN_MANIFEST.json').write_text(json.dumps(provenance,indent=2))
files=[]
for p in sorted(B.rglob('*')):
    if not p.is_file() or p.name=='FILE_MANIFEST.csv' or any(x in p.parts for x in ['__pycache__','mpl_cache','qa']):continue
    files.append({'path':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':digest(p)})
with (B/'FILE_MANIFEST.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(files)
print('Report and manifest saved',len(files),'files')
