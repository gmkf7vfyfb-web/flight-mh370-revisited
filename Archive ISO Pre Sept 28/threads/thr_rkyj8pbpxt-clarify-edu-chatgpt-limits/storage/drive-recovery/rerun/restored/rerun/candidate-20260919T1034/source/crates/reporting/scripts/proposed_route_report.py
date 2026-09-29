"""Compare a published route hypothesis with audited constraints and saved paths."""
from __future__ import annotations
import argparse, csv, datetime as dt, json, shlex
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from arc_density_report import digest, draw_land, save_figure


def epoch(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()


def report(args):
    args.output.mkdir(parents=True,exist_ok=True)
    audit=json.loads((args.audit/'summary.json').read_text());acoustic=json.loads((args.audit/'acoustic-comparison-summary.json').read_text())
    for path in [args.positions,args.paper]:
        if digest(path)!=audit['input_sha256'][str(path.resolve())]:raise ValueError('Published route source changed')
    positions=list(csv.DictReader(args.positions.open()));bto=json.loads((args.audit/'bto-comparison.json').read_text())
    arrivals=json.loads((args.audit/'conditional-acoustic-arrivals.json').read_text())
    trace=json.loads(args.histories.read_text());examples=[e for e in trace['examples'] if e['latitude_bin_center_deg']==-30]
    if not trace['full_contact_state_and_likelihood_match']:raise ValueError('Unverified example histories')
    plt.rcParams.update({'svg.fonttype':'none','font.size':10})
    figures=[]
    fig,axes=plt.subplots(1,2,figsize=(10.5,6.8));ax=axes[0];draw_land(ax)
    lon=[float(p['longitude_deg']) for p in positions];lat=[float(p['latitude_deg']) for p in positions]
    ax.plot(lon,lat,'o-',color='#a65323',lw=1.1,ms=2.3,label='Published Table 5 positions; connecting guide')
    for e in examples:
        points=e['points'];ax.plot([p['longitude_deg'] for p in points],[p['latitude_deg'] for p in points],lw=1.3,label=f"Saved model path {e['terminal_slot']}")
    ax.set(xlim=(88,104),ylim=(-33,8),xlabel='Longitude (°E)',ylabel='Latitude (°)',title='Published route and northern model examples')
    ax.legend(fontsize=7,loc='lower left');ax.grid(alpha=.15)
    ids=list(dict.fromkeys(r['epoch_id'] for r in bto));x=np.arange(len(ids))
    nominal=[r for r in bto if r['common_table_time_offset_s']==0]
    for altitude in sorted({r['altitude_ft'] for r in nominal}):
        values={r['epoch_id']:r['residual_standard_deviations'] for r in nominal if r['altitude_ft']==altitude}
        axes[1].plot(x,[values.get(i,np.nan) for i in ids],marker='o',ms=3,label=f'{altitude:,.0f} ft')
    axes[1].axhline(0,color='#555',lw=.6);axes[1].set_xticks(x,[s.replace('m','') for s in ids],rotation=65)
    axes[1].set(xlabel='Satellite observation (UTC)',ylabel='BTO residual / stated σ',title='Nominal table timing; separate altitude checks')
    axes[1].legend(fontsize=8);axes[1].grid(alpha=.15)
    fig.tight_layout(rect=(0,.12,1,.96));fig.text(.5,.018,'Table coordinates are source claims, not measured positions. Lines between table entries do not establish a physically feasible route.\n'
        'Saved model examples end in the 30°S ±1.25° bin; they are not fits to the WSPR route or its claimed impact endpoint.\n'
        'The BTO audit uses spherical interpolation of published positions; no BFO, fuel or continuous-control fit is implied.',ha='center',fontsize=7.5)
    save_figure(fig,args.output,'route-and-bto');figures.append(('route-and-bto','Route and BTO comparison'))
    fig,axes=plt.subplots(2,1,figsize=(10.5,7.5));windows=[]
    for ax,station,panel in zip(axes,['H01W','H08S'],['a','d']):
        path=args.publication_traces/f'kadri-2024-figure9-panel-{panel}-{station}.csv';rows=list(csv.DictReader(path.open()))
        minutes=np.array([(epoch(r['utc'])-1394236800)/60 for r in rows]);pressure=np.array([float(r['pressure_pa']) for r in rows])
        ax.plot(minutes,pressure,color='#555',lw=.45,label='Publication Figure 9 plotted pressure trace')
        for label,color in [("Paper's unpiloted timing illustration",'#297ca9'),("Paper's active-pilot extension illustration",'#b86628')]:
            subset=[r for r in arrivals if r['station']==station and r['impact_time_label']==label]
            values=[(epoch(r['arrival_time_utc'])-1394236800)/60 for r in subset];lo,hi=min(values),max(values)
            ax.axvspan(lo,hi,color=color,alpha=.2,label=label);windows.append(dict(station=station,scenario=label,arrival_minutes_utc=[lo,hi]))
        if station=='H01W':ax.axvline(54.5,color='#99395b',ls=':',label='Kadri preferred feature')
        ax.set(xlim=(27,90),xlabel='Minutes after 00:00 UTC',ylabel='Plotted pressure (Pa)',title=station+' · conditional source-position/time sensitivity')
        ax.legend(fontsize=7,loc='upper right');ax.grid(alpha=.15)
    fig.tight_layout(rect=(0,.1,1,1));fig.text(.5,.017,'Windows span the four published position indicators, two separate impact-time illustrations and 1.43–1.57 km/s celerity.\n'
        'Their cross-pairing is our sensitivity construction. Publication plot vertices are not raw hydrophone data or a new signal detection.',ha='center',fontsize=7.5)
    save_figure(fig,args.output,'conditional-acoustic-windows');figures.append(('conditional-acoustic-windows','Conditional acoustic windows'))
    fastest=audit['fastest_nominal_legs'][0]
    body='<h1>Godfrey route hypothesis: constraint and acoustic comparisons</h1>'
    body+='<p>This report compares the published 2023 Table 5 position claims with the existing satellite and speed audit. It also places the paper’s conditional impact-time illustrations beside the hydroacoustic publication traces. No WSPR likelihood is added to the estimator.</p>'
    body+=f'<p>The fastest nominal leg, {fastest["from_utc"][11:16]}–{fastest["to_utc"][11:16]}, implies about <b>{fastest["nominal_mean_ground_speed_kt"]:.0f} knots</b> mean ground speed. Allowing independent timing anywhere within each 110.484-second transmission reduces its minimum to about {fastest["minimum_mean_speed_allowing_independent_110_484s_slot_times_kt"]:.0f} knots. The available midpoint weather/performance check is a diagnostic, not a proof of full-route impossibility.</p>'
    contact=[r['residual_standard_deviations'] for r in bto if r['epoch_id']=='m2141']
    body+=f'<p>At 21:41, all audited altitude and common-time-offset alternatives miss the BTO by {min(abs(v) for v in contact):.1f}–{max(abs(v) for v in contact):.1f} stated observation standard deviations. That identifies a discrepancy to reconcile; it does not supply a calibrated error law for the published position claims.</p>'
    for stem,title in figures:body+='<section><h2>'+title+'</h2>'+(args.output/(stem+'.svg')).read_text()+'</section>'
    body+='''<details open><summary>What can be concluded</summary><p>The proposed northern positions have testable kinematic and satellite consequences. The printed table has not been reconciled here into a continuous path satisfying performance, BTO, BFO and fuel together. The nearby saved northern trajectories illustrate that part of the model’s support; they do not validate the published route.</p>
<p>The acoustic windows identify where a signal would be expected under the stated position, impact-time and propagation assumptions. Visible pressure activity is not enough to identify an aircraft impact: the source audit found confounding recurring signals, and the raw receiver data and calibrated source/path model are unavailable. No probability is inferred from apparent visual overlap.</p>
<p>The 00:26 position indicator is 29.128°S, 99.934°E; it is not itself a measured impact position at the separately illustrated 00:27:51 time. Page 49’s 00:20 latitude also differs from Table 5; the acoustic sensitivity retains both published alternatives.</p></details>
<p>Sources: <a href="https://pedrocarvalho.es/docs/WSPR%20report.pdf">Godfrey, Coetzee and Maskell (31 August 2023), pages 48–53</a>; <a href="https://www.nature.com/articles/s41598-024-60529-1">Kadri (2024), Figure 9, pages 9 and 13–14</a>. Exact paper and dataset hashes and the earlier audit’s limitations are retained with this report.</p>'''
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 proposed-route comparison</title><style>body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.5 system-ui}main{max-width:1050px;margin:auto;padding:18px}h1{font-size:1.65em}h2{font-size:1.2em}section,details{background:white;padding:12px;margin:20px 0}svg{width:100%;height:auto}</style><main>'+body+'</main></html>'
    if len(document.encode())>5*1024**2:raise ValueError('Inline route comparison exceeds 5 MiB')
    args.inline_output.write_text(document);(args.output/'index.html').write_text(document)
    result=dict(generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),route_audit=audit,acoustic_audit=acoustic,arrival_windows=windows,
        sampled_path_ids=[e['terminal_slot'] for e in examples],histories_sha256=digest(args.histories),report_source_sha256=digest(__file__),
        publication_trace_hashes={str(p):digest(p) for p in args.publication_traces.glob('*.csv')},
        input_hashes={str(p):digest(p) for p in [args.positions,args.paper,args.audit/'summary.json',args.audit/'bto-comparison.json',args.audit/'conditional-acoustic-arrivals.json']})
    (args.output/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    command=shlex.join(['python',str(Path(__file__).resolve()),*sum((['--'+k.replace('_','-'),str(v)] for k,v in vars(args).items()),[])])
    (args.output/'README.md').write_text('# Published-route conditional comparison\n\n```bash\n'+command+'\n```\n\nFull source audit and limitations are in summary.json. This report does not fit a new trajectory or apply WSPR/acoustic evidence. The exact arguments are preserved below.\n\n'+json.dumps({k:str(v) for k,v in vars(args).items()},indent=2)+'\n')
    print(json.dumps(dict(table_positions=len(positions),exact_saved_paths=len(examples),inline_bytes=args.inline_output.stat().st_size)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['audit','positions','paper','histories','publication-traces','output','inline-output']:p.add_argument('--'+name,required=True,type=Path)
    report(p.parse_args())
