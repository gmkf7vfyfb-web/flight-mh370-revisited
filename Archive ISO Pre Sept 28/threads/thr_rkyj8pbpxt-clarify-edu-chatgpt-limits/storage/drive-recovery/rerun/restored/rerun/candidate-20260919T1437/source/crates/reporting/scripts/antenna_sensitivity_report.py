"""Report antenna-conditioned probabilities within each saved cruise model."""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
import shlex

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from arc_density_report import (read_run, physical_identity, pool, mix_weights, cdf_difference,
    region_masses, quantiles, area_grid, ranked_area, reference_arc, map_figure, save_figure, digest)
from flight_sensitivity_report import LABELS,COLOURS


def load_group(name,entries):
    baselines=[];conditioned={};sources=[]
    for entry in entries:
        output=Path(entry['output']);summary=json.loads((output/'summary.json').read_text())
        run=read_run(Path(summary['source_run']))
        if run['summary']['posterior_csv_sha256']!=summary['source_posterior_sha256']:
            raise ValueError('Antenna weights refer to a different baseline posterior')
        baselines.append(run);sources.append(summary)
        for case in summary['cases']:
            path=output/case['weights_file']
            if digest(path)!=case['weights_sha256']:raise ValueError('Conditional weights checksum mismatch')
            values=np.loadtxt(path,delimiter=',',skiprows=1,ndmin=2)
            slots=values[:,0].astype(int)
            if not np.array_equal(slots,np.flatnonzero(run['weight']>0)):raise ValueError('Conditional row identities differ')
            if not np.allclose(values[:,1],run['weight'][slots],atol=1e-14,rtol=1e-10):raise ValueError('Baseline weight mismatch')
            weights=np.zeros_like(run['weight']);weights[slots]=values[:,3]
            if abs(weights.sum()-1)>1e-10 or np.any(weights<0):raise ValueError('Conditional weights are invalid')
            updated=dict(run,weight=weights,summary=dict(run['summary'],log_evidence=case['log_evidence']))
            conditioned.setdefault(case['name'],[]).append(updated)
    if any(physical_identity(r)!=physical_identity(baselines[0]) for r in baselines):raise ValueError('Different baseline priors mixed')
    if len(set(r['config']['branching']['seed'] for r in baselines))!=len(baselines):raise ValueError('Duplicate seed')
    baseline=pool(baselines);cases=[]
    for key,runs in conditioned.items():
        if len(runs)!=len(baselines):raise ValueError('A condition is absent from one source run')
        combined=pool(runs);meta=next(c for c in sources[0]['cases'] if c['name']==key)
        per_run=[next(c for c in s['cases'] if c['name']==key) for s in sources]
        case=dict(name=key,antenna=meta['antenna'],pitch_nose_up_deg=meta['pitch_nose_up_deg'],
                  regions=region_masses(*combined),quantiles_05_50_95_deg=quantiles(*combined),
                  cdf_difference_from_matching_baseline=cdf_difference(baseline,combined),
                  pooling_fractions=mix_weights(runs).tolist(),
                  per_run=[dict(seed=r['config']['branching']['seed'],regions=region_masses(r['points'],r['weight']),
                                row_weight_effective_count=m['row_weight_effective_count'],
                                maximum_initial_ancestor_weight=m['maximum_initial_ancestor_weight']) for r,m in zip(runs,per_run)])
        cases.append(dict(summary=case,pooled=combined,runs=runs))
    return dict(name=name,baselines=baselines,baseline=baseline,cases=cases,sources=sources)


def cdf_figure(groups,output):
    fig,axes=plt.subplots(len(groups),1,figsize=(8,3.1*len(groups)),squeeze=False)
    grid=np.linspace(-42,-15,1081)
    def cdf(xy,w):
        order=np.argsort(xy[:,0]);return np.r_[0,np.cumsum(w[order])][np.searchsorted(xy[order,0],grid,side='right')]
    for i,(group,axis) in enumerate(zip(groups,axes[:,0])):
        baseline=cdf(*group['baseline'])
        axis.plot(grid,baseline,color='black',label='Same trajectories · no antenna likelihood',lw=1.2)
        for sd,colour in [(1.72,'#237a9b'),(3.44,'#d18331')]:
            selected=[c for c in group['cases'] if c['summary']['antenna']['observation_sd_db']==sd]
            values=np.array([cdf(*c['pooled']) for c in selected])
            axis.fill_between(grid,values.min(axis=0),values.max(axis=0),color=colour,alpha=.3,
                              label=f'Range of explicit gain/pitch cases · σ={sd:g} dB')
            axis.plot(grid,values.min(axis=0),color=colour,lw=.6);axis.plot(grid,values.max(axis=0),color=colour,lw=.6)
        axis.set(title=LABELS[group['name']],xlim=(-39,-25),ylim=(0,1),ylabel='Cumulative probability')
        axis.grid(alpha=.2);axis.legend(fontsize=7,loc='lower right')
    axes[-1,0].set_xlabel('Latitude at 00:11 (°; negative is south)')
    fig.suptitle('Antenna sensitivity on matching saved flight populations',fontsize=13)
    fig.tight_layout(rect=(0,.05,1,.98))
    fig.text(.5,.01,'Shading is the range across stated calibration/attitude assumptions, not a credible or confidence interval.\n'
             'Each flight model and each antenna condition retains its own normalized probability distribution.',ha='center',fontsize=8)
    return save_figure(fig,output,'antenna-latitude-comparison')


