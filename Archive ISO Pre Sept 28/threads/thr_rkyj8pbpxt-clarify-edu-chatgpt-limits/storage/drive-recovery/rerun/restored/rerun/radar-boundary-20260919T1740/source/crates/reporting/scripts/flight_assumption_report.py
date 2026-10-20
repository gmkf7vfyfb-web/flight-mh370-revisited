#!/usr/bin/env python3
"""Figures and a readable summary from verified trajectory witness artifacts."""
import argparse, json, math, pathlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon
from html import escape

ROOT=pathlib.Path(__file__).resolve().parents[3]

def distance_nm(a,b):
    p1,p2=map(math.radians,[a['latitude'],b['latitude']]);dp=p2-p1;dl=math.radians(b['longitude']-a['longitude'])
    return 6371.0088/1.852*2*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2)))

def write_web_report(output, fig, route_axis, fig2, cruise_axes, groups, colors, labels):
    """Publish the existing results as separate, phone-sized vector plots."""
    web=output/'web';web.mkdir(exist_ok=True)
    for annotation in fig.texts:annotation.set_visible(False)
    for axis in fig.axes:
        if axis is not route_axis:axis.set_visible(False)
    route_axis.get_legend().remove()
    route_axis.set_title('')
    route_axis.tick_params(labelsize=11)
    route_axis.xaxis.label.set_size(11);route_axis.yaxis.label.set_size(11)
    fig.canvas.draw()
    bounds=route_axis.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted()).padded(.1)
    fig.savefig(web/'routes.svg',bbox_inches=bounds)
    # Put each long allowance label above its marks, keeping the plot readable
    # at a phone's width without shortening the scientific conditions.
    mobile,axis=plt.subplots(figsize=(5.5,6.5))
    for i,(label,subset) in enumerate(groups):
        axis.text(-42.5,i-.27,label,fontsize=11,va='center')
        axis.scatter([r['metrics']['latitude'] for r in subset],[i+.15]*len(subset),marker='|',s=105,lw=1.2,color='#315b80' if i<5 else '#1c877d')
    axis.set(xlim=(-43,-10),ylim=(len(groups)-.35,-.65),yticks=[])
    axis.set_xticks([-40,-35,-30,-25,-20,-15],[f'{x}°S' for x in [40,35,30,25,20,15]])
    axis.tick_params(labelsize=11)
    axis.set_xlabel('00:11 endpoint latitude',fontsize=12)
    axis.spines['left'].set_visible(False);axis.grid(axis='x',alpha=.15)
    mobile.tight_layout();mobile.savefig(web/'allowances.svg');plt.close(mobile)
    cruise_axes[0].get_legend().remove()
    for annotation in fig2.texts:annotation.set_visible(False)
    fig2.set_size_inches(5.5,9)
    cruise_axes[-1].set_xticks(np.array([1425,9555,16772,22150])/3600,['18:25','20:41','22:41','00:11'])
    for axis in cruise_axes:
        axis.tick_params(labelsize=11,labelbottom=True)
        axis.yaxis.label.set_size(11);axis.set_xlabel('UTC, 7–8 March 2014',fontsize=11)
    fig2.tight_layout(rect=(0,.08,1,.95));fig2.canvas.draw()
    for axis,name in zip(cruise_axes,['altitude','mach','fuel']):
        bounds=axis.get_tightbbox(fig2.canvas.get_renderer()).transformed(fig2.dpi_scale_trans.inverted()).padded(.1)
        fig2.savefig(web/(name+'.svg'),bbox_inches=bounds)
    legend=''.join(f'<li><span style="background:{color}"></span>{escape(label)}</li>' for color,label in zip(colors,labels))
    panels=[('routes','Example routes','The coloured routes use constant cruise targets. Dots mark observation times; squares mark 00:11 endpoints. Grey dots are other verified endpoints. Settings count commanded direction targets, including navigation-mode changes.'),
            ('allowances','What changes when more manoeuvres are allowed?','Each mark is an endpoint found in the bounded search. Mark density is not probability, and gaps remain unresolved. Each allowance includes the simpler examples. Speed and altitude allowances apply separately to each type of adjustment.'),
            ('altitude','Altitude along the example routes','The same three example routes are shown below. These selected examples keep cruise targets constant; the wider comparison also includes speed and altitude adjustments.'),
            ('mach','Mach number','Mach number is speed relative to the local speed of sound.'),
            ('fuel','Fuel remaining','Fuel is calculated using the declared fuel model. The trajectories are conditioned on a later exhaustion-to-logon delay of 30–300 seconds; this is an assumed window, not a measured timing uncertainty.')]
    sections=''.join(f'<section id="{name}"><h2>{escape(title)}</h2><p>{escape(caption)}</p>'+(f'<ul class="legend">{legend}</ul>' if name in ['routes','altitude'] else '')+f'<a class="plot" href="{name}.svg" target="_blank" rel="noopener" aria-label="Enlarge {escape(title)}"><img src="{name}.svg" alt="{escape(title)}" loading="lazy"></a><a class="enlarge" href="{name}.svg" target="_blank" rel="noopener">Open full-size plot ↗</a></section>' for name,title,caption in panels)
    page='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MH370 — Flight assumption comparison</title>
