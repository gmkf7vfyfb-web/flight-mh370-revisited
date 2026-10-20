"""Display exact retained flight histories, grouped by terminal latitude.

This is artifact rendering only. Display sampling does not alter the estimator.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import gzip
import json
from pathlib import Path
import shlex

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from arc_density_report import digest, draw_land, reference_arc, save_figure

MODES = dict(constant_true_heading='CTH', constant_magnetic_heading='CMH',
             constant_true_track='CTT', constant_magnetic_track='CMT', lateral_navigation='LNAV')
COLOURS = ['#15698d', '#cb6023', '#23866c', '#9c407c', '#787329', '#75539a']


def load_histories(paths, pooled):
    original = {r['seed']: r for r in pooled['runs']}
    examples, sources = [], []
    for path in paths:
        trace = json.loads((path / 'trajectory-examples.json').read_text())
        run = json.loads((path / 'summary.json').read_text())
        seed = trace['seed']
        source = original[seed]
        if not trace['full_contact_state_and_likelihood_match']:
            raise ValueError('Histories failed exact replay checks')
        if digest(path / 'posterior.csv') != run['posterior_csv_sha256']:
            raise ValueError('Recovered run checksum mismatch')
        if (run['posterior_csv_sha256'] != source['source_files_sha256']['posterior.csv']
                or run['log_evidence'] != source['log_evidence']):
            raise ValueError('Recovered histories changed original endpoint output')
        for example in trace['examples']:
            points = example['points']
            aircraft = example['terminal']['flight']['aircraft']
            end = points[-1]
            if [end['latitude_deg'], end['longitude_deg'], end['altitude_ft'], end['time_s']] != [
                    aircraft['position']['latitude'], aircraft['position']['longitude'],
                    aircraft['altitude'], aircraft['time']]:
                raise ValueError('A displayed history does not end at its saved particle')
            if any(b['time_s'] <= a['time_s'] for a, b in zip(points, points[1:])):
                raise ValueError('A history has non-increasing integration times')
        examples.extend(trace['examples'])
        sources.append(dict(path=str(path), seed=seed, examples=len(trace['examples']),
                            initial_candidates=run['initial_particles'],
                            exact_contact_state_checks=trace['exact_replay_checks'],
                            trajectory_sha256=digest(path / 'trajectory-examples.json'),
                            original_posterior_sha256=run['posterior_csv_sha256']))
    config = json.loads((paths[0] / 'resolved-config.json').read_text())
    return examples, sources, config


def path_label(example):
    flight = example['terminal']['flight']
    counts = flight['limited_manoeuvre_counts']
    return (f"{str(example['seed'])[-2:]}:{example['terminal_slot']} · "
            f"{MODES[flight['initial_mode']]} · {counts[0]}/{counts[1]}/{counts[2]}")


def fit_summary(example):
    bto, bfo = [], []
    bias = example['terminal']['bfo_bias']['mean_hz']
    for contact in example['contacts']:
        m = contact['observation']['measurement']
        fit = contact['state']['last_fit']
        if m['bto'] is not None:
            bto.append(abs(fit['bto_residual_us']) / m['bto_sd'])
        if m['bfo'] is not None:
            bfo.append(abs(m['bfo'] - fit['predicted_bfo_without_bias_hz'] - bias) / m['bfo_sd'])
    return dict(max_abs_bto_residual_sd=max(bto), max_abs_bfo_residual_sd=max(bfo),
                bfo_bias_mean_hz=bias)


def figure_for_bin(center, mass, examples, arc, pdf, output, conditions, source_count):
    fig = plt.figure(figsize=(9, 9))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.4, 1, 1], width_ratios=[1.08, 1])
    map_ax = fig.add_subplot(gs[:, 0])
    altitude_ax = fig.add_subplot(gs[0, 1])
    mach_ax = fig.add_subplot(gs[1, 1], sharex=altitude_ax)
    legend_ax = fig.add_subplot(gs[2, 1]); legend_ax.axis('off')
    map_ax.set_facecolor('#f0f5f8'); draw_land(map_ax)
    map_ax.plot(arc[1], arc[0], '--', color='#16858a', lw=.85)
    positions = []
    for index, example in enumerate(examples):
        colour = COLOURS[index % len(COLOURS)]
        points = example['points']
        values = np.array([[p[k] for k in ['time_s','latitude_deg','longitude_deg','altitude_ft','mach']]
                           for p in points])
        early = values[:,0] <= 1425
        late = values[:,0] >= 1425
        positions.extend(values[:,1:3])
        map_ax.plot(values[early,2], values[early,1], color=colour, lw=.7, ls=':', alpha=.7)
        map_ax.plot(values[late,2], values[late,1], color=colour, lw=1.15, alpha=.9)
        contacts = [c['state']['flight']['aircraft']['position'] for c in example['contacts']]
        map_ax.scatter([p['longitude'] for p in contacts], [p['latitude'] for p in contacts],
                       c=colour, s=12, marker='o', edgecolors='white', linewidths=.4, zorder=5)
        map_ax.scatter(values[-1,2], values[-1,1], color=colour, s=36, marker='x', zorder=6)
        hours = values[:,0]/3600
        altitude_ax.plot(hours, values[:,3]/1000, color=colour, lw=1)
        mach_ax.plot(hours, values[:,4], color=colour, lw=.85)
        legend_ax.plot([],[],color=colour,lw=2,label=path_label(example))
    positions = np.array(positions)
    map_ax.set(xlim=(positions[:,1].min()-2, positions[:,1].max()+2),
               ylim=(positions[:,0].min()-2, positions[:,0].max()+2),
               xlabel='Longitude (°E)', ylabel='Latitude (°)', title='Exact integrated routes')
    map_ax.set_aspect(1/np.cos(np.deg2rad((positions[:,0].min()+positions[:,0].max())/2)))
    map_ax.grid(alpha=.2)
    altitude_ax.set(ylabel='Altitude (thousands of ft)', title='Altitude and Mach histories')
    mach_ax.set(ylabel='Mach', xlabel='UTC (7–8 March 2014)')
    ticks = np.array([1394218800,1394226000,1394233200,1394237459])-1394215309
    mach_ax.set_xticks(ticks/3600, ['19:00','21:00','23:00','00:11'])
    for ax in [altitude_ax,mach_ax]:
        ax.grid(alpha=.2);ax.tick_params(labelsize=8)
    legend_ax.legend(loc='upper left',fontsize=8,frameon=False,title='Seed suffix:row · initial mode · turn/Mach/alt starts',title_fontsize=7)
    fig.suptitle(f'00:11 latitude bin centred on {abs(center):g}°S (±1.25°)\n'
                 f'{100*mass:.3g}% of the pooled probability', fontsize=13)
    fig.subplots_adjust(top=.88,bottom=.16,left=.08,right=.98,wspace=.38,hspace=.32)
    fig.text(.5,.025,f'Each line is a saved trajectory, selected within this bin from {source_count} existing runs; line counts do not represent probability.\n'
             'Dots: SATCOM contacts. Cross: 00:10:59 endpoint. Dotted route: before 18:25:34. Dashed arc: reference at 35,000 ft only.\n'
             +conditions+'\n'+
             'Gaussian errors give positive weight to poor fits too. Residuals and rare-bin limitations are listed in the browser report.',
             ha='center',fontsize=7)
    pdf.savefig(fig,bbox_inches='tight')
    name=f'latitude-{abs(center):g}S'.replace('.','p')
    return name,save_figure(fig,output,name)


def report(histories, pooled_path, output, inline):
    # Keep SVG labels as accessible text instead of duplicating font outlines
    # in every latitude panel. The vector PDF still embeds its print fonts.
    plt.rcParams['svg.fonttype']='none'
    output.mkdir(parents=True,exist_ok=True)
    pooled=json.loads(pooled_path.read_text())
    examples,sources,config=load_histories(histories,pooled)
    arc=reference_arc(config)
    limits=config['model']['dynamics']['manoeuvre_limits']['maximum_counts']
    conditions=f'Post-18:25 caps: {limits[0]} turns / {limits[1]} Mach / {limits[2]} altitude starts; BTO/BFO + fuel; vertical BFO '+('enabled.' if config['model'].get('include_vertical_doppler',False) else 'omitted.')
    bins=pooled['complexity_by_latitude'][0]
    options,panels,records=[],[],[]
    drawings={}
    with PdfPages(output/'trajectory-examples.pdf') as pdf:
        for center,mass in zip(bins['latitude_bin_centers_deg'],bins['latitude_bin_probability']):
            chosen=[e for e in examples if e['latitude_bin_center_deg']==center]
            if mass<=0:continue
            metadata=[dict(seed=e['seed'],terminal_slot=e['terminal_slot'],label=path_label(e),
                           source_run_weight=e['source_run_weight'],
                           source_bin_probability=e['bin_probability_in_source_run'],
                           **fit_summary(e)) for e in chosen]
            records.append(dict(latitude_bin_center_deg=center,pooled_bin_probability=mass,examples=metadata))
            if not chosen:
                svg='<p>No history retained in the illustrated runs for this bin.</p>'
                name=f'latitude-{abs(center):g}S'.replace('.','p')
            else:name,svg=figure_for_bin(center,mass,chosen,arc,pdf,output,conditions,len(sources))
            drawings[name]=svg
            options.append(f'<option value="{name}">{abs(center):g}°S ±1.25° · {100*mass:.3g}% of pool</option>')
            rows=''.join(f'<tr><td>{html.escape(m["label"])}</td><td>{m["max_abs_bto_residual_sd"]:.2f}</td>'
                         f'<td>{m["max_abs_bfo_residual_sd"]:.2f}</td><td>{100*m["source_bin_probability"]:.3g}%</td></tr>' for m in metadata)
            panels.append(f'<section id="{name}" class="bin"><button class="zoom" onclick="this.parentElement.classList.toggle(\'enlarged\')">Enlarge / fit plot</button><div id="plot-{name}">Loading saved plot…</div>'
                          '<div class="scroll"><table><tr><th>Displayed trajectory</th><th>Largest |BTO| residual / σ</th>'
                          f'<th>Largest |BFO| residual / σ</th><th>Bin probability in source run</th></tr>{rows}</table></div></section>')
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    body=(f'<h1>Sample flight histories along the 00:11 arc</h1><p>{len(examples)} exact saved histories from {len(sources)} existing runs ({", ".join(str(s["initial_candidates"]) for s in sources)} initial candidates), '
          f'covering {len(records)} latitude bins. The probability shown for each bin comes from all {pooled["total_initial_candidates"]:,} initial candidates.</p>'
          '<p>Choose a latitude to compare routes, altitude and Mach histories. Each bin is 2.5° wide. The examples were sampled using their weights within each source run; '
          'they are illustrations, not a new ensemble or an estimate of each route’s individual probability.</p>'
          '<p>The northernmost bins carry very little probability and have weak sampling support. Some displayed paths have large satellite residuals: '
          'positive Gaussian likelihood does not mean a path satisfies every observation within one or two standard deviations. '
          'The tables make these residuals visible. The source runs can also assign different weight to a bin.</p>'
          '<label for="latitude">Terminal latitude</label><select id="latitude" onchange="showBin(this.value)">'+''.join(options)+'</select>'+''.join(panels)+
          '<details><summary>How to read and reproduce this report</summary><p>Turn, Mach and altitude counts refer to command starts after 18:25:34. '
          'CTH/CMH mean constant true/magnetic heading; CTT/CMT mean constant true/magnetic track; LNAV means the model’s lateral-navigation family. '
          'The BFO residuals use each complete path’s final fitted common bias; σ is the input observation standard deviation. '
          'No additional error cutoff is imposed for display.</p><p>Histories were recovered by deterministic replay with all contact states and likelihoods checked exactly. '
          'Their endpoint CSVs match the original runs byte for byte. Full-resolution histories remain in the source artifacts; plots simplify only their rendering.</p>'
          f'<p>{sum(s["exact_contact_state_checks"] for s in sources)} exact contact-state checks. Source hashes, identities, bin tables and the reproduction command are recorded alongside the exported vector PDF.</p></details>'
          f'<p class="stamp">Generated {stamp}. Conditional cruise estimate through 00:10:59 UTC; this is not an impact or search-area map.</p>')
    css='body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.55 system-ui,sans-serif}main{max-width:1050px;margin:auto;padding:20px}h1{font-size:1.8em}label{display:block;font-weight:600}select{max-width:100%;font:inherit;padding:10px;margin:8px 0 20px}.bin{display:none;background:white;overflow:auto}.bin.active{display:block}svg{display:block;width:100%;height:auto}.zoom{position:sticky;left:0;padding:8px;font:inherit;cursor:pointer}.enlarged svg{width:1200px;max-width:none}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:8px;border-bottom:1px solid #ccd9df;text-align:right}th:first-child,td:first-child{text-align:left}details{background:white;padding:15px;margin-top:20px}.stamp{font-size:12px;color:#617786}'
    script="function showBin(id){document.querySelectorAll('.bin').forEach(p=>p.classList.toggle('active',p.id===id));}const chosen=document.getElementById('latitude');chosen.value='latitude-37p5S';showBin(chosen.value||chosen.options[0].value);"
    packed=base64.b64encode(gzip.compress(json.dumps(drawings,separators=(',',':')).encode(),mtime=0)).decode()
    script+='const packed="'+packed+'";async function loadPlots(){const bytes=Uint8Array.from(atob(packed),c=>c.charCodeAt(0));const data=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"))).text());for(const [id,svg] of Object.entries(data))document.getElementById("plot-"+id).innerHTML=svg;}loadPlots().catch(e=>{document.querySelectorAll("[id^=plot-]").forEach(n=>n.textContent="Could not load saved plot: "+e.message);});'
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 trajectory examples</title><style>'+css+'</style><main>'+body+'</main><script>'+script+'</script></html>'
    if len(document.encode())>5*1024**2:raise ValueError('Inline report exceeds 5 MiB')
    for path in [output/'index.html']+([inline] if inline else []):
        temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_text(document);temporary.replace(path)
    command=shlex.join(['python',str(Path(__file__).resolve()),'--histories',*[str(p) for p in histories],
                        '--pooled-summary',str(pooled_path),'--output',str(output)]+(['--inline-output',str(inline)] if inline else []))
    summary=dict(generated_utc=stamp,source_runs=sources,pooled_summary=str(pooled_path),pooled_summary_sha256=digest(pooled_path),
                 source_sha256=digest(__file__),initial_candidates=pooled['total_initial_candidates'],bins=records,
                 exact_history_count=len(examples),inline_bytes=len(document.encode()),reproduction_command=command)
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'README.md').write_text('# Exact trajectory examples\n\nReproduce with:\n\n```bash\n'+command+'\n```\n\n'
         'Dependencies match the canonical arc-density report (NumPy and Matplotlib). All routes come from saved exact deterministic replays. '
         'No trajectory is inferred by joining contact positions. Latitude-bin probabilities use the stated pooled ensemble; example source runs are listed above. '
         'Histories are illustrative positive-weight draws, not a hard observation-fit feasibility boundary.\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--histories',type=Path,nargs='+',required=True)
    parser.add_argument('--pooled-summary',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--inline-output',type=Path)
    a=parser.parse_args()
    result=report(a.histories,a.pooled_summary,a.output,a.inline_output)
    print(json.dumps({k:result[k] for k in ['exact_history_count','inline_bytes','source_runs']},indent=2))
