#!/usr/bin/env python3
"""Report a failed selection honestly: route geometry is not a posterior."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter,MultipleLocator
import numpy as np
import pandas as pd
import run_route_mixture43 as model
from render_strict_airway import land_polygons,draw_land,arc_curve,degree_lat,textblock

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/route_mixture43'
PDF=ROOT/'output/pdf/mh370_three_route_equal_priors_diagnostics.pdf'
COLORS={'p627':'#bc5b36','igogu_boundary':'#186b85','igogu_south':'#795aa2'}
LABELS={'p627':'P627','igogu_boundary':'IGOGU / published boundary','igogu_south':'IGOGU / south continuation'}
RUNS=['prefix_large_p627','p627_b','igogu_south_a','igogu_boundary_a']


def setup_summary():
    runs=[]
    for name in RUNS:
        manifest=json.loads((OUT/name/'manifest.json').read_text())
        if manifest.get('completed') is not False:
            raise ValueError(f'{name} is not a committed no-support result')
        last=manifest['stages'][-1]
        if last['joint_survivors']!=0:
            raise ValueError('This diagnostic renderer must not replace a supported posterior')
        runs.append({'name':name,'route':manifest['route'],'seed':manifest['seed'],
            'initial_draws':manifest['initial_particles'],'initial_ess':manifest['stages'][0].get('pre_resample_ess'),
            'prefix_survivors':manifest['stages'][0]['joint_survivors'],
            'first_call_proposals':manifest['stages'][1]['proposed'] if len(manifest['stages'])>1 else None,
            'first_call_survivors':last['joint_survivors'] if len(manifest['stages'])>1 else None,
            'physics_before_call':last.get('physics_before_call'),
            'igogu_or_p627_completed_before_call':last.get('igogu_or_p627_completed_before_call'),
            'completed':False,'posterior_route_weight':None,
            'prefix_gate_diagnostic':manifest.get('prefix_gate_diagnostic')})
    result={'user_correction':'one third per leaf, replacing 50/25/25',
        'route_priors':{k:v['prior'] for k,v in model.ROUTE_DEFINITIONS.items()},
        'igogu_total_prior':2/3,'igogu_only_conditional_priors':{'igogu_boundary':.5,'igogu_south':.5},
        'posterior_status':'No complete retained trajectories. Density and posterior route weights are undefined.',
        'fuel_status':'00:15-00:19 exhaustion selection is enabled but no new run reaches that stage.',
        'classification':'Finite-sample conditional model result, not proof of physical exclusion.',
        'inherited_first_call_gate':'P627 must pass POVUS and capture its south target within10deg by18:39:55.354. IGOGU leaves must pass IGOGU and capture true south within10deg by the same time.',
        'control_model_note':'600-second speed capture, 0.25m/s2 commanded acceleration cap, sparse random target changes; these are control-prior assumptions, not manufacturer limits.',
        'runs':runs}
    (OUT/'equal_prior_diagnostic_summary.json').write_text(json.dumps(result,indent=2))
    (OUT/'equal_prior_config.json').write_text(json.dumps({
        'route_definitions':model.ROUTE_DEFINITIONS,'bfo_sigma_hz':4.3,'bfo_hard_limit_hz':8.6,
        'bto_sigmas_us':{'R1200':29,'R600':62},'range_gate_sigmas':2,'crossing_seconds':60,
        'fuel_window_utc':['2014-03-08T00:15:00Z','2014-03-08T00:19:00Z'],
        'first_R600_assumed_valid':True,'warmup_messages_after_first_R600':'excluded',
        'all_0019_BTO_BFO':'excluded','runs':RUNS},indent=2))
    pd.DataFrame(runs).to_csv(OUT/'run_comparison.csv',index=False)
    obs=model.Observations()
    obs.arcs[['timestamp_utc','source_row','channel_name','raw_bto_us','bto_us','bto_sigma_us','bfo_hz']].to_csv(OUT/'observation_selection.csv',index=False)
    return result


def style_table(table,size=9):
    table.auto_set_font_size(False);table.set_fontsize(size)
    for (i,j),cell in table.get_celld().items():
        cell.set_edgecolor('#d9e2e8');cell.set_linewidth(.5)
        if i==0:cell.set_facecolor('#e8f0f5');cell.set_text_props(weight='bold',color='#19394e')


def summary_page(summary):
    fig=plt.figure(figsize=(8.27,11.7),facecolor='white')
    fig.text(.07,.952,'MH370 | equal route priors',fontsize=21,weight='bold',color='#17384d')
    fig.text(.07,.923,'4.3 Hz BFO sensitivity and first-R600 restart condition',fontsize=11,color='#4a6575')
    textblock(fig,.07,.886,'The requested priors are applied. The sampled populations contain no complete surviving trajectories, so a normalized 00:11 density cannot be produced from these runs.',width=94,size=11,line=.024,color='#923c23')
    ax=fig.add_axes([.07,.713,.86,.106]);ax.axis('off')
    table=ax.table(cellText=[[LABELS[k],'1/3 (33.333...)'] for k in model.ROUTE_DEFINITIONS],
        colLabels=['Hypothesis','Prior probability'],cellLoc='left',colLoc='left',colWidths=[.69,.31],bbox=[0,0,1,1])
    style_table(table,10)
    textblock(fig,.07,.691,'IGOGU has 2/3 total prior probability. Within the IGOGU-only view, its two variants each begin with 1/2. These are prior weights; no posterior weights are inferred from the failed populations.',width=101,size=9.4,line=.018)
    fig.text(.07,.608,'What the larger runs found',fontsize=14,weight='bold',color='#17384d')
    rows=[]
    for run in summary['runs']:
        label=LABELS[run['route']]
        if run['route']=='p627':label+=' A' if run['name']=='prefix_large_p627' else ' B'
        rows.append([label,f"{run['initial_draws']:,}",str(run['prefix_survivors']),
            'Not reached' if run['first_call_survivors'] is None else '0'])
    ax=fig.add_axes([.07,.451,.86,.137]);ax.axis('off')
    table=ax.table(cellText=rows,colLabels=['Run','Initial draws','18:28 pass','First-call pass'],
        colWidths=[.42,.20,.17,.21],bbox=[0,0,1,1],cellLoc='left',colLoc='left');style_table(table,8.5)
    y=textblock(fig,.07,.429,'P627 has no joint early survivor. In run B, 39 paths pass the range, BFO and physical checks; all fail the additional nominal-arc crossing-time condition. Each IGOGU variant has early survivors, but none of its 90,000 first-call proposals reaches IGOGU before the inherited turn deadline. That deadline is an added route-prior condition, not rejection by call BFOs alone.',width=105,size=9.3,line=.018)
    y=textblock(fig,.07,y-.009,'BFO gates: +/-8.6 Hz, including every available receive BFO in both calls and the first R600 burst assumed valid. BTO gates: +/-58 us for ordinary R1200 and +/-124 us for corrected R600. The true path must cross each contact-time range locus within +/-60 seconds. Later restart warm-up messages and all 00:19 BTO/BFO remain excluded.',width=105,size=9.3,line=.018)
    y=textblock(fig,.07,y-.009,'Fuel exhaustion during 00:15-00:19 is enabled in the public-data aircraft/fuel model. These new runs stop before that selection: no new path has demonstrated the full set of satellite, route, performance and fuel criteria.',width=105,size=9.3,line=.018)
    y=textblock(fig,.07,y-.009,'Interpretation: this is a negative sampling result under the stated prior, not a proof of route impossibility. The 600-second speed-response prior and sparse control changes restrict the ability to accelerate after 18:28. IGOGU prefix effective sample sizes are approximately 1.3 and 51.9; repeating retained particles does not create independent support.',width=105,size=9.3,line=.018)
    fig.text(.07,.055,'Following pages show the requested three route views as geometry only. No posterior is painted.',fontsize=8.4,color='#4a6575')
    fig.text(.93,.023,'1 / 4',ha='right',fontsize=8,color='#67808e')
    return fig


def route_geometry(ax,which,labels=True):
    radar=np.degrees(model.RADAR)
    for key in which:
        r=model.ROUTE_DEFINITIONS[key];points=np.vstack([radar,np.array(r['points'])])
        ax.plot(points[:,1],points[:,0],color=COLORS[key],lw=1.2,ls='--',zorder=6)
        ax.scatter(points[1:,1],points[1:,0],s=17,color=COLORS[key],marker='D',zorder=7)
    ax.scatter(radar[1],radar[0],marker='*',s=65,color='#152c3c',zorder=8)
    if labels:
        fixes={}
        for key in which:
            for point,name in zip(model.ROUTE_DEFINITIONS[key]['points'],model.ROUTE_DEFINITIONS[key]['names']):
                fixes[name]=point
        for name,(lat,lon) in fixes.items():
            short=name.replace('FIR ','').replace('94:25E','94d25E')
            offset={'NILAM':(7,9),'SANOB':(-15,-15),'IGEBO':(-37,9),
                'POVUS':(-25,-24),'IGOGU':(7,9),'FIR 6N/94:25E':(-70,-8),
                'FIR 6N/92E':(7,9)}.get(name,(6,9))
            ax.annotate(short,(lon,lat),xytext=offset,textcoords='offset points',fontsize=6.5,
                bbox=dict(fc='white',ec='none',alpha=.88,pad=1),
                arrowprops=dict(arrowstyle='-',lw=.35,color='#79909a'),zorder=10)
        ax.annotate('Last radar',(radar[1],radar[0]),xytext=(7,-13),textcoords='offset points',fontsize=6.8)
    if 'igogu_south' in which:
        p=model.ROUTE_DEFINITIONS['igogu_south']['points'][-1]
        ax.plot([p[1],p[1]],[p[0],4.6],color=COLORS['igogu_south'],ls=':',lw=1.15,zorder=7)


def map_page(title,which,page):
    fig=plt.figure(figsize=(8.27,11.7),facecolor='white')
    fig.text(.07,.956,title,fontsize=20,weight='bold',color='#17384d')
    fig.text(.07,.928,'Requested route view | prior geometry and 00:11 range locus',fontsize=10.5,color='#4a6575')
    fig.text(.07,.897,'No complete selected trajectories; posterior density is undefined.',fontsize=10.5,weight='bold',color='#923c23')
    ax=fig.add_axes([.08,.20,.85,.66]);bounds=(75,113,-44,10);rings=land_polygons()
    draw_land(ax,rings,bounds);ax.set_facecolor('#fbfdfe')
    lat,lon=arc_curve(10000);ax.plot(lon,lat,color='#8c8995',lw=.85,ls='--',zorder=3)
    route_geometry(ax,which,False)
    ax.set(xlim=bounds[:2],ylim=bounds[2:],xlabel='Longitude east',ylabel='Latitude')
    ax.set_aspect(1/np.cos(np.radians(20)))
    ax.xaxis.set_major_locator(MultipleLocator(5));ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}°E'));ax.yaxis.set_major_formatter(FuncFormatter(degree_lat))
    ax.grid(lw=.4,color='#dde6eb');ax.tick_params(labelsize=8)
    ax.text(93,-13,'NO DENSITY ESTIMATE',ha='center',fontsize=13,weight='bold',color='#667884')
    ax.text(93,-15.3,'The blank map does not mean zero geographic probability.',ha='center',fontsize=7.5,color='#667884')
    ax.legend(handles=[Line2D([0],[0],color=COLORS[k],lw=1.3,ls='--',label=LABELS[k]) for k in which]+
        [Line2D([0],[0],color='#8c8995',lw=.9,ls='--',label='00:11 BTO locus at 10 km altitude')],
        loc='lower left',fontsize=7,framealpha=.97)
    inset=ax.inset_axes([.025,.692,.74,.28]);inset.set_zorder(20);ib=(91.2,97.6,4.25,8.5)
    draw_land(inset,rings,ib);route_geometry(inset,which,True)
    inset.set(xlim=ib[:2],ylim=ib[2:],facecolor='white');inset.set_aspect(1/np.cos(np.radians(6)))
    inset.grid(lw=.35,color='#dde6eb');inset.tick_params(labelsize=6)
    inset.set_title('Specified route geometry; lines are not sampled trajectories',loc='left',fontsize=7.3,pad=5)
    textblock(fig,.07,.13,'Every route leaf has prior weight 1/3. The IGOGU-only view groups two leaves (1/2 each within that group). The published boundary bends west at 6°N; a straight southward continuation from IGOGU is a distinct hypothesis. These coordinates use current publications and do not independently authenticate the 2014 boundary.',width=111,size=8.5,line=.016)
    fig.text(.07,.041,'No old 7 Hz ensemble has been substituted for the requested 4.3 Hz result.',fontsize=8.3,color='#4a6575')
    fig.text(.93,.023,f'{page} / 4',ha='right',fontsize=8,color='#67808e')
    return fig


if __name__=='__main__':
    summary=setup_summary();PDF.parent.mkdir(parents=True,exist_ok=True)
    figs=[summary_page(summary),map_page('Combined: three equal priors',list(model.ROUTE_DEFINITIONS),2),
        map_page('IGOGU variants only',['igogu_boundary','igogu_south'],3),map_page('P627 only',['p627'],4)]
    with PdfPages(PDF) as pdf:
        for fig in figs:pdf.savefig(fig)
    previews=ROOT/'tmp/pdfs/equal_prior_checks';previews.mkdir(parents=True,exist_ok=True)
    for i,fig in enumerate(figs,1):
        fig.savefig(previews/f'page_{i}.png',dpi=120);plt.close(fig)
    print(PDF)