<style>
:root{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#243746;background:#f2f5f6;color-scheme:light}
*{box-sizing:border-box}body{margin:0}main{max-width:760px;margin:auto;padding:28px 16px 48px}
.eyebrow{color:#496777;letter-spacing:.08em;text-transform:uppercase;font-size:.78rem;font-weight:650}
h1{font-size:clamp(1.65rem,5vw,2.4rem);line-height:1.15;margin:10px 0 16px}h2{font-size:1.25rem;line-height:1.3;margin:0 0 10px}
p{line-height:1.6;margin:0 0 16px}a{color:#145e87;text-underline-offset:3px}a:focus-visible{outline:3px solid #bf781e;outline-offset:4px}
.note{border-left:4px solid #bf781e;background:#fff8ee;padding:12px 16px;border-radius:4px;margin:20px 0;line-height:1.55}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 24px}nav a{display:block;padding:10px 14px;border:1px solid #bccbd3;border-radius:24px;text-decoration:none;background:white}
section{scroll-margin-top:16px;background:white;border:1px solid #dce4e8;border-radius:14px;padding:22px 18px;margin-bottom:20px}
.plot{display:block;margin:12px auto 0;max-width:610px}.plot img{width:100%;height:auto;display:block}.enlarge{display:inline-block;padding:12px 0 0;font-size:.9rem}
.legend{list-style:none;margin:12px 0 18px;padding:0;font-size:.9rem;line-height:1.7}.legend span{display:inline-block;width:24px;height:4px;border-radius:2px;vertical-align:middle;margin-right:9px}
footer{font-size:.9rem;line-height:1.6;color:#526571}@media(max-width:480px){main{padding:22px 10px 32px}section{padding:18px 10px}h1{margin-bottom:12px}}
</style></head><body><main>
<div class="eyebrow">MH370 · Bounded pre-analysis</div><h1>Flight assumption comparison</h1>
<p>The comparison plots, arranged for reading on a phone. Tap any plot to open it at full size and zoom in.</p>
<div class="note"><strong>Feasible examples, not a probability map.</strong> These results depend on the stated flight, SATCOM and fuel models. They do not establish the outer limits of possible routes or a preferred impact location.</div>
<nav aria-label="Plots"><a href="#routes">Routes</a><a href="#allowances">Allowed changes</a><a href="#altitude">Altitude, speed &amp; fuel</a></nav>
'''+sections+'''
<footer>Same verified trajectories as the comparison PDF. No additional simulation was needed to create this page. The earlier flight segment, aircraft performance bounds, weather and fuel model remain conditional. Ocean drift, Pléiades, antenna gain, hydroacoustics and search non-detection are not included; no impact location is inferred.</footer>
</main></body></html>'''
    (web/'index.html').write_text(page)

def main(output, web_only=False):
    rows=[json.loads(x) for x in (output/'verified-witnesses.jsonl').read_text().splitlines()]
    if not rows:raise ValueError('No verified trajectory witnesses.')
    nominal=[r for r in rows if r['request'].get('flow_scale',1)==1]
    constant=[r for r in nominal if not r['command_counts']['mach'] and not r['command_counts']['altitude']]
    groups=[]
    for cap in [1,2,4,8,16]:
        subset=[r for r in constant if r['command_counts']['control']<=cap]
        groups.append((str(cap)+(' direction change' if cap==1 else ' direction changes'),subset))
    for cap in [2,4,8]:
        subset=[r for r in nominal if r['command_counts']['control']<=8 and r['command_counts']['mach']<=cap and r['command_counts']['altitude']<=cap]
        groups.append((f'8 direction + up to {cap} speed/altitude',subset))
    limits=[]
    for label,subset in groups:
        limits.append({'comparison':label,'examples':len(subset),'south_latitude':min(r['metrics']['latitude'] for r in subset),'north_latitude':max(r['metrics']['latitude'] for r in subset)})
    south=min(nominal,key=lambda r:r['metrics']['latitude']);north=max(nominal,key=lambda r:r['metrics']['latitude'])
    separation=distance_nm(south['metrics'],north['metrics'])
    one=[r for r in constant if r['command_counts']['control']==1]
    simple=min(one,key=lambda r:r['metrics']['joint_chi2'])
    north_simple=min([r for r in constant if r['metrics']['latitude']>-16],key=lambda r:(r['command_counts']['control'],r['metrics']['joint_chi2']))
    middle=min([r for r in constant if abs(r['metrics']['latitude']+30)<1],key=lambda r:r['metrics']['joint_chi2'])
    selected=[simple,middle,north_simple]
    colors=['#315b80','#bf781e','#1c877d']
    labels=[f"{r['command_counts']['control']} direction setting{'s' if r['command_counts']['control']!=1 else ''}; {abs(r['metrics']['latitude']):.0f}°S endpoint" for r in selected]
    runtimes={name:json.loads((output/(name+'-runtime.json')).read_text()) for name in ['search','refinement','supplement','verification']}
    runtime=sum(r['elapsed_s'] for r in runtimes.values())
    cpu=runtimes['search']['child_user_cpu_s']+runtimes['search']['child_system_cpu_s']+sum(runtimes[x].get('child_cpu_s',0) for x in ['refinement','supplement'])
    checks=json.loads((output/'integration-checks.json').read_text())
    separations=[];time_diffs=[]
    for c in checks:
        a,b=c['comparisons'][0]['metrics'],c['comparisons'][-1]['metrics']
        if a.get('valid') and b.get('valid'):
            separations.append(distance_nm(a,b))
            if a.get('restart_delay_s') is not None and b.get('restart_delay_s') is not None:time_diffs.append(abs(a['restart_delay_s']-b['restart_delay_s']))
    coherence=[]
    for row in selected:
        trace=row['result']['trace'];heading=np.array([v['heading_true_deg'] for v in trace]);alt=np.array([v['aircraft']['altitude'] for v in trace]);mach=np.array([v['mach'] for v in trace])
        modes=[row['request']['initial_mode']]+[c['mode'] for c in sorted(row['request']['commands'],key=lambda c:c['time']) if 'control' in c]
        coherence.append({'endpoint_latitude':row['metrics']['latitude'],'direction_target_changes':row['command_counts']['control'],'mode_switches':sum(a!=b for a,b in zip(modes,modes[1:])),'sampled_absolute_heading_change_deg':float(np.abs((np.diff(heading)+180)%360-180).sum()),'total_climb_ft':float(np.maximum(np.diff(alt),0).sum()),'total_descent_ft':float(np.maximum(-np.diff(alt),0).sum()),'total_mach_variation':float(np.abs(np.diff(mach)).sum())})
    if not web_only:
        with (output/'witness-requests.jsonl').open('w') as f:
            for row in rows:f.write(json.dumps(row['request'])+'\n')
    summary={'status':'conditional feasibility examples; no posterior and no certified exclusion','coherence_examples':coherence,'comparisons':limits,'verified_examples':len(rows),'extreme_example_separation_nm':separation,'south_example':south['metrics'],'north_example':north['metrics'],'search_and_verification_elapsed_seconds_sum':runtime,'search_child_cpu_seconds':cpu,'search_evaluations':sum(runtimes[k]['evaluations'] for k in ['search','refinement','supplement']),'search_profiles':sum(runtimes[k]['profiles'] for k in ['search','refinement','supplement']),'maximum_coarse_to_fine_endpoint_shift_nm':max(separations),'maximum_coarse_to_fine_exhaustion_time_shift_s':max(time_diffs)}
    if not web_only:(output/'summary.json').write_text(json.dumps(summary,indent=2))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig,(ax,profile)=plt.subplots(1,2,figsize=(11.7,6.7),gridspec_kw={'width_ratios':[1,1.2]})
    land=json.loads((ROOT/'crates/reporting/assets/ne_110m_land.geojson').read_text())
    for feature in land['features']:
        g=feature['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'] if g['type']=='MultiPolygon' else []
        for poly in polys:
            ring=np.asarray(poly[0]);ax.add_patch(Polygon(ring,facecolor='#e5e7e9',edgecolor='#adb5bc',linewidth=.35,zorder=0))
    # The guide joins actual checked endpoints; it is not a separately calculated arc or exclusion boundary.
    ordered=sorted(nominal,key=lambda r:r['metrics']['latitude'])
    ax.scatter([r['metrics']['longitude'] for r in ordered],[r['metrics']['latitude'] for r in ordered],s=7,c='#8c959c',alpha=.4,label='Other verified 00:11 endpoints')
    for r,color,label in zip(selected,colors,labels):
        trace=r['result']['trace'];lat=[t['aircraft']['position']['latitude'] for t in trace];lon=[t['aircraft']['position']['longitude'] for t in trace]
        ax.plot(lon,lat,color=color,lw=1.3,label=label)
        fit=r['result']['fits'];ax.scatter([x['aircraft']['position']['longitude'] for x in fit],[x['aircraft']['position']['latitude'] for x in fit],s=10,color=color)
        ax.scatter([lon[-1]],[lat[-1]],s=36,marker='s',color=color,zorder=5)
    ax.set(xlim=(79,121),ylim=(-43,10),xlabel='Longitude (°E)',ylabel='Latitude (°)',title='Example trajectories and their 00:11 endpoints')
    ax.set_aspect(1/math.cos(math.radians(20)));ax.grid(alpha=.18);ax.legend(loc='upper left',fontsize=6.8,framealpha=.94)
    for i,(label,subset) in enumerate(groups):
        lats=[r['metrics']['latitude'] for r in subset]
        profile.scatter(lats,[i]*len(lats),marker='|',s=95,lw=1.1,color='#315b80' if i<5 else '#1c877d')
    profile.set_yticks(range(len(groups)),[x[0] for x in groups]);profile.invert_yaxis();profile.set_xlim(-43,-10)
    profile.set_xticks([-40,-35,-30,-25,-20,-15],[f'{x}°S' for x in [40,35,30,25,20,15]])
    profile.set_xlabel('00:11 endpoint latitude along the eastern arc');profile.set_title('Demonstrated endpoints as allowances increase')
    profile.grid(axis='x',alpha=.2)
    fig.suptitle('MH370 flight-assumption pre-analysis',fontsize=17,y=.98)
    fig.text(.5,.925,'Conditional feasibility examples • marker density is not probability • empty space is unresolved',ha='center',fontsize=9,color='#6e3b29')
    fig.text(.04,.04,'Nominal fuel proxy; declared restart delay 30–300 s. All shown examples pass BTO/BFO checks at three integration resolutions.\nThe earlier radar-to-18:25 segment, performance bounds, weather and fuel assumptions remain conditional. No later location evidence is enabled.',fontsize=8)
    fig.subplots_adjust(left=.06,right=.98,bottom=.15,top=.86,wspace=.72)
    if not web_only:
        fig.savefig(output/'comparison.png',dpi=170);fig.savefig(output/'comparison.svg')
    fig2,axes=plt.subplots(3,1,figsize=(8.3,9),sharex=True)
    for r,color,label in zip(selected,colors,labels):
        trace=r['result']['trace'];t=np.array([v['aircraft']['time'] for v in trace])/3600
        axes[0].plot(t,[v['aircraft']['altitude']/1000 for v in trace],color=color,label=label)
        axes[1].plot(t,[v['mach'] for v in trace],color=color)
        axes[2].plot(t,[v['fuel_kg']/1000 for v in trace],color=color)
    for a in axes:a.grid(alpha=.2)
    axes[0].set_ylabel('Pressure altitude (1,000 ft)');axes[1].set_ylabel('Mach number');axes[2].set_ylabel('Fuel onboard (tonnes)')
    ticks=np.array([1425,5953,9555,13177,16772,18793,22150])/3600
    axes[2].set_xticks(ticks,['18:25','19:41','20:41','21:41','22:41','23:15','00:11']);axes[2].set_xlabel('UTC, 7–8 March 2014')
    axes[0].legend(fontsize=8);fig2.suptitle('Wider examples with steady cruise targets',fontsize=13)
    fig2.text(.1,.035,'These selected examples keep cruise targets constant. Separate 2/4/8 speed and altitude adjustment tests\nare included in the comparison. Constant cruise is a conditional subset, not a preferred pilot behaviour.',fontsize=8)
    fig2.tight_layout(rect=(0,.08,1,.95))
    if not web_only:
        with PdfPages(output/'flight-assumption-preanalysis.pdf') as pdf:
            pdf.savefig(fig);pdf.savefig(fig2)
    write_web_report(output,fig,ax,fig2,axes,groups,colors,labels)
    plt.close(fig2);plt.close(fig)
    if web_only:
        print(output/'web/index.html');return
    coherence_table='\n'.join(f"| {abs(c['endpoint_latitude']):.0f}°S | {c['direction_target_changes']} | {c['mode_switches']} | {c['sampled_absolute_heading_change_deg']:.0f}° | {c['total_climb_ft']:.0f} / {c['total_descent_ft']:.0f} |" for c in coherence)
    exact_fuel=all(r['result'].get('continuation',{}).get('method')=='exact_boundary' for r in rows)
    fuel_note=('These artifacts use the repaired exact fuel-exhaustion boundary. Changing-flow event times are bracketed and reintegrated; the canonical regression compares against an independently integrated changing-Mach fuel law.' if exact_fuel else 'These original artifacts used ordinary fuel continuation steps of at most 10 seconds, refined to 2.5 seconds, because they predate the exact-boundary repair. No post-exhaustion location from that diagnostic is used. The current runner has since repaired the changing-flow boundary; regenerating the control uses that repaired method.')
    table='\n'.join(f"| {r['comparison']} | {abs(r['south_latitude']):.1f}°S to {abs(r['north_latitude']):.1f}°S |" for r in limits)
    text=f'''# Flight-assumption pre-analysis

**The one-turn restriction can hide a much wider feasible set.** Verified examples in this bounded probe terminate from approximately {abs(south['metrics']['latitude']):.0f}°S to {abs(north['metrics']['latitude']):.0f}°S at 00:11. The extreme examples are {separation:.0f} nautical miles apart by great-circle distance; the along-arc span is longer. These are demonstrated examples under declared models, not outer bounds, a credible interval, a density estimate, or a search recommendation.

[Browser comparison plots](web/index.html) · [Comparison PDF](flight-assumption-preanalysis.pdf) · [Machine-readable summary](summary.json) · [Run provenance](run-manifest.json)

| Allowed target changes after 18:25 | Demonstrated endpoint range in this probe |
| --- | --- |
{table}

Ranges include examples from smaller allowances; a trajectory with fewer commands remains admissible when the allowance increases. They are spans between found examples, not a claim that every intervening point has been established. Decimal degrees document the calculation rather than confidence in a boundary. Counts are commanded settings, not a judgement about pilot intent. Some are small corrections or changes of navigation mode.

The main sweep compared 1/2/4/8/16 direction settings, then allowed 2/4/8 speed and altitude target changes separately from direction. Follow-up searches stepped along the arc, removed commands from successful paths, tried all five fixed navigation modes, and used fixed fuel-flow multipliers 0.9 and 1.1 as separate alternatives. Separate speed-only and altitude-only checks were also run. Six structured holding-command probes did not meet all conditions; this limited result does not exclude holding patterns. The northern examples could be reduced to six direction settings while retaining constant cruise targets.

The first coarse sweep appeared to leave gaps and to stop around 20°S. Following successful paths to nearby endpoints found additional examples towards 15°S, including eight-command paths. This shows that apparent gaps and apparent turn-count advantages can be failures of the search. The modest extra span found with 16 settings does not certify saturation at eight. No maximum possible extent X or model-weighted conditional width Y has yet been established.

## Descriptive simplicity measures

| Example endpoint | Direction settings | Mode switches | Sampled total heading change | Climb / descent (ft) |
| --- | ---: | ---: | ---: | ---: |
{coherence_table}

These measures have no assigned probability weight. Total heading change includes the effects of winds and navigation geometry; it is not a count of deliberate turns. Cruise adjustments remain separate. The full vector, including Mach variation, is saved in the summary.

## What was assumed

- The likelihood uses the ten existing observation epochs from 18:25 through 00:11, including the existing C-channel averages. The first 18:25 BFO is absent. BTO deviations are 29 microseconds, except 43 microseconds for the anomalous 18:25 observation. BFO deviation is 7 Hz, with one shared uncertain bias (existing prior mean 150 Hz and standard deviation 25 Hz).
- The optimizer uses endpoint-target and nominal fuel-time residuals to guide its search (0.2 degrees and 90 seconds as numerical scales). These guidance choices affect search efficiency and which examples are found; they are not additional observations or probability weights in a reported PDF.
- A diagnostic fit screen requires every BTO residual and every BFO residual after the shared-bias fit to be within three declared standard deviations, and the joint standardized squared error to be at most 38. This is a declared screening convention, not a calibrated confidence level. No independent offset is fitted to each BFO.
- Trajectories start from the existing 18:01:49 radar prior. Its position and direction vary within three prior standard deviations. Before 18:25, each trial retains its initial navigation mode and cruise targets; that earlier flying behaviour has not been broadly searched here. Initial Mach is 0.73–0.84 and altitude 25,000–43,000 ft; initial vertical speed is zero.
- After 18:25, command times are continuous. All five existing navigation modes are available in tested schedules. Speed targets may range from Mach 0.3 to 0.87 and altitude targets from 500 to 43,000 ft, subject to the canonical lift, speed, bank, roll, acceleration, climb, thrust and drag checks. The finite mode schedules are not an exhaustive mode-sequence enumeration.
- ERA5 and IGRF inputs are fixed at the configured reconstructions. Public aerodynamic/thrust proxies and the declared fuel extension are conditional models, not a calibrated Boeing performance deck. The main matrix holds the fuel-flow multiplier at 1.0; 0.9 and 1.1 are sensitivity alternatives.
- Fuel uses the existing calculated 18:28 anchor of about 33.5 tonnes and symmetric engine feed/flow. This anchor is calculated, not a direct onboard measurement. Direction changes, climbs, speed and declining mass feed into the actual trajectory calculation.
- The later restart is conditioned through positive exhaustion-to-logon delay windows of 60–180 seconds and 30–300 seconds, relative to 00:19:29.416. Both windows are analyst sensitivity choices. They are not empirical timing confidence intervals. The nominal 00:17:30 comes from the approximate APU/SDU sequence in [ATSB's 2015 report](https://www.atsb.gov.au/sites/default/files/2022-12/AE-2014-054_MH370-Definition%20of%20Underwater%20Search%20Areas_3Dec2015.pdf#page=14). Applying this later condition changes what is inferred about 00:11.
- Ocean drift, Pléiades, antenna gain, hydroacoustics and search non-detection are disabled. No end-of-flight or impact location is inferred. Missing search witnesses remain unresolved.

## Verification and time

The searches completed {summary['search_profiles']} optimization profiles and approximately {summary['search_evaluations']:,} canonical trajectory evaluations. Summed elapsed time for the search batches and verification was {runtime/60:.1f} minutes, with up to four search workers. Recorded child CPU time for the searches was {cpu/60:.1f} CPU-minutes. The largest individual replay process used about {runtimes['verification']['maximum_child_rss_kib']/1024:.0f} MiB; four concurrent replay processes required approximately four times that amount. Build and engineering time are additional.

All {len(rows)} candidate witnesses passed replays at the original integration steps, half steps and quarter steps. The largest coarse-to-quarter endpoint shift was {max(separations):.2f} NM and the largest exhaustion-time shift was {max(time_diffs):.1f} seconds. Figures use the fine replay. The original run also has a separately implemented SATCOM comparison in `independent-satcom-check.json`; this external audit is additional to the reproducible runner checks. These checks do not validate the unknown behavioural prior or certify aircraft performance outside the source models.

{fuel_note}

## Implementation recommendation

Use eight direction changes as the initial working representation and retain sixteen as a required sensitivity comparison. Keep cruise adjustment allowances separate: start with four speed and four altitude target changes and test eight of each. These are computational starting points, not assertions about pilot behaviour. Report the number and total amount of turning, speed adjustment and climb/descent separately; an operationally simple step-climb policy must not be penalized as though it were erratic flying. A scalar preference for simplicity remains an explicit behavioural prior.

A stable PDF is still unproved. The next bounded task is to demonstrate recovery and stable probabilities on known-flight and synthetic controls with this representation. Finding trajectories cheaply does not establish their relative probability. The 30-minute pre-analysis allowance was respected; sampler escalation remains conditional on numerical support.

## Reproduction

Use Python with NumPy, SciPy and Matplotlib installed; exact versions and input/code hashes are in the manifest. From the project root, this command runs the bounded search and witness verification into an empty directory:

```bash
python crates/controls/flight_assumptions.py --output /absolute/path/to/empty-output
```

The control builds the central runner, calls its `replay-flight-trajectory` command and stops numerical requests after 30 minutes. Generate the plots and this report from its artifacts:

```bash
python crates/reporting/scripts/flight_assumption_report.py /absolute/path/to/output
```

To check saved witnesses without repeating optimization, use `--verify-existing` with the control command. The original search used the same replay implementation in an isolated temporary harness; all retained geographic witnesses were subsequently reproduced through the integrated central runner. No product scientific equations were replaced by the optimizer.
'''
    (output/'report.md').write_text(text)
    print(json.dumps(summary,indent=2))

def witness_assumption_audit(original, output, rows):
    """Summarize stored diagnostics and descriptive path complexity."""
    import csv,hashlib,tomllib
    nominal=[r for r in rows if r['request'].get('flow_scale',1.)==1.]
    records=[]
    for row in nominal:
        trace=[p for p in row['result']['trace'] if p['aircraft']['time']>=1425.]
        aircraft=[p['aircraft'] for p in trace]
        distance=sum(distance_nm(a['position'],b['position']) for a,b in zip(aircraft,aircraft[1:]))
        direct=distance_nm(aircraft[0]['position'],aircraft[-1]['position'])
        heading=np.array([p['heading_true_deg'] for p in trace]);altitude=np.array([p['altitude'] for p in aircraft]);mach=np.array([p['mach'] for p in trace])
        modes=[row['request']['initial_mode']]+[c['mode'] for c in sorted(row['request']['commands'],key=lambda c:c['time']) if 'control' in c]
        diagnostic=row['result']['diagnostics']
        records.append({'witness':len(records),'latitude_0011_deg':row['metrics']['latitude'],'longitude_0011_deg':row['metrics']['longitude'],
                        'direction_settings':row['command_counts']['control'],'speed_settings':row['command_counts']['mach'],'altitude_settings':row['command_counts']['altitude'],
                        'navigation_mode_changes':sum(a!=b for a,b in zip(modes,modes[1:])),
                        'sampled_absolute_heading_change_deg':float(np.abs((np.diff(heading)+180)%360-180).sum()),
                        'sampled_path_length_nm':distance,'path_to_direct_distance_ratio':distance/direct,
                        'sampled_total_climb_ft':float(np.maximum(np.diff(altitude),0).sum()),
                        'sampled_total_descent_ft':float(np.maximum(-np.diff(altitude),0).sum()),
                        'sampled_absolute_mach_change':float(np.abs(np.diff(mach)).sum()),
                        'outside_source_fuel_domain_seconds':diagnostic['fuel_outside_martin_domain_seconds'],
                        'has_thrust_proxy_extrapolation':diagnostic['powered_thrust_proxy_extrapolation_segments']>0})
    inside=[r for r in records if r['outside_source_fuel_domain_seconds']==0.]
    latitude_span=lambda data:[min(r['latitude_0011_deg'] for r in data),max(r['latitude_0011_deg'] for r in data)]
    allowance_spans=[]
    for cap in [1,2,4,8,16]:
        subset=[r for r in records if r['direction_settings']<=cap and not r['speed_settings'] and not r['altitude_settings']]
        allowance_spans.append({'maximum_direction_settings':cap,'examples':len(subset),'latitude_span_deg':latitude_span(subset)})
    config=ROOT/'configs/mh370-broad-powered-flight-diagnostic.toml';cfg=tomllib.loads(config.read_text())
    audit={'status':'Descriptive audit of found nominal-fuel examples, not complete physical support or a posterior',
           'nominal_examples':len(records),'latitude_span_deg':latitude_span(records),
           'examples_without_source_fuel_domain_exit':len(inside),'latitude_span_without_source_fuel_domain_exit_deg':latitude_span(inside),
           'examples_with_thrust_proxy_extrapolation':sum(r['has_thrust_proxy_extrapolation'] for r in records),
           'steady_cruise_direction_allowance_spans':allowance_spans,
           'limits':cfg['model']['limits'],'fuel_model':cfg['model']['fuel_model'],
           'fuel_anchor':cfg['fuel_anchor'],'powered_feasibility':cfg['model']['powered_feasibility'],
           'exhaustion_to_r600_condition_seconds':[30.,300.],
           'coherence_measure_note':'Descriptive coordinates are kept separate. No weighted simplicity score or pilot-behaviour prior is inferred. Trace-derived totals are discretized approximations.',
           'input_sha256':{str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in [original/'verified-witnesses.jsonl',output/'cruise-exploration/verified-witnesses.jsonl',config,pathlib.Path(__file__)]}}
    (output/'witness-assumption-audit.json').write_text(json.dumps(audit,indent=2))
    with (output/'web/coherence-examples.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    fig,ax=plt.subplots(figsize=(5.5,4.6))
    scatter=ax.scatter([r['latitude_0011_deg'] for r in records],[r['path_to_direct_distance_ratio'] for r in records],c=[r['direction_settings'] for r in records],s=22,cmap='viridis',vmin=1,vmax=16,alpha=.75)
    ax.axhline(1,color='#777',ls='--',lw=.8);ax.set(xlabel='00:11 endpoint latitude (degrees)',ylabel='Post-18:25 path length /\ndirect start-to-end distance');ax.grid(alpha=.15)
    bar=fig.colorbar(scatter,ax=ax,pad=.02);bar.set_label('Direction target settings');bar.set_ticks([1,2,4,8,16]);fig.tight_layout();fig.savefig(output/'web/coherence-comparison.svg');fig.savefig(output/'web/coherence-comparison.png',dpi=140);plt.close(fig)
    north,south=-audit['latitude_span_deg'][1],-audit['latitude_span_deg'][0]
    return f'''<section id="assumptions"><h2>The assumptions behind the broad examples</h2><p>The {len(records)} nominal-fuel examples reach approximately {north:.0f}–{south:.0f}°S at 00:11. This is a span between found examples; it is neither a complete outer boundary nor a claim that every intervening location is feasible. The flight before 18:25 keeps its starting cruise targets, and initial vertical speed is zero.</p><p>Mach 0.30–0.87 and altitude 500–43,000 ft are declared outer limits, with stall margin, 330-knot calibrated airspeed, bank, roll and climb/descent constraints also applied. These do not constitute a calibrated Boeing 777 performance model. All {len(records)} paths use the thrust approximation beyond the available audited climb-trajectory coverage; that coverage itself is not engine validation.</p><p>The fuel model extends a long-range-cruise spreadsheet using declared Mach, altitude, bank and climb corrections. {len(records)-len(inside)} examples leave the source table’s domain, but the other {len(inside)} still span approximately {-audit['latitude_span_without_source_fuel_domain_exit_deg'][1]:.0f}–{-audit['latitude_span_without_source_fuel_domain_exit_deg'][0]:.0f}°S. Staying within that table’s domain does not establish all its assumptions. The calculated 18:28 fuel anchor is imposed, fuel-flow scale is nominal, and the 30–300-second exhaustion-to-R600 condition permits approximately 00:14:29–00:18:59 exhaustion. It is not a measured “00:17:30 ± x” distribution.</p></section><section id="coherence"><h2>Describing trajectory coherence without assigning intent</h2><p>The plot compares route length with direct distance between the same post-18:25 start and 00:11 end. A larger ratio means more detour. Colour records direction settings. A long detour could still be deliberate; it is not made less probable by this plot.</p><a href="coherence-comparison.svg"><img src="coherence-comparison.svg" alt="Descriptive path detour and direction-setting counts by 00:11 endpoint"></a><p>Direction settings, navigation-mode switches, accumulated heading change, total climb/descent and Mach variation remain separate descriptive measures. Routine step climbs are not automatically penalized like direction reversals. Any rule preferring smaller values would be an explicit behavioural hypothesis, to be compared with the broader family. <a href="coherence-examples.csv">Inspect all descriptive metrics</a>.</p></section>'''


def progress_report(original, output):
    """Render current control artifacts without treating witnesses as samples."""
    import datetime, hashlib
    web=output/'web';web.mkdir(parents=True,exist_ok=True)
    source=output/'cruise-exploration'
    profiles=[json.loads(x) for x in (source/'cruise-exploration.jsonl').read_text().splitlines()]
    verified=[json.loads(x) for x in (source/'verified-witnesses.jsonl').read_text().splitlines()]
    old=[json.loads(x) for x in (original/'verified-witnesses.jsonl').read_text().splitlines()]
    cruise=json.loads((source/'cruise-exploration-summary.json').read_text())
    exact=json.loads((output/'exact-replay-summary.json').read_text())
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans','Arial','Helvetica','sans-serif'],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    assumptions=witness_assumption_audit(original,output,old+verified)
    machs=sorted(set(r['request']['initial'][3] for r in profiles));alts=sorted(set(r['request']['initial'][4] for r in profiles))
    counts=np.zeros((len(alts),len(machs)),int);attempts=counts.copy()
    for r in profiles:attempts[alts.index(r['request']['initial'][4]),machs.index(r['request']['initial'][3])]+=1
    for r in verified:counts[alts.index(r['request']['initial'][4]),machs.index(r['request']['initial'][3])]+=1
    fig,ax=plt.subplots(figsize=(5.4,4.1));ax.imshow(counts,cmap='Blues',origin='lower',vmin=0,vmax=max(1,counts.max()),aspect='auto')
    for i in range(len(alts)):
        for j in range(len(machs)):ax.text(j,i,f'{counts[i,j]} / {attempts[i,j]}',ha='center',va='center',color='white' if counts[i,j]>counts.max()*.55 else '#243746',fontsize=11)
    ax.set(xticks=range(len(machs)),xticklabels=[f'{x:.2f}' for x in machs],yticks=range(len(alts)),yticklabels=[f'{x/1000:g}' for x in alts],xlabel='Fixed initial Mach number',ylabel='Fixed initial altitude (1,000 ft)');fig.tight_layout();fig.savefig(web/'cruise-grid.svg');plt.close(fig)
    groups=[]
    for directions in [1,2,4,8,16]:
        subset=[r for r in old+verified if r['request'].get('flow_scale',1)==1 and r['command_counts']['control']<=directions and r['command_counts']['mach']==0 and r['command_counts']['altitude']==0]
        groups.append((f'Up to {directions} direction; steady cruise',subset))
    for changes in [2,4,8]:
        subset=[r for r in old+verified if r['request'].get('flow_scale',1)==1 and r['command_counts']['control']<=8 and r['command_counts']['mach']<=changes and r['command_counts']['altitude']<=changes]
        groups.append((f'8 direction; up to {changes} speed / altitude',subset))
    fig,ax=plt.subplots(figsize=(5.5,6.5))
    for i,(label,rows) in enumerate(groups):
        ax.text(-42,i-.28,label,fontsize=10);ax.scatter([r['metrics']['latitude'] for r in rows],[i+.1]*len(rows),marker='|',s=85,lw=1,color='#315b80' if i<5 else '#1c877d')
    ax.set(xlim=(-42.5,-10),ylim=(len(groups)-.3,-.7),yticks=[],xlabel='00:11 endpoint latitude (degrees)');ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(web/'support-comparison.svg');plt.close(fig)
    runs=[]
    for p in sorted((output/'command-sampler').glob('**/summary.json')):
        d=json.loads(p.read_text());h=d.get('history',[])
        if not h:continue
        runs.append({'path':str(p.relative_to(output)),'counts':d.get('counts'),'seed':d['seed'],'seconds':d['elapsed_s'],'temperature':h[-1]['temperature'],'mutation_acceptance':h[-1]['mutation_acceptance'],'roots':h[-1]['root_count'],'log_normalizer':h[-1]['log_normalizer']})
    reference=json.loads((output/'sampler-reference-local-mixture/summary.json').read_text())
    normalization_path=output/'sampler-normalization-control/summary.json'
    normalization=json.loads(normalization_path.read_text()) if normalization_path.exists() else []
    timestamp=datetime.datetime.now(datetime.timezone.utc).strftime('%d %B %Y, %H:%M UTC')
    manifest={'updated_utc':timestamp,'cruise_profiles':len(profiles),'cruise_verified':len(verified),'sampler_runs':runs,'broad_posterior_status':'not validated','reference_probability':reference['positive_mode_fraction'],'normalization_controls_passed':bool(normalization) and all(r['passed'] for r in normalization)}
    (web/'results.json').write_text(json.dumps(manifest,indent=2))
    def panel(name,title,caption):return f'<section><h2>{escape(title)}</h2><p>{escape(caption)}</p><a href="{name}.svg"><img src="{name}.svg" alt="{escape(title)}"></a><a href="{name}.svg">Open full-size plot ↗</a></section>'
    grid=panel('cruise-grid','Wider starting speed and altitude',f'Verified examples / attempted fits at each fixed starting setting. Each cell combines different manoeuvre allowances and target endpoints. {len(verified)} examples survived finer replay. Zero means unresolved by this search; the counts are not probabilities. Initial cruise remains fixed before 18:25. The declared continuous bounds are Mach 0.30–0.87 and 500–43,000 ft; this is a sparse check within them.')
    support=panel('support-comparison','Endpoints with increasing freedom','Each mark is a verified example. Smaller allowances are included in the larger ones. Mark density is not probability, and gaps remain unresolved. Cruise changes and direction changes are counted separately. This combines the original examples and the broader cruise check at the nominal fuel-flow multiplier.')
    stability_path=output/'command-sampler/residual-drift-eight-settings/numerical-assessment.json'
    stability=''
    if stability_path.exists():
        assessment=json.loads(stability_path.read_text());fig,ax=plt.subplots(figsize=(5.5,4.1))
        for run,color in zip(assessment['runs'],['#315b80','#bf781e']):
            data=np.load(stability_path.parent/('seed-'+str(run['seed']))/'particles.npz')['data'];latitude=np.sort(data[:,0]);ax.step(latitude,np.arange(1,len(latitude)+1)/len(latitude),where='post',color=color,label=f"{len(latitude)} particles; {run['elapsed_s']/60:.1f} minutes")
        ax.set(xlabel='00:11 endpoint latitude (degrees)',ylabel='Fraction of numerical population',ylim=(0,1.02));ax.grid(alpha=.18);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(web/'sampler-disagreement.svg');plt.close(fig)
        stability='<p>The two broader runs disagree in their tails: about 2% versus 14% of their numerical populations lie north of 35°S. Larger broad ensembles have stopped. The near-agreement of their central locations does not validate either probability distribution. The separate known-flight repeat below also fails.</p><a href="sampler-disagreement.svg"><img src="sampler-disagreement.svg" alt="Independent numerical populations with disagreeing north tails"></a>'
    known_path=output/'command-sampler/mh371-flexible-control/numerical-assessment.json'
    if known_path.exists():
        known=json.loads(known_path.read_text());fig,ax=plt.subplots(figsize=(5.5,4.1))
        for run,color in zip(known['runs'],['#315b80','#bf781e']):
            latitude=np.sort(np.load(known_path.parent/('seed-'+str(run['seed']))/'particles.npz')['data'][:,0]);ax.step(latitude,np.arange(1,len(latitude)+1)/len(latitude),where='post',color=color,label=f"{len(latitude)} particles; {run['elapsed_s']/60:.1f} minutes")
        ax.axvline(known['withheld_truth_position_deg'][0],color='#b8493d',ls='--',label='Withheld known position');ax.set(xlabel='Known-flight endpoint latitude (degrees north)',ylabel='Fraction of numerical population',ylim=(0,1.02));ax.grid(alpha=.18);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(web/'known-flight-disagreement.svg');plt.close(fig)
        stability+='<p>The known-flight repeat also fails distribution agreement. Both runs place the known aircraft within a broad span, but their population shapes differ sharply. The actual later positions were reserved for scoring after inference. Neither run is a validated probability estimate.</p><a href="known-flight-disagreement.svg"><img src="known-flight-disagreement.svg" alt="Known-flight numerical populations disagree despite a broadly covered truth"></a>'
    coherent_path=output/'command-sampler/coherent-conditional/numerical-assessment.json'
    if coherent_path.exists():
        coherent=json.loads(coherent_path.read_text());fig,ax=plt.subplots(figsize=(5.5,4.1))
        for run,color in zip(coherent['runs'],['#315b80','#bf781e']):
            latitude=np.sort(np.load(coherent_path.parent/('seed-'+str(run['seed']))/'particles.npz')['data'][:,0]);ax.step(latitude,np.arange(1,len(latitude)+1)/len(latitude),where='post',color=color,label=f"{len(latitude)} particles; {run['elapsed_s']/60:.1f} minutes")
        ax.set(xlabel='00:11 endpoint latitude (degrees)',ylabel='Fraction of numerical population',ylim=(0,1.02));ax.grid(alpha=.18);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(web/'coherent-repeat.svg');plt.close(fig)
        south=-min(r['latitude_quantiles_05_50_95'][0] for r in coherent['runs']);north=-max(r['latitude_quantiles_05_50_95'][-1] for r in coherent['runs'])
        stability+=f'<h3>A simpler conditional model</h3><p>Allowing one direction setting with constant Mach and altitude gives much closer independent repeats. Both place their middle 90% within approximately {north:.1f}–{south:.1f}°S. This is a conditional numerical result under the stated fuel and flight priors, not a measured width of the general solution space. The full distributions still differ by up to about {100*coherent["latitude_empirical_cdf_max_difference"]:.0f} percentage points; categorical mode weights also need stronger validation.</p><a href="coherent-repeat.svg"><img src="coherent-repeat.svg" alt="More consistent independent populations for the simple conditional flight model"></a>'
    synthetic_path=output/'command-sampler/synthetic-coherent-control/numerical-assessment.json'
    if synthetic_path.exists():
        synthetic=json.loads(synthetic_path.read_text())
        stability+='<p>A separate noisy synthetic flight also recovers its withheld endpoint within both runs’ central 90% coordinate spans, with closely agreeing distributions and normalizers. This uses the same forward equations to generate and fit the data, so it checks inference and data handling, not physical-model accuracy or coverage across many flights. The independent flexible known-flight failure above remains unresolved.</p>'
    update_evidence_panels(output)
    update_terminal_panels(output)
    update_final_bfo_panel(output)
    update_hypothesis_path_panels(output)
    update_source_comparison_panels(output)
    from flight_analysis_results import write_results
    outcome=write_results(original,output)
    additional=''
    terminal_directory='terminal-final-contact' if (output/'terminal-final-contact/summary.json').exists() else 'terminal-examples'
    for directory,title in [('antenna-comparison','Conditional antenna comparison'),('final-bfo-comparison','Final BFO check'),(terminal_directory,'End-of-flight examples'),('evidence-comparison','Other evidence and search planning')]:
        p=output/directory/'report-fragment.html'
        if p.exists():additional+=p.read_text()
    run_rows=''.join(f'<tr><td>{escape(str(r["counts"]))}</td><td>{r["seed"]}</td><td>{r["seconds"]/60:.1f}</td><td>{100*r["mutation_acceptance"]:.1f}%</td></tr>' for r in runs)
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 — Overnight analysis</title><style>
    *{{box-sizing:border-box}}body{{margin:0;background:#f2f5f6;color:#243746;font:16px/1.55 system-ui,-apple-system,sans-serif}}main{{max-width:760px;margin:auto;padding:26px 14px 50px}}h1{{font-size:clamp(1.7rem,6vw,2.4rem);line-height:1.15}}h2{{font-size:1.25rem;line-height:1.3}}a{{color:#145e87;text-underline-offset:3px}}section{{background:white;border:1px solid #dce4e8;border-radius:12px;padding:20px 16px;margin:20px 0}}img{{width:100%;height:auto}}.note{{border-left:4px solid #bf781e;background:#fff8ee;padding:12px 16px}}small{{color:#526571}}table{{border-collapse:collapse;width:100%;font-size:.85rem}}td,th{{text-align:left;padding:8px 4px;border-bottom:1px solid #dce4e8}}details{{margin:16px 0}}summary{{cursor:pointer;font-weight:600}}@media(max-width:450px){{main{{padding:20px 10px}}section{{padding:16px 10px}}}}
    </style></head><body><main><a href="../">← Original comparison plots</a><h1>Overnight analysis</h1><small>Updated {escape(timestamp)}</small><p>Progress toward a broader, reliable trajectory estimate and explicit comparisons with additional evidence.</p><div class="note"><strong>A broad probability map is not yet validated.</strong> The flight plots show feasible examples under the stated models through 00:11. Broad flight sampling has stopped after failed independent-run checks; the two-hour sampling cap will not be exceeded. Terminal illustrations also fail the final-BFO comparison described below.</div>{outcome}<section><h2>What is established so far?</h2><p>The changing-flight fuel-boundary defect is repaired. All 158 original examples replay through the repaired boundary, with exhaustion times within 0.0011 seconds of the earlier fine timing check. That agreement measures numerical accuracy; it does not imply that actual fuel exhaustion is known that precisely.</p><p>The new cruise search attempted {len(profiles)} fits in {cruise['elapsed_s']/60:.1f} minutes and retained {len(verified)} examples after finer replay. It broadens the tested flight assumptions without assigning probabilities to the examples.</p></section>{assumptions}{grid}{support}<section><h2>Probability sampling: broad validation failed</h2><p>The revised sampler recovers {reference['positive_mode_fraction']:.3f} for an independently calculable probability of 0.700, despite a deliberately biased guide. {'All four additional checks of continuous and discrete probabilities passed.' if manifest['normalization_controls_passed'] else 'Further normalization checks are in progress.'} These checks verify parts of the sampling mathematics; they do not establish that all feasible flight families have been explored.</p>{stability}<details><summary>Completed numerical pilots</summary><p>Counts are fixed labelled direction, speed and altitude settings. These are conditional experiments, not a probability distribution over all counts up to a maximum. Acceptance is a movement diagnostic, not a sufficient convergence test.</p><table><thead><tr><th>Settings</th><th>Seed</th><th>Minutes</th><th>Moves accepted</th></tr></thead><tbody>{run_rows}</tbody></table></details></section>{additional}<footer><p><a href="results.json">Machine-readable progress</a>. Later evidence is included only where an explicitly labelled comparison appears above. No search-location recommendation follows from the witness plots.</p></footer></main></body></html>'''
    import re
    from html import unescape
    def anchor(match):
        title=match.group(1);name=re.sub('[^a-z0-9]+','-',unescape(title).lower()).strip('-')
        return f'<section id="{name}"><h2>{title}</h2>'
    page=re.sub(r'<section><h2>([^<]+)</h2>',anchor,page)
    navigation='<nav aria-label="Report sections" style="display:flex;gap:12px;flex-wrap:wrap;margin:18px 0">'+''.join(f'<a href="#{name}">{label}</a>' for name,label in [('results-and-decision','Results'),('assumptions','Assumptions'),('coherence','Coherence'),('probability-sampling-broad-validation-failed','Flight sampling'),('conditional-antenna-comparison','Antenna'),('final-bfo','Final BFO'),('end-of-flight','End of flight'),('kadri-s-original-preferred-event','Kadri'),('recovered-debris-and-ocean-drift','Ocean drift'),('godfrey-s-proposed-route','Godfrey'),('what-can-7-500-km-of-search-achieve','Search')])+'</nav>'
    first_section='<section id="results-and-decision">' if outcome else '<section id="what-is-established-so-far">'
    page=page.replace(first_section,navigation+first_section).replace('<img src=','<img loading="lazy" src=')
    (web/'index.html').write_text(page)
    link=original/'web/overnight'
    if not link.exists():link.symlink_to(web,target_is_directory=True)
    index=original/'web/index.html';old_page=index.read_text()
    if 'href="overnight/"' not in old_page:index.write_text(old_page.replace('<nav aria-label="Plots">','<nav aria-label="Plots"><a href="overnight/">Overnight analysis</a>'))
    print(web/'index.html')

def update_evidence_panels(output):
    """Create conditional comparison panels solely from completed artifacts."""
    import csv
    web=output/'web'
    directory=output/'antenna-comparison'
    if (directory/'summary.json').exists():
        models=[('full-compensation','#315b80','Full compensation'),('partial-compensation','#bf781e','Partial compensation'),('no-compensation','#1c877d','No compensation')]
        fig,ax=plt.subplots(figsize=(5.5,4.4));statistics=[];table=[]
        for name,color,label in models:
            rows=[json.loads(x) for x in (directory/(name+'-examples.jsonl')).read_text().splitlines()]
            scores=np.array([r['antenna']['alternatives'][1]['log_likelihood'] for r in rows]);latitude=np.array([r['endpoint']['position']['latitude'] for r in rows]);relative=np.exp(scores-scores.max())
            ax.scatter(latitude,relative,s=12,color=color,alpha=.6,label=label)
            statistics.append({'model':name,'fixed_pitch_deg':3,'log_likelihood_spread_among_witnesses':float(np.ptp(scores)),'largest_likelihood_ratio_among_witnesses':float(np.exp(np.ptp(scores)))})
            for r,s,v in zip(rows,scores,relative):table.append({'conditional_model':name,'witness':r['witness'],'latitude_deg':r['endpoint']['position']['latitude'],'longitude_deg':r['endpoint']['position']['longitude'],'fixed_pitch_nose_up_deg':3.,'log_likelihood':float(s),'relative_to_best_tested_witness':float(v)})
        ax.set(yscale='log',ylim=(.05,1.2),xlabel='00:11 endpoint latitude (degrees)',ylabel='Relative antenna likelihood\n(best tested example = 1)');ax.grid(alpha=.16);ax.legend(fontsize=9,loc='lower right');fig.tight_layout();fig.savefig(web/'antenna-comparison.svg');plt.close(fig)
        with (directory/'relative-scores.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=table[0]);writer.writeheader();writer.writerows(table)
        (directory/'likelihood-comparison.json').write_text(json.dumps(statistics,indent=2))
        n=len(rows);ratio=statistics[-1]['largest_likelihood_ratio_among_witnesses']
        fragment=f'''<section><h2>Conditional antenna comparison</h2><p>With full gain compensation, the antenna model provides almost no discrimination among these {n} paths. With no compensation, its largest likelihood ratio among the tested examples is about {ratio:.0f}:1 at an assumed 3° nose-up pitch.</p><p>These are relative scores for the antenna evidence alone, not geographic probabilities. The comparison uses the existing unverified antenna reconstruction, five power observations, a fixed reference calibration and independent 1.72 dB observation errors. Uncertainty in the shared reference calibration has not been marginalized. Heading and bank come from each simulated path; 0°, 3° and 6° pitch alternatives are retained in the artifacts. A valid baseline distribution is still needed before a PDF can be updated.</p><a href="antenna-comparison.svg"><img src="antenna-comparison.svg" alt="Relative antenna likelihood under three compensation alternatives"></a><a href="antenna-comparison.svg">Open full-size plot ↗</a></section>'''
        (directory/'report-fragment.html').write_text(fragment)
    directory=output/'terminal-examples'
    if (directory/'summary.json').exists() and not (output/'terminal-final-contact/summary.json').exists():
        summary=json.loads((directory/'summary.json').read_text());rows=[json.loads(x) for x in (directory/'impacts.jsonl').read_text().splitlines()]
        fig,ax=plt.subplots(figsize=(5.5,4.4));statistics=[]
        for family,color,label in [('openap_v2_6_0_attached_flow','#315b80','Current public polar'),('openap_published2020_attached_flow','#bf781e','Published 2020 polar')]:
            selected=[r for r in rows if r['aerodynamic_family']==family];time=np.array([(r['impact']['point']['time']-22660.416)/60 for r in selected]);distance=np.array([r['impact']['point']['displacement_from_last_contact'] for r in selected]);ax.scatter(time,distance,s=2,alpha=.12,color=color,label=label)
            statistics.append({'family':family,'impact_examples':len(selected),'minutes_relative_to_r600_span':[float(time.min()),float(time.max())],'displacement_from_exhaustion_nm_span':[float(distance.min()),float(distance.max())],'impact_ground_speed_m_s_span':[min(r['impact']['ground_speed'] for r in selected),max(r['impact']['ground_speed'] for r in selected)],'kinetic_energy_j_span':[min(r['impact']['kinetic_energy'] for r in selected),max(r['impact']['kinetic_energy'] for r in selected)]})
        ax.axvline(0,color='#8f3631',lw=1,ls='--');ax.set(xlabel='Impact time relative to 00:19:29 (minutes)',ylabel='Displacement from fuel exhaustion (NM)');ax.grid(alpha=.15);ax.legend(fontsize=9,markerscale=4);fig.tight_layout();fig.savefig(web/'terminal-time-range.svg');plt.close(fig)
        (directory/'impact-ranges.json').write_text(json.dumps(statistics,indent=2))
        fragment=f'''<section><h2>End-of-flight examples</h2><p>The paired public aerodynamic alternatives generated {len(rows):,} impact examples from {summary['witnesses']} source paths. Time, displacement and velocity are calculated together. The cloud is not a probability map: its density reflects the chosen source paths and the declared lift / bank sampling design.</p><p>Displacement is measured from fuel exhaustion. Points to the left of the dashed line impact before the R600 contact; no final-contact likelihood has yet been applied. Weather-domain exits and model-envelope exits are retained separately as unresolved. The powered segment keeps its last command after 00:11, and the terminal model holds its selected lift coefficient and bank constant. These public attached-flow approximations do not establish all possible post-stall or compressible flight. Body pitch, breakup and acoustic coupling are unresolved.</p><a href="terminal-time-range.svg"><img src="terminal-time-range.svg" alt="Joint time and displacement for conditional impact examples"></a><a href="terminal-time-range.svg">Open full-size plot ↗</a></section>'''
        (directory/'report-fragment.html').write_text(fragment)


def update_terminal_panels(output):
    """Report final-contact comparisons without manufacturing source weights."""
    directory=output/'terminal-final-contact';web=output/'web'
    if not (directory/'summary.json').exists():return
    summary=json.loads((directory/'summary.json').read_text())
    rows=[json.loads(line) for line in (directory/'impacts.jsonl').open()]
    baseline=output/'terminal-checkpoint-rounding-control'
    if baseline.exists():
        import hashlib
        previous={(r['witness'],r['example']):r for r in (json.loads(line) for line in (baseline/'impacts.jsonl').open())}
        changes=[]
        for row in rows:
            old=previous.get((row['witness'],row['example']))
            if old is None:continue
            a,b=old['impact'],row['impact']
            before,after=old['final_contact_bto'],row['final_contact_bto']
            residual_change=(abs(before[0]['fit']['bto']['predicted']-after[0]['fit']['bto']['predicted'])
                             if before and after and before[0]['status']==after[0]['status']=='bto_geometry_scored' else 0.)
            changes.append((abs(a['point']['time']-b['point']['time']),distance_nm(a['point']['position'],b['point']['position']),abs(a['kinetic_energy']/b['kinetic_energy']-1),residual_change))
        path=output/'terminal-timestamp-correction.json';audit=json.loads(path.read_text())
        old_manifest=json.loads((baseline/'run-manifest.json').read_text());new_manifest=json.loads((directory/'run-manifest.json').read_text())
        without_checkpoints=lambda cases:[{k:v for k,v in c.items() if k!='checkpoints_relative_s'} for c in cases]
        audit.update({'corrected_runtime_s':summary['elapsed_s'],'paired_impact_examples':len(changes),
                      'impact_outcome_counts_unchanged':summary['outcome_counts']==json.loads((baseline/'summary.json').read_text())['outcome_counts'],
                      'physical_control_cases_unchanged':without_checkpoints(old_manifest['terminal_cases'])==without_checkpoints(new_manifest['terminal_cases']),
                      'maximum_impact_time_change_s':max(r[0] for r in changes),
                      'maximum_impact_position_change_nm':max(r[1] for r in changes),
                      'maximum_relative_impact_energy_change':max(r[2] for r in changes),
                      'maximum_r600_predicted_bto_change_us':max(r[3] for r in changes),
                      'corrected_manifest_sha256':hashlib.sha256((directory/'run-manifest.json').read_bytes()).hexdigest()})
        if not audit['physical_control_cases_unchanged']:raise ValueError('Timing control changed physical cases')
        path.write_text(json.dumps(audit,indent=2))
    weather_unresolved=sum(r['examples'] for r in summary['outcome_counts'] if r['outcome']=='terminal_weather_domain_unresolved')
    envelope_unresolved=sum(r['examples'] for r in summary['outcome_counts'] if 'declared_envelope_exit' in r['outcome'])
    trial_unresolved=sum(r['examples'] for r in summary['outcome_counts'] if r['outcome']=='terminal_integration_trial_unresolved')
    pre_contact=sum(r['examples'] for r in summary['final_contact_counts'] if r['outcome'].startswith('impact_before_airborne_contact'))
    families=[('openap_v2_6_0_attached_flow','#315b80','Current public polar'),('openap_published2020_attached_flow','#bf781e','Published 2020 polar')]
    statistics=[];panels={name:plt.subplots(2,1,figsize=(5.5,6.6),sharex=True) for name in ['terminal-time-range','terminal-impact-velocity']}
    fig_acoustic,axes_acoustic=plt.subplots(2,1,figsize=(5.5,6.6),sharex=True)
    for j,(family,color,label) in enumerate(families):
        selected=[r for r in rows if r['aerodynamic_family']==family]
        bto=np.array([r['final_contact_bto'][0].get('residual_standard_deviations',np.nan) if r['final_contact_bto'] else np.nan for r in selected]);compatible=np.isfinite(bto)&(abs(bto)<=3)
        times=np.array([(r['impact']['point']['time']-22660.416)/60 for r in selected]);distances=np.array([r['impact']['point']['displacement_from_last_contact'] for r in selected]);horizontal=np.array([r['impact']['ground_speed'] for r in selected]);down=np.array([-r['impact']['vertical_speed'] for r in selected])
        energy=np.array([r['impact']['kinetic_energy'] for r in selected]);vertical_energy=np.array([r['impact']['vertical_kinetic_energy'] for r in selected]);latitude=np.array([r['impact']['point']['position']['latitude'] for r in selected]);angles=np.array([r['impact']['impact_angle'] for r in selected])
        for name,x,y in [('terminal-time-range',times,distances),('terminal-impact-velocity',horizontal,down)]:
            ax=panels[name][1][j];ax.scatter(x,y,s=3,alpha=.2,color='#999',rasterized=True,label='All resolved examples');ax.scatter(x[compatible],y[compatible],s=3,alpha=.18,color=color,rasterized=True,label='R600 BTO residual within ±3 SD');ax.set_title(label,fontsize=11,loc='left');ax.grid(alpha=.15)
            if name=='terminal-time-range':ax.axvline(0,color='#8f3631',lw=1,ls='--')
        for station,ax in zip(['H01W','H08S'],axes_acoustic):
            arrivals=[next(a for a in r['acoustic_arrivals'] if a['station_name']==station)['prediction']['arrival_time_s'] for r in selected]
            # Relative-time origin 18:01:49; 21,491 s is midnight on 8 March.
            lo=np.array([(a['minimum']-21491.)/60 for a in arrivals]);hi=np.array([(a['maximum']-21491.)/60 for a in arrivals])
            ax.scatter(latitude[compatible],lo[compatible],s=2,alpha=.12,color=color,rasterized=True,label=label);ax.scatter(latitude[compatible],hi[compatible],s=2,alpha=.12,color=color,rasterized=True)
            ax.set_title(station+' predicted arrival limits',fontsize=11,loc='left');ax.grid(alpha=.15)
            if station=='H01W':ax.axhline(54.5,color='#b8493d',ls='--',lw=1,label='Kadri preferred arrival 00:54:30' if j==0 else None)
        span=lambda a:[float(np.min(a[compatible])),float(np.max(a[compatible]))]
        statistics.append({'family':family,'impact_examples':len(selected),'examples_within_3_bto_sd':int(compatible.sum()),'r600_powered_in_declared_apu_model':int(sum(bool(ok) and r['final_contact_bto'][0].get('satcom_power_available_in_declared_apu_model',False) for r,ok in zip(selected,compatible))),'condition':'Illustrative absolute R600 BTO residual <=3 SD; Gaussian likelihood is not a hard exclusion. No source-state probabilities.','minutes_after_r600_span':span(times),'displacement_from_exhaustion_nm_span':span(distances),'impact_latitude_deg_span':span(latitude),'ground_speed_m_s_span':span(horizontal),'downward_speed_m_s_span':span(down),'ground_relative_impact_angle_deg_span':span(angles),'kinetic_energy_j_span':span(energy),'vertical_kinetic_energy_j_span':span(vertical_energy)})
    for name,(fig,axes) in panels.items():
        for ax in axes:ax.set_ylabel('Displacement from exhaustion (NM)' if name=='terminal-time-range' else 'Downward velocity (m/s)')
        axes[-1].set_xlabel('Impact time after 00:19:29 (minutes)' if name=='terminal-time-range' else 'Horizontal ground velocity (m/s)')
        axes[0].legend(fontsize=7,markerscale=4,loc='upper left');fig.tight_layout();fig.savefig(web/(name+'.svg'),dpi=180);plt.close(fig)
    for ax in axes_acoustic:ax.set_ylabel('Arrival time after 00:00 (minutes)')
    axes_acoustic[-1].set_xlabel('Impact latitude (degrees)');axes_acoustic[0].legend(fontsize=7,markerscale=4);fig_acoustic.tight_layout();fig_acoustic.savefig(web/'terminal-acoustic-timing.svg',dpi=180);plt.close(fig_acoustic)
    (directory/'impact-ranges.json').write_text(json.dumps(statistics,indent=2))
    refinement=output/'terminal-refinement/summary.json'
    check=json.loads(refinement.read_text()) if refinement.exists() else None
    note=f"All {check['passed']} of {check['cases']} selected impact cases met the declared integration-refinement tolerances at 0.5 versus 0.25 second steps." if check else 'Representative integration-refinement checks are pending.'
    table=''.join(f'<tr><td>{label}</td><td>{s["examples_within_3_bto_sd"]:,}</td><td>{s["minutes_after_r600_span"][0]:.1f}–{s["minutes_after_r600_span"][1]:.1f}</td><td>{s["displacement_from_exhaustion_nm_span"][0]:.1f}–{s["displacement_from_exhaustion_nm_span"][1]:.0f}</td></tr>' for s,(_,_,label) in zip(statistics,families))
    energy_low=min(s['kinetic_energy_j_span'][0] for s in statistics);energy_high=max(s['kinetic_energy_j_span'][1] for s in statistics)
    (directory/'report-fragment.html').write_text(f'''<section id="end-of-flight"><h2>End of flight, with final-contact BTO</h2><p>{summary['witnesses']} nominal-fuel source paths and two separate public aerodynamic families generated {len(rows):,} impact examples in {summary['elapsed_s']:.0f} seconds. The expanded controls include sustained bank and an initial bank followed by wings-level flight. The plots highlight examples within three observation standard deviations of the corrected 00:19:29 R600 BTO. This is a descriptive band; the Gaussian observation model has no hard three-SD cutoff.</p><p>The examples have no geographic probability weights. Their counts and plotted density reflect the source paths and chosen lift/bank design. The spans below describe found examples, not confidence intervals or complete feasible bounds.</p><table><thead><tr><th>Alternative</th><th>BTO-band examples</th><th>Minutes after R600</th><th>Range from exhaustion (NM)</th></tr></thead><tbody>{table}</tbody></table><a href="terminal-time-range.svg"><img src="terminal-time-range.svg" alt="Conditional impact time and displacement, highlighting final-contact BTO compatibility"></a><p>{note} Numerical agreement does not establish physical accuracy. There are {weather_unresolved:,} weather-domain unresolved attempts, {envelope_unresolved:,} declared-envelope exits and {trial_unresolved:,} unresolved near-vertical trials. These do not become location exclusions. {pre_contact:,} resolved impacts precede the airborne R600 contact and have zero support under that condition.</p><p>Only {sum(r["r600_powered_in_declared_apu_model"] for r in statistics):,} of the {sum(r["examples_within_3_bto_sd"] for r in statistics):,} BTO-band examples are marked as SATCOM-powered at R600 by the declared APU preset. Its one-second start delay and 118-second generator delay are illustrative timing choices, not a calibrated APU/SDU restart likelihood. Geometry scores and power flags remain separate.</p><p>The powered segment retains its last command after 00:11. Public attached-flow polars and constant lift-coefficient scenarios do not establish post-stall, breakup or compressible-flight behaviour. The separate final-BFO check above finds no matching pair among these examples at the carried bias mean. Calibrated SDU/APU restart timing is still unavailable. Thus the long glides are conditional illustrations, not solutions satisfying all end-of-flight observations.</p></section><section id="impact"><h2>Impact velocity and possible acoustic energy</h2><p>Each impact has jointly calculated horizontal and downward velocity, ground-relative entry angle and kinetic energy. Entry angle is not aircraft body pitch. The BTO-band examples carry about {energy_low/1e9:.2g}–{energy_high/1e9:.2g} GJ of kinetic energy; this is an energy budget, not a measured sound source.</p><a href="terminal-impact-velocity.svg"><img src="terminal-impact-velocity.svg" alt="Horizontal and downward impact velocities under two aerodynamic alternatives"></a><p>Coupling a fraction η of that energy into acoustic waves gives E<sub>acoustic</sub> = η E<sub>impact</sub>. Neither η, body attitude, breakup nor water-entry impulse has been inferred. For illustration only, η = 10<sup>−4</sup> would give approximately {energy_low*1e-4/1e3:.0f}–{energy_high*1e-4/1e3:.0f} kJ. That multiplier is not an adopted prior or a predicted efficiency, and does not determine a receiver amplitude.</p></section><section id="acoustic-timing"><h2>Acoustic arrival-time comparisons</h2><p>For the BTO-band impact examples, the dots give arrival-time limits at Cape Leeuwin (H01W) and Diego Garcia (H08S) using effective sound speeds of 1,430 and 1,570 m/s. Each point retains its linked impact position and time. These are conditional travel-time calculations, with no signal-association likelihood, amplitude, dispersion, blockage or detection model.</p><a href="terminal-acoustic-timing.svg"><img src="terminal-acoustic-timing.svg" alt="Conditional acoustic travel-time limits for impact examples"></a><p>The dashed line marks Kadri’s preferred arrival time. Timing overlap alone does not establish a match: his reported bearing and the signal’s identity also matter.</p></section>''')


def update_final_bfo_panel(output):
    """Keep the joint startup condition visible before terminal illustrations."""
    directory=output/'final-bfo-comparison';web=output/'web'
    if not (directory/'summary.json').exists():return
    summary=json.loads((directory/'summary.json').read_text());rows=[json.loads(line) for line in (directory/'terminal-bfo-comparisons.jsonl').open()]
    bias_note=''
    if (directory/'bias-sensitivity.json').exists():
        sensitivity=json.loads((directory/'bias-sensitivity.json').read_text())
        nearest=min(r['minimum_required_bias_sd'] for r in sensitivity['comparison_counts'] if r['minimum_required_bias_sd'] is not None)
        bias_note=f'<p>Allowing the shared steady bias to vary also leaves zero matching examples within three conditional bias standard deviations. Among the few pairs whose frequency change could be matched at any bias, the nearest requires about {nearest:.0f} standard deviations under the earlier observation model. The selected Kadri examples cannot be rescued by any common bias shift because their frequency change fails the joint condition. These are sensitivity checks, not claims that Gaussian tails have a hard boundary.</p>'
    fig,ax=plt.subplots(figsize=(5.5,4.8))
    for family,color,label in [('openap_v2_6_0_attached_flow','#315b80','Current public polar'),('openap_published2020_attached_flow','#bf781e','Published 2020 polar')]:
        pairs=np.array([r['steady_bfo_hz'] for r in rows if r['family']==family and r['r600_within_3_bto_sd']]);ax.scatter(pairs[:,0],pairs[:,1],s=3,alpha=.12,color=color,label=label,rasterized=True)
    # Corner cloud of the declared joint warmup/noise support, using the
    # printed-table error convention. Convex hull is exact for this linear set.
    from scipy.spatial import ConvexHull
    candidates=[]
    for w1,w2 in [(17,17),(23,17),(136,130),(130,130)]:
        for e1 in [-18,28]:
            for e2 in [-18,28]:candidates.append([182-w1+e1,-2-w2+e2])
    points=np.array(candidates);hull=points[ConvexHull(points).vertices];ax.add_patch(Polygon(hull,fill=False,lw=1.5,edgecolor='#b8493d',label='Shared warm-up + bounded errors'))
    ax.add_patch(Polygon([[164,-20],[210,-20],[210,26],[164,26]],fill=False,lw=1.2,ls='--',edgecolor='#333',label='No warm-up + bounded errors'))
    ax.set(xlabel='Predicted steady BFO at first final contact (Hz)',ylabel='Predicted steady BFO at second final contact (Hz)');ax.grid(alpha=.15);ax.legend(fontsize=7,markerscale=4,loc='upper left');fig.tight_layout();fig.savefig(web/'final-bfo-pairs.svg',dpi=180);fig.savefig(web/'final-bfo-pairs.png',dpi=140);plt.close(fig)
    matches=sum(r['no_warmup_compatible']+r['shared_warmup_compatible'] for r in summary['comparison_counts'])
    status=f"None of the {summary['resolved_pair_count']:,} resolved pairs matches both final readings under either tested startup condition." if matches==0 else 'Some resolved pairs satisfy the declared joint conditions; this is not a calibrated likelihood.'
    (directory/'report-fragment.html').write_text(f'''<section id="final-bfo"><h2>Final BFO: the tested terminal family is insufficient</h2><div class="note"><strong>{status}</strong> The impact and Kadri plots below are therefore conditional illustrations, not trajectories satisfying all final satellite evidence.</div><p>The comparison retains the measured 182 and −2 Hz readings and predicts BFO from each calculated position and velocity. A single shared oscillator warm-up condition links the two readings; we also test a no-warm-up alternative. The outlined regions show those conditions with the published historical error bounds. Coloured points also satisfy the illustrative R600 BTO band.</p><a href="final-bfo-pairs.svg"><img src="final-bfo-pairs.svg" alt="Predicted pairs of final BFO values compared with joint conditional observation regions"></a><p>Historical error extrema and previous log-on behaviour are conditional bounds, not probability distributions. The paper’s prose and table use different error signs; both were checked and the conclusion for these examples is unchanged. The steady bias is carried from the earlier flight, not fitted to the final readings. Both final checkpoints use the logged fractional-second timestamps, 00:19:29.416 and 00:19:37.443. This fixes their 8.027-second separation; it does not determine an acceleration without a flight and startup model. <a href="https://arxiv.org/html/1702.02432v3">Holland, inspected 2018 version, sections III–VI</a>; <a href="https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf">Inmarsat/DCA log, page 41</a>.</p>{bias_note}<p>This result does not eliminate a geographic region. It shows that constant-lift and the tested bank histories do not yet provide an adequate end-of-flight family. Descent and recovery behaviour, calibrated startup uncertainty and unsupported aerodynamic states remain to be resolved before claiming impact probabilities.</p></section>''')


def update_hypothesis_path_panels(output):
    """Show actual conditional paths retained by an external event comparison."""
    import datetime as dt
    directory=output/'kadri-trajectory-examples';path=directory/'trajectory-examples.jsonl';web=output/'web'
    if not (directory/'summary.json').exists():return
    rows=[json.loads(line) for line in path.open()]
    selected=json.loads((output/'kadri-preferred-event/selected-impact-examples.json').read_text());lookup={(r['witness'],r['example']):r for r in selected}
    fig,ax=plt.subplots(figsize=(5.5,6.4));zoom,az=plt.subplots(figsize=(5.5,5.0));profiles,ap=plt.subplots(2,1,figsize=(5.5,5.8),sharex=True)
    land=json.loads((ROOT/'crates/reporting/assets/ne_110m_land.geojson').read_text())
    for feature in land['features']:
        g=feature['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'] if g['type']=='MultiPolygon' else []
        for poly in polys:ax.add_patch(Polygon(np.asarray(poly[0]),facecolor='#e5e7e9',edgecolor='#adb5bc',linewidth=.35,zorder=0))
    colors=plt.get_cmap('tab10');table=[];mesh_checks=[];all_points=[]
    for j,row in enumerate(rows):
        color=colors(j);label=chr(65+j);response=row['response'];trace=[t for t in response['trace'] if t['aircraft']['time']>=1425.]
        aircraft=[t['aircraft'] for t in trace];ax.plot([a['position']['longitude'] for a in aircraft],[a['position']['latitude'] for a in aircraft],lw=1.1,color=color,label=label)
        time=np.array([a['time'] for a in aircraft]);ap[0].plot(time,[t['mach'] for t in trace],color=color,lw=1);ap[1].plot(time,[a['altitude']/1000 for a in aircraft],color=color,lw=1)
        powered=[response['endpoint']]+[r['state']['powered_flight']['aircraft'] for r in row['powered_continuation_trace']]+[response['continuation']['state']['powered_flight']['aircraft']]
        x=[a['position']['longitude'] for a in powered];y=[a['position']['latitude'] for a in powered];az.plot(x,y,color=color,lw=1.3);az.scatter(x[0],y[0],color=color,marker='s',s=24);az.scatter(x[-1],y[-1],color=color,marker='o',s=24)
        for e,example in zip(row['example_indices'],response['terminal_examples']):
            attempt=example['attempt'];impact=attempt['transition']['impact'];original=lookup[(row['witness'],e)];state=[c['state']['kinematics']['point_mass'] for c in attempt['checkpoints']]+[attempt['transition']['terminal']['kinematics']['point_mass']]
            xx=[x[-1]]+[s['position']['longitude'] for s in state];yy=[y[-1]]+[s['position']['latitude'] for s in state];az.plot(xx,yy,color=color,lw=1,ls='--');az.scatter(xx[-1],yy[-1],marker='x',s=32,color=color);all_points.extend(zip(xx,yy))
            contact=example['final_contact_bto'][0]
            if contact.get('aircraft'):
                pos=contact['aircraft']['position'];az.scatter(pos['longitude'],pos['latitude'],marker='^',s=24,color=color)
            a=original['impact'];mesh_checks.append({'witness':row['witness'],'example':e,'time_change_s':abs(a['point']['time']-impact['point']['time']),'position_change_nm':distance_nm(a['point']['position'],impact['point']['position']),'relative_energy_change':abs(a['kinetic_energy']/impact['kinetic_energy']-1)})
        reference=lookup[(row['witness'],row['example_indices'][0])];count=reference['command_counts'];table.append(f'<tr><td style="color:{matplotlib.colors.to_hex(color)}"><strong>{label}</strong></td><td>{count["control"]}</td><td>{count["mach"]}</td><td>{count["altitude"]}</td><td>{len(row["example_indices"])}</td></tr>')
    ax.set(xlim=(89,107),ylim=(-29,9),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees)');ax.set_aspect(1/math.cos(math.radians(15)));ax.legend(title='Source path',ncol=4,fontsize=8,loc='upper right');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(web/'kadri-flight-paths.svg');fig.savefig(web/'kadri-flight-paths.png',dpi=150);plt.close(fig)
    points=np.array(all_points);az.set(xlim=(points[:,0].min()-.25,points[:,0].max()+.25),ylim=(points[:,1].min()-.25,points[:,1].max()+.25),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees)');az.set_aspect(1/math.cos(math.radians(26)));az.grid(alpha=.15)
    from matplotlib.lines import Line2D
    az.legend(handles=[Line2D([],[],color='#555',marker=m,ls='none',label=l) for m,l in [('s','00:11'),('o','Fuel exhaustion'),('^','R600 contact'),('x','Impact')]],fontsize=8,ncol=2);zoom.tight_layout();zoom.savefig(web/'kadri-terminal-paths.svg');plt.close(zoom)
    ap[0].set_ylabel('Mach number');ap[1].set_ylabel('Pressure altitude (1,000 ft)');ap[1].set_xticks([1425,9555,16772,22150],['18:25','20:41','22:41','00:11']);ap[1].set_xlabel('UTC, 7–8 March 2014')
    for axis in ap:axis.grid(alpha=.15)
    profiles.tight_layout();profiles.savefig(web/'kadri-cruise-profiles.svg');plt.close(profiles)
    (directory/'checkpoint-mesh-comparison.json').write_text(json.dumps(mesh_checks,indent=2))
    comparison=json.loads((output/'kadri-preferred-event/impact-comparison-summary.json').read_text());origin=dt.datetime(2014,3,7,18,1,49,tzinfo=dt.timezone.utc).timestamp();times=[r['impact']['point']['time'] for r in selected]
    start,end=[dt.datetime.fromtimestamp(origin+t,dt.timezone.utc).strftime('%H:%M') for t in [min(times),max(times)]]
    fragment=f'''<section id="kadri-paths"><h2>Paths meeting Kadri timing and bearing conditions</h2><div class="note"><strong>None of these examples passes the joint final-BFO comparison at the carried bias mean.</strong> These paths illustrate a partial evidence match, not a SATCOM-consistent impact solution.</div><p>{len(selected)} resolved impact examples from {len(rows)} source paths meet the illustrative R600 BTO band, fall within ±0.5° of the reported bearing and can produce the preferred arrival at a sound speed within 1,430–1,570 m/s. Their calculated impact times are approximately {start}–{end} UTC. Widening the bearing condition to ±3.3° retains {comparison['conditional_counts_by_bearing_half_width_deg']['3.3']} examples. These counts are properties of the tested examples, not likelihoods or probabilities.</p><a href="kadri-flight-paths.svg"><img src="kadri-flight-paths.svg" alt="Actual post-18:25 candidate paths linked to conditional Kadri impact examples"></a><table><thead><tr><th>Path</th><th>Direction settings</th><th>Speed changes</th><th>Altitude changes</th><th>Impacts</th></tr></thead><tbody>{''.join(table)}</tbody></table><details><summary>Mach and altitude along these paths</summary><img src="kadri-cruise-profiles.svg" alt="Cruise profiles of the conditional source paths"></details><p>The close view joins the 00:11 state, powered continuation, exhaustion, R600 checkpoint and simulated impact. Dashed segments show terminal flight. The same colour identifies the same source path in both plots.</p><a href="kadri-terminal-paths.svg"><img src="kadri-terminal-paths.svg" alt="Linked final powered and unpowered flight segments for the selected examples"></a><p>These are examples selected after simulation, not a sample drawn from a Kadri-conditioned trajectory prior. They fail the separate joint final-BFO check; calibrated restart timing also remains unavailable. The bearing tolerance, signal association, effective sound speed and public aerodynamic assumptions are explicit conditions; a deliberately complicated route is not ruled out by a simplicity preference.</p></section>'''
    (directory/'report-fragment.html').write_text(fragment)


def godfrey_acoustic_panel(output):
    """Overlay saved conditional arrival windows on attributed plot vertices."""
    import csv
    import datetime as dt
    directory=output/'godfrey-trajectory-audit';evidence=output/'evidence-comparison';web=output/'web'
    path=directory/'conditional-acoustic-arrivals.json'
    if not path.exists():return ''
    arrivals=json.loads(path.read_text());metadata=json.loads((evidence/'metadata.json').read_text())
    midnight=dt.datetime(2014,3,8,tzinfo=dt.timezone.utc)
    minute=lambda value:(dt.datetime.fromisoformat(value.replace('Z','+00:00'))-midnight).total_seconds()/60
    scenarios=list(dict.fromkeys(r['impact_time_label'] for r in arrivals))
    fig,axes=plt.subplots(2,1,figsize=(5.5,6.3));summary=[]
    for station,ax in zip(['H01W','H08S'],axes):
        for trace in metadata['figure9_vector_traces']:
            if trace['station']!=station:continue
            # Each publication panel remains a separate line; its boundary is
            # not treated as continuous raw receiver data.
            rows=list(csv.DictReader((evidence/pathlib.Path(trace['file']).name).open()))
            ax.plot([minute(r['utc']) for r in rows],[float(r['pressure_pa']) for r in rows],color='#53616c',lw=.35,rasterized=True)
        for label,color,short in zip(scenarios,['#315b80','#bf781e'],['00:21:46 impact illustration','00:27:51 impact illustration']):
            selected=[r for r in arrivals if r['station']==station and r['impact_time_label']==label]
            times=[minute(r['arrival_time_utc']) for r in selected];lo,hi=min(times),max(times)
            ax.axvspan(lo,hi,color=color,alpha=.16,label=short)
            summary.append({'station':station,'impact_time_label':label,'arrival_minutes_after_midnight_span':[lo,hi]})
        if station=='H01W':ax.axvline(54.5,color='#b8493d',ls='--',lw=1,label='Kadri preferred arrival')
        ax.set_title(station+' · published Figure 9 traces',loc='left',fontsize=11)
        ax.set_ylabel('Plotted pressure (Pa)');ax.set_xlabel('UTC, 8 March 2014');ax.grid(alpha=.12)
        ticks=[30,35,40,45,50,55] if station=='H01W' else [60,65,70,75,80]
        ax.set_xticks(ticks,[f'{int(m)//60:02d}:{int(m)%60:02d}' for m in ticks])
        ax.set_xlim((27,57) if station=='H01W' else (60,80))
    axes[0].legend(fontsize=7,loc='lower left');fig.tight_layout();fig.savefig(web/'godfrey-acoustic-windows.svg',dpi=170);fig.savefig(web/'godfrey-acoustic-windows.png',dpi=130);plt.close(fig)
    (directory/'plotted-acoustic-windows.json').write_text(json.dumps(summary,indent=2))
    def clock_string(minutes):
        return (midnight+dt.timedelta(minutes=minutes)).strftime('%H:%M')
    table=''.join(f'<tr><td>{station}</td><td>{clock_string(min(r["arrival_minutes_after_midnight_span"][0] for r in summary if r["station"]==station))}–{clock_string(max(r["arrival_minutes_after_midnight_span"][1] for r in summary if r["station"]==station))}</td></tr>' for station in ['H01W','H08S'])
    return f'''<section id="godfrey-acoustics"><h2>Godfrey locations: predicted acoustic timing</h2><p>Separate sensitivity calculations combine four reported position indicators with the report’s two illustrative impact times, and effective sound speeds of 1,430–1,570 m/s. These eight combinations are our comparison grid, not eight coherent flights or eight impact claims made by the authors. The 00:26 position indicator near 29.13°S, 99.93°E is not a measured impact point.</p><table><thead><tr><th>Receiver</th><th>Combined illustrative arrival range, UTC</th></tr></thead><tbody>{table}</tbody></table><p>The coloured bands show arrival windows for the two impact-time assumptions. The background lines are digitised vertices from Kadri’s published Figure 9, with each original panel kept separate.</p><a href="godfrey-acoustic-windows.svg"><img src="godfrey-acoustic-windows.svg" alt="Godfrey conditional acoustic arrival windows over digitised published hydrophone plot traces"></a><p>A visible fluctuation within a window cannot identify a crash, and absence of a conspicuous peak here cannot exclude one. The publication traces have already been processed and plotted; raw multi-channel waveforms, source amplitude, propagation loss and a calibrated detection model are unavailable. No acoustic association or WSPR likelihood follows from this overlay. <a href="https://pedrocarvalho.es/docs/WSPR%20report.pdf">Godfrey report, pages 48–49</a>; <a href="https://www.nature.com/articles/s41598-024-60529-1">Kadri (2024), Figure 9 and page 13</a>.</p></section>'''


def search_context_panel(output):
    """Display attributed coverage context and explicit hypothetical detection."""
    from matplotlib.lines import Line2D
    directory=output/'evidence-comparison';web=output/'web';path=directory/'search-evidence-atlas.geojson'
    if not path.exists():return ''
    atlas=json.loads(path.read_text());fig,ax=plt.subplots(figsize=(5.5,6.1))
    styles={'phase2_deep':('#315b80','-',.30),'oi2018_proxy':('#bf781e','--',.05),
            'oi2024_outboard_proxy':('#b8493d',':',.07),'oi2024_inboard_proxy':('#b8493d',':',.07)}
    for feature in atlas['features']:
        layer=feature['properties']['atlas_layer'];g=feature['geometry']
        if layer=='seventh_arc':
            points=np.array(g['coordinates']);ax.plot(points[:,0],points[:,1],color='#53616c',ls='--',lw=.8)
        if layer not in styles:continue
        color,style,alpha=styles[layer]
        polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'] if g['type']=='MultiPolygon' else []
        for polygon in polygons:
            # These are context outlines. No point-in-polygon calculation or
            # detection likelihood is applied, including to interior holes.
            points=np.array(polygon[0]);ax.fill(points[:,0],points[:,1],color=color,alpha=alpha)
            ax.plot(points[:,0],points[:,1],color=color,ls=style,lw=.75)
            for hole in polygon[1:]:
                points=np.array(hole);ax.plot(points[:,0],points[:,1],color=color,ls=style,lw=.5)
    witnesses=output/'antenna-comparison/full-compensation-examples.jsonl'
    if witnesses.exists():
        rows=[json.loads(line) for line in witnesses.open()];positions=[r['endpoint']['position'] for r in rows]
        ax.scatter([p['longitude'] for p in positions],[p['latitude'] for p in positions],s=8,color='#8c959c',alpha=.5)
    selected=output/'kadri-preferred-event/selected-impact-examples.json'
    if selected.exists():
        rows=json.loads(selected.read_text());positions=[r['impact']['point']['position'] for r in rows]
        ax.scatter([p['longitude'] for p in positions],[p['latitude'] for p in positions],s=25,color='#784f88',marker='x')
    godfrey=output/'godfrey-trajectory-audit/conditional-acoustic-arrivals.json'
    if godfrey.exists():
        positions=sorted(set((r['longitude_deg'],r['latitude_deg']) for r in json.loads(godfrey.read_text())))
        ax.scatter(*np.array(positions).T,s=24,color='#1c877d',marker='D')
    handles=[Line2D([],[],color=c,ls=s,label=l) for c,s,l in [('#315b80','-','Official detailed data footprint'),('#bf781e','--','2018 outline · approximate'),('#b8493d',':','2024 proposal · approximate'),('#53616c','--','Seventh arc · FL400')]]
    handles += [Line2D([],[],color=c,marker=m,ls='none',label=l) for c,m,l in [('#8c959c','o','00:11 examples · unweighted'),('#784f88','x','Kadri timing/bearing examples'),('#1c877d','D','Godfrey position indicators')]]
    ax.legend(handles=handles,fontsize=7,loc='upper left');ax.set(xlim=(82,110),ylim=(-43,-11),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees)');ax.set_aspect(1/math.cos(math.radians(28)));ax.grid(alpha=.15);fig.tight_layout();fig.savefig(web/'search-context.svg');fig.savefig(web/'search-context.png',dpi=140);plt.close(fig)
    # Generic Bayes calculation for a hypothetical chosen area. p is its
    # probability mass, not its geometric area divided by the found span.
    widget='''<div class="note" id="search-sensitivity"><strong>Illustration: what area and detection uncertainty mean</strong><p>These sliders are hypothetical inputs, not estimates from this project. A 7,500 km² area can have very different value depending on how much probability it contains.</p><label for="search-mass">Assumed chance that wreckage is in the selected area: <output id="search-mass-label">20%</output></label><input id="search-mass" type="range" min="1" max="99" value="20" style="width:100%"><label for="search-detection">Assumed chance of finding it if it is there: <output id="search-detection-label">80%</output></label><input id="search-detection" type="range" min="0" max="100" value="80" style="width:100%"><p aria-live="polite" id="search-sensitivity-result">Under these hypothetical inputs: 16.0% chance of discovery. If the search finds nothing, 4.8% remains in this area.</p><small>Chance of discovery = p × d. After no discovery, chance it remains in that area = p(1 − d)/(1 − pd). Here d is the overall detection chance for this search. Repeated passes cannot be treated as independent without justification.</small></div><script>(()=>{const p=document.getElementById('search-mass'),d=document.getElementById('search-detection');function update(){const mass=Number(p.value)/100,detect=Number(d.value)/100;document.getElementById('search-mass-label').value=p.value+'%';document.getElementById('search-detection-label').value=d.value+'%';document.getElementById('search-sensitivity-result').textContent='Under these hypothetical inputs: '+(100*mass*detect).toFixed(1)+'% chance of discovery. If the search finds nothing, '+(100*mass*(1-detect)/(1-mass*detect)).toFixed(1)+'% remains in this area.'}p.addEventListener('input',update);d.addEventListener('input',update);update()})();</script>'''
    return '''<section id="search-context"><h2>Search coverage and the candidate examples</h2><p>The blue outline is an official detailed sonar-data footprint. The orange outline reconstructs the 2018 search context; red outlines are an approximate 2024 proposal, not the current contract or completed survey. None supplies a complete, target-specific chance of missed detection, so none has been used as a binary exclusion.</p><a href="search-context.svg"><img src="search-context.svg" alt="Attributed search outlines, unweighted 00:11 examples and explicitly conditional source hypotheses"></a><p>The grey marks are 00:11 positions, not impacts. The Kadri examples fail the joint final-BFO check; Godfrey’s indicators still require the route checks described above. This map therefore shows spatial context, not a ranked search region. Points are not probability weights, and no current AUV swath geometry is inferred from vessel tracks.</p>'''+widget+'</section>'


def update_source_comparison_panels(output):
    """Report immutable source-result snapshots, never pool them into a PDF."""
    import csv,shutil
    directory=output/'evidence-comparison';web=output/'web';parts=[]
    if (directory/'drift-relative-curves.csv').exists():
        rows=list(csv.DictReader((directory/'drift-relative-curves.csv').open()))
        labels={'cmems-stringent-nine-recovered-only':'CMEMS: stringent nine','cmems-expanded-official-twenty-recovered-only':'CMEMS: expanded objects','cmems-stringent-nine-excluding-interior-panels':'CMEMS: omit interior panels','cmems-stringent-nine-full-declared-evidence':'CMEMS: ancillary conditions','gdp-stringent-nine-full-declared-evidence':'GDP: ancillary conditions'}
        fig,ax=plt.subplots(figsize=(5.5,4.8))
        for i,name in enumerate(dict.fromkeys(r['variant_id'] for r in rows)):
            subset=[r for r in rows if r['variant_id']==name];lat=np.array([float(r['latitude_deg']) for r in subset]);score=np.array([float(r['prior_removed_log_likelihood']) for r in subset]);relative=np.exp(score-score.max());ax.plot(lat,np.where(relative>=1e-8,relative,np.nan),label=labels.get(name,name.replace('-',' ')),lw=1.4)
        ax.set(xlabel='Source latitude along the reference arc (degrees)',ylabel='Relative conditional drift score',yscale='log',ylim=(1e-8,1.4));ax.grid(alpha=.15);ax.legend(fontsize=7,loc='lower left');fig.tight_layout();fig.savefig(web/'drift-alternatives.svg');plt.close(fig)
        parts.append('<section><h2>Recovered debris and ocean drift</h2><p>The existing source-prior-removed calculations can be compared, but their numerical instability prevents a reliable update of the flight distribution. Different recovered-object sets and transport assumptions remain separate curves. A narrow spike can reflect rare-event sampling rather than precise knowledge. Scores below 10<sup>−8</sup> are omitted from the logarithmic plot.</p><p>GLORYS12 currents with a separate WAVERYS Stokes response is the best-supported starting family in the existing matched transport checks. Full surface Stokes response, direct windage, coastal retention and discovery delays remain conditional choices. These curves are inherited sensitivity results; no new multi-year drift ensemble or combined flight–drift PDF is claimed.</p><a href="drift-alternatives.svg"><img src="drift-alternatives.svg" alt="Different conditional drift scores along the reference arc"></a></section>')
    if (directory/'pleiades-grid.csv').exists():
        grid={r['cell_id']:r for r in csv.DictReader((directory/'pleiades-grid.csv').open())};rows=list(csv.DictReader((directory/'pleiades-surfaces.csv').open()));fig,ax=plt.subplots(figsize=(5.5,4.1))
        for name,label in [('bran2016','BRAN2016'),('oscar_v2_final','OSCAR v2 Final'),('glorys12_waverys','GLORYS12 + WAVERYS')]:
            groups={}
            for r in rows:
                if r['surface_id']!=name:continue
                cell=grid[r['cell_id']];groups.setdefault(int(cell['along_index']),[]).append((float(cell['cross_nm']),float(cell['latitude_deg']),float(r['relative_likelihood'])))
            values=[]
            for k,group in sorted(groups.items()):values.append((next(lat for cross,lat,score in group if cross==0),max(score for cross,lat,score in group)))
            x,y=np.array(values).T;ax.plot(x,y/y.max(),label=label)
        ax.set(xlabel='Reference-arc latitude (degrees)',ylabel='Maximum relative proxy score\nover the tested cross-arc offsets');ax.grid(alpha=.15);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(web/'pleiades-alternatives.svg');plt.close(fig)
        parts.append('<section><h2>Pléiades: an explicit object-identity hypothesis</h2><p>The image objects have not been identified as MH370 debris. This comparison assumes exactly one associated object, gives each of twelve selected image locations equal weight, and uses a declared transport/error model. The three current products are alternative explanations of the same image evidence.</p><p>The plot takes the maximum compatibility score across the tested cross-arc offsets; it is neither a marginal PDF nor a confidence interval. The existing grid covers only a strip around 32–39°S. More northerly flight solutions are outside its computed support and cannot be ruled out by setting their score to zero.</p><a href="pleiades-alternatives.svg"><img src="pleiades-alternatives.svg" alt="Conditional image transport comparisons for three current products"></a></section>')
    kadri=output/'kadri-preferred-event'
    if (kadri/'summary.json').exists():
        shutil.copyfile(kadri/'preferred-event-geometry.svg',web/'kadri-preferred-event.svg')
        parts.append('<section><h2>Kadri’s original preferred event</h2><p>The preferred Table 1 entry is 00:54:30 UTC at a bearing of 306.18° from Cape Leeuwin. Conditional on an association with MH370, it defines linked impact locations and times. The curves below recreate that relationship; they do not show that an aircraft could follow every implied route.</p><p>The paper’s printed range, speed and timing illustration do not reproduce its prose numbers. The recreation retains the printed inputs and a separate interpretation of the apparent velocity-unit error. The reported signal’s identity and acoustic association remain unproved. <a href="https://www.nature.com/articles/s41598-024-60529-1">Kadri (2024), pages 13–14 and Table 1</a>.</p><a href="kadri-preferred-event.svg"><img src="kadri-preferred-event.svg" alt="Conditional location and time curves for Kadri’s original preferred event"></a></section>')
        fragment=output/'kadri-trajectory-examples/report-fragment.html'
        if fragment.exists():parts.append(fragment.read_text())
    godfrey=output/'godfrey-trajectory-audit'
    if (godfrey/'bto-comparison.json').exists():
        rows=json.loads((godfrey/'bto-comparison.json').read_text());epochs=list(dict.fromkeys(r['epoch_id'] for r in rows));fig,ax=plt.subplots(figsize=(5.5,4.0))
        lo=[];hi=[];closest=[]
        for epoch in epochs:
            z=np.array([r['residual_standard_deviations'] for r in rows if r['epoch_id']==epoch]);lo.append(z.min());hi.append(z.max());closest.append(z[np.argmin(abs(z))])
        ax.vlines(range(len(epochs)),lo,hi,color='#315b80',lw=3);ax.scatter(range(len(epochs)),closest,s=20,color='#bf781e',label='Closest tested combination');ax.axhline(0,color='#777',lw=1);ax.axhspan(-3,3,color='#ddd',alpha=.3);ax.set(xticks=range(len(epochs)),xticklabels=[e[1:] for e in epochs],xlabel='SATCOM epoch label (UTC)',ylabel='Observed minus nominal-route BTO\n(observation standard deviations)');ax.tick_params(axis='x',rotation=55);ax.grid(axis='y',alpha=.15);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(web/'godfrey-bto-check.svg');plt.close(fig)
        parts.append('<section><h2>Godfrey’s proposed route</h2><p>The 68 tabulated positions were transcribed from the 2023 report and checked at their nominal times. One six-minute leg implies about 735 knots; allowing independent times within the WSPR transmissions reduces its necessary mean speed to about 563 knots. Its favorable midpoint weather/speed check is about 530 knots, which is a concern to resolve rather than a rigorous full-leg exclusion.</p><p>Shortest-leg interpolation also leaves BTO discrepancies at 20:41 and 21:41 across the tested altitude and common timestamp alternatives. The bars show those alternatives, not confidence intervals. Position uncertainty, continuous controls, fuel and BFO still require a full route fit. The public WSPR archive has not supplied a calibrated location likelihood. <a href="https://pedrocarvalho.es/docs/WSPR%20report.pdf">Godfrey, Coetzee and Maskell (2023), Table 5, pages 50–53</a>.</p><a href="godfrey-bto-check.svg"><img src="godfrey-bto-check.svg" alt="BTO diagnostic comparison along the published nominal route"></a></section>')
    acoustic=godfrey_acoustic_panel(output)
    if acoustic:parts.append(acoustic)
    if (directory/'search-readiness.json').exists():
        parts.append('<section><h2>What can 7,500 km² of search achieve?</h2><p>The useful quantity is the probability of wreckage within the chosen area, multiplied by the chance of detection there. The width of the feasible region alone does not establish that searching is futile. Equally, the density of optimized example paths cannot justify a search allocation.</p><p>A defensible recommendation still needs a stable impact distribution, attributed coverage with gaps and sonar quality, and target-specific detection uncertainty. Approximate search outlines, vessel tracks and bathymetric coverage cannot be treated as certain exclusions. The 2022 official sonar review covered a particular approximately 17,000 km² region; its 72.79 km² of gaps or lower-quality coverage is not a global missed-detection map. <a href="https://www.atsb.gov.au/mh370-data-review">ATSB data review</a>.</p></section>')
        status=directory/'current-contract-status.json'
        if status.exists():
            current=json.loads(status.read_text())
            parts[-1]=parts[-1].replace('</section>',f'<p>A later administrative update matters: RTM’s 29 June report quotes a ministerial statement extending the contract to June 2027, with {current["reported_remaining_area_km2"]:,.2f} km² remaining and an anticipated November–April asset window. The original statement PDF has not been located. This reported total does not provide a remaining-area polygon or a guaranteed survey schedule. <a href="{escape(current["source_url"])}">RTM report</a>.</p></section>')
        context=search_context_panel(output)
        if context:parts.append(context)
    if parts:(directory/'report-fragment.html').write_text(''.join(parts))

def inline_preview(web, target, page='index.html'):
    """Embed generated plots for ISO previews without a running report server."""
    import base64
    import re
    html=(web/page).read_text()
    # Images remain zoomable through the viewer; local download links cannot
    # resolve in an opaque-origin preview and must not look like working links.
    html=re.sub(r'<a href="(?!https?://|#)[^"]*">(.*?)</a>',r'\1',html,flags=re.S)
    def embed(match):
        name=match.group(1)
        if name.startswith(('data:','http://','https://')):
            raise ValueError('Inline report requires locally retained image inputs')
        path=web/name
        if path.suffix!='.svg':
            raise ValueError(f'Unexpected report image type: {path.suffix}')
        return 'src="data:image/svg+xml;base64,'+base64.b64encode(path.read_bytes()).decode()+'"'
    html=re.sub(r'src="([^"]+)"',embed,html)
    html=html.replace('<main>','<main><p><strong>Embedded report:</strong> all plots are included in this file. A report web server is not required. Download links are available in the browser edition.</p>',1)
    if len(html.encode())>=5*1024*1024:
        raise ValueError('Inline report exceeds the ISO preview document limit')
    target.write_text(html)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=pathlib.Path)
    parser.add_argument('--web-only',action='store_true',help='Render the browser plots without rewriting the archived report or numerical artifacts.')
    parser.add_argument('--progress-from',type=pathlib.Path,help='Add a browser progress report from extended control artifacts; output remains the original pre-analysis directory.')
    parser.add_argument('--inline-output',type=pathlib.Path,help='Also write a self-contained ISO HTML preview with embedded plots.')
    parser.add_argument('--sampler-from',type=pathlib.Path,help='Add current forward/backward sampling comparisons from retained artifacts.')
    parser.add_argument('--inline-page',default='index.html',choices=['index.html','flight-sampling.html'],help='Page to embed in the self-contained preview.')
    args=parser.parse_args()
    if args.progress_from:progress_report(args.output,args.progress_from)
    else:main(args.output,args.web_only)
    if args.sampler_from:
        from flight_sampling_report import write_sampling_report
        write_sampling_report(args.sampler_from,(args.progress_from or args.output)/'web')
    if args.inline_output:inline_preview((args.progress_from or args.output)/'web',args.inline_output,args.inline_page)
