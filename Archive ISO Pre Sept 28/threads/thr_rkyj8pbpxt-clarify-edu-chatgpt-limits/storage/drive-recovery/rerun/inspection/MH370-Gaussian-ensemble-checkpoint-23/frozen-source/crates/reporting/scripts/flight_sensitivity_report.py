"""Compare explicitly different cruise priors without pooling across models."""
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

from arc_density_report import (read_run, physical_identity, pool, mix_weights, region_masses,
    quantiles, cdf_difference, area_grid, ranked_area, reference_arc, map_figure, save_figure, digest)

LABELS={'baseline':'4 / 2 / 2 · vertical BFO off',
        'turns4-mach2-altitude2-vertical-bfo':'4 / 2 / 2 · vertical BFO on',
        'turns4-mach4-altitude4-vertical-bfo':'4 / 4 / 4 · vertical BFO on',
        'turns8-mach4-altitude4-vertical-bfo':'8 / 4 / 4 · vertical BFO on',
        'turns16-mach8-altitude8-vertical-bfo':'16 / 8 / 8 · vertical BFO on'}
COLOURS=['#647a86','#20749c','#d47725','#23836a','#954478']


def cdf_plot(groups,output):
    fig,axes=plt.subplots(2,1,figsize=(8,8))
    for i,group in enumerate(groups):
        for axis,col in zip(axes,[0,1]):
            for run in group['runs']:
                order=np.argsort(run['points'][:,col]);axis.plot(run['points'][order,col],np.cumsum(run['weight'][order]),
                                                               color=COLOURS[i],alpha=.2,lw=.8)
            points,weights=group['pooled'];order=np.argsort(points[:,col])
            axis.plot(points[order,col],np.cumsum(weights[order]),color=COLOURS[i],lw=1.7,
                      label=f'{LABELS[group["name"]]} ({len(group["runs"])} runs)')
    for axis,label in zip(axes,['Latitude at 00:11 (°; negative is south)','Longitude at 00:11 (°E)']):
        axis.set(xlabel=label,ylabel='Cumulative probability',ylim=(0,1));axis.grid(alpha=.2);axis.legend(fontsize=8)
    fig.suptitle('Sensitivity to vertical BFO and allowed manoeuvre counts',fontsize=13)
    fig.tight_layout(rect=(0,.07,1,.95))
    fig.text(.5,.018,'Caps are turn / Mach / altitude starts after 18:25:34. Bold: within-model pool. Faint: separate runs.\n'
             'Each model has its own prior and estimate. Matched seeds help comparison; cross-model curves are not independent.',ha='center',fontsize=8)
    return save_figure(fig,output,'model-cdf-comparison')


def region_plot(groups,output):
    fig,axes=plt.subplots(1,2,figsize=(9,5.5))
    for axis,key,title in zip(axes,['between_35S_and_38S','north_of_30S'],['Between 35°S and 38°S','North of 30°S']):
        for i,group in enumerate(groups):
            values=[100*region_masses(r['points'],r['weight'])[key] for r in group['runs']]
            axis.plot([min(values),max(values)],[i,i],color=COLOURS[i],lw=2)
            axis.scatter(values,[i]*len(values),color=COLOURS[i],s=25,marker='|',zorder=3)
            axis.scatter(100*group['summary']['regions'][key],i,color=COLOURS[i],s=44,zorder=4)
        axis.set(yticks=range(len(groups)),yticklabels=[LABELS[g['name']] for g in groups],xlabel='Probability (%)',title=title)
        axis.invert_yaxis();axis.grid(axis='x',alpha=.2)
    axes[1].set_yticklabels([])
    fig.suptitle('Model changes compared with variation between repeats',fontsize=13)
    fig.tight_layout(rect=(0,.1,1,.95))
    fig.text(.5,.018,'Dots: within-model pooled estimates. Line ends: minimum and maximum separate-run estimates.\n'
             'Two-run ranges are descriptive variation, not confidence intervals.',ha='center',fontsize=8)
    return save_figure(fig,output,'model-region-comparison')