def report(status_paths,output,inline):
    output.mkdir(parents=True,exist_ok=True);families={};states=[]
    for status_path in status_paths:
        status=json.loads(status_path.read_text());states.append(status['status'])
        for entry in status['runs']:
            if entry['status']=='completed':families.setdefault(entry.get('family','baseline'),[]).append(entry)
    # Every comparison uses exactly the same source trajectories on both sides.
    groups=[load_group(k,v) for k,v in families.items() if len(v)>=2]
    if not groups:raise ValueError('No completed matched pair for antenna comparison')
    figures=[cdf_figure(groups,output)];records=[]
    for group in groups:
        folder=output/group['name'];folder.mkdir(exist_ok=True)
        case_records=[]
        for case in group['cases']:
            xe,ye,mass=area_grid(*case['pooled'],5)
            np.savez_compressed(folder/(case['summary']['name']+'.npz'),x_edges_km=xe,y_edges_km=ye,probability=mass,cell_area_km2=25.)
            case['summary']['ranked_airborne_area_5km_cells']=ranked_area(mass,5)
            case_records.append(case['summary'])
        selected=next(c for c in group['cases'] if c['summary']['name']=='departure1-pitch3-sd1p72')
        selected_folder=folder/'no-precompensation-pitch3-sd1p72';selected_folder.mkdir(exist_ok=True)
        xy,w=selected['pooled'];alt=np.array([float(row['altitude_ft']) for r in selected['runs'] for row in r['rows']])
        figures.append(map_figure(xy,w,area_grid(xy,w,5),reference_arc(group['baselines'][0]['config']),selected_folder,
                                  sum(r['summary']['initial_particles'] for r in selected['runs']),len(selected['runs']),
                                  [float(alt[w>0].min()),float(alt[w>0].max())],
                                  condition_label=LABELS[group['name']]+' · antenna: no precompensation, pitch 3°, SD 1.72 dB'))
        records.append(dict(name=group['name'],label=LABELS[group['name']],
                            initial_candidates=sum(r['summary']['initial_particles'] for r in group['baselines']),
                            baseline_regions=region_masses(*group['baseline']),
                            baseline_repeat_cdf_difference=cdf_difference((group['baselines'][0]['points'],group['baselines'][0]['weight']),
                                                                         (group['baselines'][1]['points'],group['baselines'][1]['weight'])),
                            cases=case_records,sources=group['sources']))
    summary=dict(generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='conditional_sensitivity_only',
                 groups=records,upstream_status=states,source_sha256=digest(__file__),
                 observation_assumptions='Five independent Gaussian power errors per case. 1.72 dB and doubled 3.44 dB are explicit calibration sensitivities; common calibration error is not calibrated.',
                 attitude_assumptions='True heading and signed commanded bank from dynamics; fixed body-pitch alternatives 0, 3, 6 degrees. No posterior probability is assigned to those alternatives.',
                 gain_assumptions='Full, half and absent directional-gain precompensation; same unverified first-pass surface and link calibration.',
                 scope='Within the retained trajectory support of the matching source runs under each model; per-model initial candidate counts are recorded.')
    rows='';detail=''
    for group in records:
        mass=[100*c['regions']['between_35S_and_38S'] for c in group['cases']]
        north=[100*c['regions']['north_of_30S'] for c in group['cases']]
        diff=[100*c['cdf_difference_from_matching_baseline'][0] for c in group['cases']]
        rows+=(f'<tr><td>{group["label"]}<br>{group["initial_candidates"]:,} initial candidates</td><td>{100*group["baseline_regions"]["between_35S_and_38S"]:.1f}%</td>'
               f'<td>{min(mass):.1f}–{max(mass):.1f}%</td><td>{min(north):.2f}–{max(north):.2f}%</td><td>{max(diff):.2f} pp</td></tr>')
        detail+=f'<details><summary>All antenna cases: {group["label"]}</summary><div class="scroll"><table><tr><th>Precompensation departure</th><th>Pitch</th><th>Error SD</th><th>35–38°S</th><th>North of 30°S</th><th>Latitude CDF change</th></tr>'
        for c in group['cases']:
            a=c['antenna'];detail+=(f'<tr><td>{a["directional_departure_scale"]:g}</td><td>{c["pitch_nose_up_deg"]:g}°</td><td>{a["observation_sd_db"]:g} dB</td>'
                                  f'<td>{100*c["regions"]["between_35S_and_38S"]:.2f}%</td><td>{100*c["regions"]["north_of_30S"]:.3f}%</td>'
                                  f'<td>{100*c["cdf_difference_from_matching_baseline"][0]:.2f} pp</td></tr>')
        detail+='</table></div></details>'
    def panel(svg):return '<section><button class="zoom" onclick="this.parentElement.classList.toggle(\'enlarged\')">Enlarge / fit plot</button>'+svg+'</section>'
    maps=''.join(f'<h2>{r["label"]}: no gain precompensation, pitch 3°, error SD 1.72 dB</h2><p>This is one explicitly labelled conditional case; other cases are included in the comparison and saved cell probabilities.</p>'+panel(svg) for r,svg in zip(records,figures[1:]))
    body=('<h1>What the conditional antenna observable changes</h1><p>These comparisons apply the five retained signal-power observations to the same saved flight histories. '
          'Each antenna result is compared with its matching baseline. Candidate counts are listed per model; this is not an antenna update of the full million-candidate original baseline.</p>'
          '<p>The gain surface is an unverified first-pass reconstruction. Full, half and no gain precompensation are separate assumptions, as are the body-pitch and error-size alternatives. '
          'Their spread is a sensitivity range, not a probability distribution over antenna models.</p>'
          '<div class="scroll"><table><tr><th>Flight model: turn/Mach/alt caps</th><th>Baseline 35–38°S</th><th>Antenna range 35–38°S</th><th>Antenna range north of 30°S</th><th>Largest latitude CDF change</th></tr>'+rows+'</table></div>'+panel(figures[0])+detail+maps+
          '<details><summary>Conditions and limitations</summary><p>Five normal power errors are treated as independent within each case. The supplied 1.72 dB uncertainty is also doubled to 3.44 dB for sensitivity; '
          'this does not calibrate a shared receiver offset or errors in the reconstructed gain surface. Body pitch is fixed at 0°, 3° or 6° in separate cases, while heading and bank come from each trajectory. '
          'Power times follow the whole-second flight-model contacts by 0.904–0.928 seconds; the calculation uses the retained model states.</p>'
          '<p>Probability weights and SMC normalizer estimates are updated together. Cases are pooled only within the same flight and antenna model, using initial-effort-weighted unnormalized measures. '
          'No new trajectories are generated. Shared ancestry and separate-run differences remain limitations; weight-based effective row counts do not measure the number of independent posterior samples.</p></details>'
          f'<p class="stamp">Generated {summary["generated_utc"]}. Through 00:10:59 UTC; no impact, drift or searched-area evidence is included here.</p>')
    css='body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.55 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:20px}h1{font-size:1.7em}h2{font-size:1.2em}section,details{background:white;margin:20px 0;padding:10px;overflow:auto}svg{display:block;width:100%;height:auto}.zoom{position:sticky;left:0;padding:8px;font:inherit;cursor:pointer}.enlarged svg{width:1150px;max-width:none}.scroll{overflow-x:auto}table{border-collapse:collapse;background:white;width:100%;font-size:13px}td,th{padding:8px;border-bottom:1px solid #ccd9df;text-align:right}td:first-child,th:first-child{text-align:left}.stamp{font-size:12px;color:#617786}'
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 antenna sensitivity</title><style>'+css+'</style><main>'+body+'</main></html>'
    if len(document.encode())>5*1024**2:raise ValueError('Inline report exceeds 5 MiB')
    for p in [output/'index.html']+([inline] if inline else []):
        temporary=p.with_suffix(p.suffix+'.tmp');temporary.write_text(document);temporary.replace(p)
    summary['inline_bytes']=len(document.encode());(output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    command=shlex.join(['python',str(Path(__file__).resolve()),'--statuses',*[str(p) for p in status_paths],'--output',str(output)]+(['--inline-output',str(inline)] if inline else []))
    (output/'README.md').write_text('# Conditional antenna comparisons\n\n```bash\n'+command+'\n```\n\nAll inputs are saved runner outputs. Each named NPZ contains unsmoothed 5 km cell probabilities for one flight/antenna model. The equal-area projection is defined in arc_density_report.py.\n')
    print(json.dumps(dict(models=len(records),conditional_cases=sum(len(r['cases']) for r in records),inline_bytes=summary['inline_bytes'])))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--statuses',type=Path,nargs='+',required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--inline-output',type=Path)
    a=p.parse_args();report(a.statuses,a.output,a.inline_output)