def summarize(name,runs):
    if any(physical_identity(r)!=physical_identity(runs[0]) for r in runs):raise ValueError('Within-model identity differs')
    if len(set(r['config']['branching']['seed'] for r in runs))!=len(runs):raise ValueError('Duplicate seed within a model')
    combined=pool(runs);counts={}
    for field in ['limited_turns','limited_speed_changes','limited_altitude_changes']:
        values=np.array([int(row[field]) for r in runs for row in r['rows']])
        counts[field]={str(n):float(combined[1][values==n].sum()) for n in np.unique(values)}
    summary=dict(name=name,label=LABELS[name],initial_candidates=sum(r['summary']['initial_particles'] for r in runs),
                 regions=region_masses(*combined),quantiles_05_50_95_deg=quantiles(*combined),
                 counts=counts,model=runs[0]['config']['model'],pooling_fractions=mix_weights(runs).tolist(),
                 independent_run_cdf_difference=cdf_difference((runs[0]['points'],runs[0]['weight']),
                     (runs[1]['points'],runs[1]['weight'])) if len(runs)==2 else None,
                 runs=[dict(path=str(r['path']),seed=r['config']['branching']['seed'],
                            regions=region_masses(r['points'],r['weight']),summary=r['summary'],provenance=r['provenance']) for r in runs])
    grid=area_grid(*combined,5)
    summary['ranked_airborne_area_5km_cells']=ranked_area(grid[2],5)
    return dict(name=name,runs=runs,pooled=combined,summary=summary,grid=grid)


def report(status_path,baseline,output,inline):
    output.mkdir(parents=True,exist_ok=True)
    status=json.loads(status_path.read_text());families={'baseline':baseline}
    for item in status['runs']:
        if item['status']=='completed':families.setdefault(item['family'],[]).append(Path(item['output']))
    groups=[summarize(name,[read_run(p) for p in paths]) for name,paths in families.items()]
    figures=[cdf_plot(groups,output),region_plot(groups,output)]
    for group in groups:
        sub=output/group['name'];sub.mkdir(exist_ok=True)
        runs=group['runs'];xy,w=group['pooled']
        alt=[float(row['altitude_ft']) for r in runs for row in r['rows']]
        bounds=[float(np.min(np.array(alt)[w>0])),float(np.max(np.array(alt)[w>0]))]
        figures.append(map_figure(xy,w,group['grid'],reference_arc(runs[0]['config']),sub,
                                  group['summary']['initial_candidates'],len(runs),bounds,
                                  condition_label='Post-18:25 turn / Mach / altitude caps: '+LABELS[group['name']]))
        np.savez_compressed(sub/'area-density-5km.npz',longitude_projection_edges_km=group['grid'][0],
                            latitude_projection_edges_km=group['grid'][1],probability=group['grid'][2],cell_area_km2=25.)
    summary=dict(generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='conditional_model_sensitivity',
                 queue_status=status['status'],groups=[g['summary'] for g in groups],
                 completed_sensitivity_runs=sum(r['status']=='completed' for r in status['runs']),
                 planned_sensitivity_runs=len(status['runs']),source_sha256=digest(__file__),
                 comparisons_to_matched_baseline={g['name']:cdf_difference(groups[0]['pooled'],g['pooled']) for g in groups[1:]},
                 limitations=['Only two distinct seeds per new model in this initial comparison; their variation is shown.',
                              'Models have different manoeuvre priors and are never pooled across families.',
                              'The fuel proxy and kinematic aircraft model remain conditional approximations.',
                              'Sample size and cap relaxation do not establish full physical coverage or calibrated posterior precision.'])
    rows=''
    for g in groups:
        s=g['summary'];diff=s['independent_run_cdf_difference']
        rows+=(f'<tr><td>{LABELS[g["name"]]}</td><td>{s["initial_candidates"]:,}</td>'
               f'<td>{100*s["regions"]["between_35S_and_38S"]:.1f}%</td><td>{100*s["regions"]["north_of_30S"]:.2f}%</td>'
               '<td>'+('/'.join(f'{100*d:.1f}' for d in diff)+' pp' if diff else 'Repeat pending')+'</td></tr>')
    sections=''.join('<section><button class="zoom" onclick="this.parentElement.classList.toggle(\'enlarged\')">Enlarge / fit plot</button>'+svg+'</section>' for svg in figures[:2])
    for g,svg in zip(groups,figures[2:]):
        sections+=f'<h2>{LABELS[g["name"]]}</h2><section><button class="zoom" onclick="this.parentElement.classList.toggle(\'enlarged\')">Enlarge / fit plot</button>{svg}</section>'
    body=(f'<h1>How the 00:11 estimate changes as flight assumptions are relaxed</h1>'
          f'<p>{summary["completed_sensitivity_runs"]} of {summary["planned_sensitivity_runs"]} initial comparison runs complete. '
          'Each run starts with 85,000 candidates. The baseline here uses the same two seeds as the new models; the separate million-candidate report remains the larger baseline estimate.</p>'
          '<p>The first comparison enables the Doppler contribution of climbing and descending while preserving the 4/2/2 manoeuvre caps. '
          'Later comparisons raise speed and altitude allowances, then turns. All retain the same Mach and altitude ranges, satellite observations, fuel condition and navigation-mode priors.</p>'
          '<p>Each physical model keeps its own probability distribution. A larger sample does not make an arbitrary manoeuvre cap an observation. '
          'Run-to-run differences are displayed alongside changes between models; these initial comparisons do not supply calibrated confidence intervals.</p>'
          '<div class="scroll"><table><tr><th>Turn/Mach/altitude caps</th><th>Candidates</th><th>35–38°S</th><th>North of 30°S</th><th>Repeat CDF difference: lat/lon</th></tr>'+rows+'</table></div>'+sections+
          '<p>All maps show airborne probability density at 00:10:59 UTC. They are not impact or searched-area PDFs. '
          'The 35,000 ft curve is solely a geometric reference; each candidate uses its actual altitude.</p>'
          f'<p class="stamp">Generated {summary["generated_utc"]}. Model configurations, input identities, seeds and runtime are saved with this report.</p>')
    css='body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.55 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:20px}h1{font-size:1.7em}h2{font-size:1.2em}section{background:white;margin:20px 0;overflow:auto}svg{display:block;width:100%;height:auto}.zoom{position:sticky;left:0;padding:8px;font:inherit;cursor:pointer}.enlarged svg{width:1150px;max-width:none}.scroll{overflow-x:auto}table{border-collapse:collapse;background:white;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #ccd9df;text-align:right}td:first-child,th:first-child{text-align:left}.stamp{font-size:12px;color:#617786}'
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 flight-model sensitivity</title><style>'+css+'</style><main>'+body+'</main></html>'
    if len(document.encode())>5*1024**2:raise ValueError('Inline report exceeds 5 MiB')
    for p in [output/'index.html']+([inline] if inline else []):
        tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(document);tmp.replace(p)
    summary['inline_bytes']=len(document.encode())
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    command=shlex.join(['python',str(Path(__file__).resolve()),'--status',str(status_path),'--baseline',*[str(p) for p in baseline],
                        '--output',str(output)]+(['--inline-output',str(inline)] if inline else []))
    (output/'README.md').write_text('# Cruise-model comparisons\n\n```bash\n'+command+'\n```\n\n'
        'Equal-effort SMC measures are pooled within a model using their estimated normalizers. Different priors are never combined. '
        'The matched baseline consists of two selected original runs, not the full million ensemble.\n')
    print(json.dumps({k:summary[k] for k in ['queue_status','completed_sensitivity_runs','inline_bytes']}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--status',type=Path,required=True)
    p.add_argument('--baseline',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--inline-output',type=Path);a=p.parse_args();report(a.status,a.baseline,a.output,a.inline_output)
