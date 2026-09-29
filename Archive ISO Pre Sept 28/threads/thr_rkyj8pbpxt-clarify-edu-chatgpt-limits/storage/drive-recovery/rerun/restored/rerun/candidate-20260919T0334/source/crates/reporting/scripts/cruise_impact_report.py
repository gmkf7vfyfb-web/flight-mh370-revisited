"""Render separately conditioned impact ensembles; never run flight inference."""
from __future__ import annotations
import argparse
import base64
import csv
import datetime as dt
import html
import gzip
import json
from pathlib import Path
import shlex

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from geographiclib.geodesic import Geodesic
from arc_density_report import area_grid, ranked_area, inverse, digest, draw_land, save_figure, scalar_quantiles

DEFAULT_CASE='r600-no-startup-offset'
LABELS={
 'neither-final-contact':'Neither final contact', 'r600-bto-only':'R600 BTO only',
 'r600-no-startup-offset':'R600 BTO + BFO; no startup offset',
 'r1200-bfo-no-startup-offset':'R1200 BFO only; no startup offset',
 'r600-bto-r1200-bfo-no-startup-offset':'R600 BTO + R1200 BFO; no startup offset',
 'both-sequential-no-startup-offset':'Both BFOs in sequence + R600 BTO; no startup offset',
 'r600-shared-startup':'R600 BTO + BFO; shared startup prior',
 'r1200-bfo-shared-startup':'R1200 BFO only; shared startup prior',
 'r600-bto-r1200-bfo-shared-startup':'R600 BTO + R1200 BFO; shared startup prior',
 'both-sequential-shared-startup':'Both BFOs in sequence + R600 BTO; shared startup prior',
}


def physical_metrics(source):
    """Geodesic displacement is a reporting statistic, not a motion equation."""
    result={}
    for line in (source/'continuations.jsonl').open():
        row=json.loads(line)
        if row.get('status')!='propagated':continue
        impact=row['transition']['impact']
        if impact is None:continue
        position=impact['point']['position'];contacts={c['id']:c for c in row['contacts']}
        last=contacts.get('m0019b')
        result[(row['family'],row['source_index'],row['draw'])]=dict(
            post_r1200_seconds=None if last is None else impact['point']['time']-last['aircraft']['time'],
            post_r1200_displacement_km=None if last is None else Geodesic.WGS84.Inverse(
                last['aircraft']['position']['latitude'],last['aircraft']['position']['longitude'],position['latitude'],position['longitude'])['s12']/1000)
    return result


def load_case(source, family, case, metrics, output):
    path=source/case['weights_file']
    if digest(path)!=case['weights_sha256']:raise ValueError('Conditional weights changed')
    rows=list(csv.DictReader(path.open()))
    impact=[r for r in rows if r['impact_latitude_deg'] and float(r['conditional_weight'])>0]
    total_weight=sum(float(r['conditional_weight']) for r in rows)
    if case['has_positive_supported_weight'] and abs(total_weight-1)>1e-8:raise ValueError('Weights do not sum to one')
    record=dict(name=case['name'],label=LABELS.get(case['name'],case['name']),diagnostics=case,
                impact_quantiles_05_50_95={},impact_sample_rows=len(impact),input_sha256=digest(path))
    if not impact:
        record.update(cells=[],latitude_edges=[],longitude_edges=[],cdf=[],impact_mass=0.)
        return record
    w=np.array([float(r['conditional_weight']) for r in impact]);mass=float(w.sum());w/=mass
    points=np.array([[float(r['impact_latitude_deg']),float(r['impact_longitude_deg'])] for r in impact])
    xe,ye,grid=area_grid(points,w,10.)
    latitude,longitude=inverse(xe,ye)
    iy,ix=np.nonzero(grid>0)
    record.update(impact_mass=mass,latitude_edges=latitude.tolist(),longitude_edges=longitude.tolist(),
                  cells=[[int(x),int(y),float(grid[y,x])] for y,x in zip(iy,ix)],
                  cell_area_km2=100.,ranked_impact_area_km2=ranked_area(grid,10.),
                  impact_weight_effective_rows=float(1/(w*w).sum()))
    cdf_edges=np.arange(-55,20.001,.05)
    order=np.argsort(points[:,0]);values=np.cumsum(w[order]);indices=np.searchsorted(points[order,0],cdf_edges,side='right')
    cdf=np.where(indices>0,values[np.maximum(0,indices-1)],0.)
    record['cdf']=[[float(x),float(y)] for x,y in zip(cdf_edges,cdf)]
    columns={'latitude_deg':'impact_latitude_deg','longitude_deg':'impact_longitude_deg',
             'true_airspeed_m_s':'impact_true_airspeed_m_s','vertical_speed_m_s':'impact_vertical_speed_m_s',
             'velocity_angle_deg':'impact_velocity_angle_deg','kinetic_energy_j':'impact_kinetic_energy_j',
             'vertical_energy_j':'impact_vertical_energy_j','displacement_from_exhaustion_nm':'displacement_from_exhaustion_nm'}
    for name,column in columns.items():record['impact_quantiles_05_50_95'][name]=scalar_quantiles(np.array([float(r[column]) for r in impact]),w)
    record['impact_quantiles_05_50_95']['minutes_after_0019']=scalar_quantiles(np.array([(float(r['impact_time_s'])-22631.)/60 for r in impact]),w)
    for name in ['post_r1200_seconds','post_r1200_displacement_km']:
        values=np.array([metrics[(family,int(r['source_index']),int(r['draw']))][name] if metrics[(family,int(r['source_index']),int(r['draw']))][name] is not None else np.nan for r in impact])
        valid=np.isfinite(values)
        record['impact_quantiles_05_50_95'][name]=scalar_quantiles(values[valid],w[valid]/w[valid].sum()) if valid.any() else None
        record[name+'_represented_impact_fraction']=float(w[valid].sum())
    record['regions']={name:float(w[mask].sum()) for name,mask in {
        'between_35S_and_38S':(points[:,0]>=-38)&(points[:,0]<-35),
        'north_of_35S':points[:,0]>=-35,'north_of_30S':points[:,0]>=-30}.items()}
    np.savez_compressed(output/(family+'--'+case['name']+'.npz'),longitude_projection_edges_km=xe,
                        latitude_projection_edges_km=ye,probability_given_computed_impact=grid,cell_area_km2=100.)
    return record


def family_figure(group, output):
    fig,axes=plt.subplots(1,2,figsize=(10.5,6.4),gridspec_kw={'width_ratios':[1,1.1]})
    selected=next(c for c in group['cases'] if c['name']==DEFAULT_CASE)
    ax=axes[0];draw_land(ax);ax.set_facecolor('#f1f6f9')
    if selected['cells']:
        lat=np.asarray(selected['latitude_edges']);lon=np.asarray(selected['longitude_edges'])
        grid=np.zeros((len(lat)-1,len(lon)-1))
        for x,y,m in selected['cells']:grid[y,x]=m/100
        shown=np.ma.masked_where(grid<=0,grid);top=grid.max()
        picture=ax.pcolormesh(lon,lat,shown,norm=LogNorm(vmin=max(top*1e-4,1e-12),vmax=top),cmap='magma_r',rasterized=True)
        fig.colorbar(picture,ax=ax,orientation='horizontal',pad=.14,label='Probability density per km²',fraction=.045)
    ax.set(xlim=(80,108),ylim=(-45,-25),xlabel='Longitude (°E)',ylabel='Latitude (°)',title='R600 BTO + BFO; no startup offset')
    ax.grid(alpha=.15);axes[1].set(xlim=(-43,-20),ylim=(0,1),xlabel='Impact latitude (°)',ylabel='Cumulative probability',title='Sensitivity to final-contact assumptions')
    for case in group['cases']:
        if not case['cdf']:continue
        values=np.array(case['cdf']);axes[1].plot(values[:,0],values[:,1],lw=1.2,label=case['label'])
    axes[1].grid(alpha=.2);axes[1].legend(fontsize=6.5,loc='lower right')
    fig.suptitle(group['name'].replace('-',' '),fontsize=12)
    fig.tight_layout(rect=(0,.1,1,.94))
    d=selected['diagnostics']
    fig.text(.5,.016,f"Conditional on computed impacts and this force/polar model; 10 × 10 km cells, no added smoothing.\n"
             f"Incoming probability with uncomputed selected-contact likelihood: {100*d['fraction_of_fuel_conditioned_prior_with_uncomputed_likelihood']:.2f}%; "
             f"impact fraction within scored support: {100*selected['impact_mass']:.2f}%.\n"
             'Control priors and attached-flow polars are conditional approximations; body attitude and acoustic coupling are not inferred.',ha='center',fontsize=7.5)
    return save_figure(fig,output,group['name'])


def add_numerical_comparison(groups, source, comparison):
    prior=json.loads((source/'summary.json').read_text());other=json.loads((comparison/'summary.json').read_text())
    if other['status']!='conditional_final_contact_sensitivities':raise ValueError('Incomplete numerical comparison')
    a=prior['source_configuration'];b=other['source_configuration']
    for key in ['source_runs','powered_step_s','final_contacts']:
        if a[key]!=b[key]:raise ValueError('Numerical comparison changed the physical source')
    for key in a['kernel']:
        if key!='families' and a['kernel'][key]!=b['kernel'][key]:raise ValueError('Terminal model changed')
    definitions={f['name']:f for f in a['kernel']['families']}
    for f in b['kernel']['families']:
        if definitions.get(f['name'])!=f:raise ValueError('Control prior changed')
    index={(f['name'],c['name']):c for f in other['families'] for c in f['cases']}
    for group in groups:
        for case in group['cases']:
            c=index.get((group['name'],case['name']))
            if c is None:continue
            path=comparison/c['weights_file']
            if digest(path)!=c['weights_sha256']:raise ValueError('Comparison weights changed')
            rows=[r for r in csv.DictReader(path.open()) if r['impact_latitude_deg'] and float(r['conditional_weight'])>0]
            values=[];difference=None
            if rows and case['cdf']:
                lat=np.array([float(r['impact_latitude_deg']) for r in rows]);w=np.array([float(r['conditional_weight']) for r in rows]);w/=w.sum();order=np.argsort(lat);cum=np.cumsum(w[order]);edges=np.array(case['cdf'])[:,0];i=np.searchsorted(lat[order],edges,side='right');cdf=np.where(i>0,cum[np.maximum(i-1,0)],0.)
                values=[[float(x),float(y)] for x,y in zip(edges,cdf)];difference=float(np.max(np.abs(cdf-np.array(case['cdf'])[:,1])))
            case['numerical_comparison']=dict(cdf=values,maximum_latitude_cdf_difference=difference,
                row_weight_effective_count=c['row_weight_effective_count'],largest_initial_ancestor_weight=c['largest_initial_ancestor_weight'],
                log_known_evidence_difference=c['log_known_evidence_contribution']-case['diagnostics']['log_known_evidence_contribution'],
                incoming_uncomputed_likelihood_fraction=c['fraction_of_fuel_conditioned_prior_with_uncomputed_likelihood'],weights_sha256=digest(path))


def report(source, output, inline, comparison=None):
    output.mkdir(parents=True,exist_ok=True)
    summary=json.loads((source/'summary.json').read_text())
    if summary['status']!='conditional_final_contact_sensitivities':raise ValueError('Incomplete source')
    physical_source=Path(summary['source']);metrics=physical_metrics(physical_source)
    groups=[]
    plt.rcParams.update({'svg.fonttype':'none','font.size':10})
    for family in summary['families']:
        group=dict(name=family['name'],draws=family['draws'],cases=[load_case(source,family['name'],c,metrics,output) for c in family['cases']])
        family_figure(group,output);groups.append(group)
    if comparison is not None:add_numerical_comparison(groups,source,comparison)
    result=dict(generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='conditional impact sensitivity; model support and Monte Carlo limits retained',
                groups=groups,source_summary_sha256=digest(source/'summary.json'),report_source_sha256=digest(__file__),
                source=str(source),selected_case=DEFAULT_CASE,observations=summary['source_summary']['contacts'],
                limitations=summary['limitations'],numerical_comparison_source=None if comparison is None else str(comparison),
                source_initial_candidates=sum(s['initial_candidates'] for s in summary['source_summary']['sources']),
                terminal_weather_sha256=summary['source_summary'].get('terminal_weather_sha256'),
                terminal_weather_altitude_limit_ft=summary['source_configuration']['kernel']['environment']['maximum_pressure_altitude_ft'])
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    write_browser(result,output,inline)
    command=shlex.join(['python',str(Path(__file__).resolve()),'--source',str(source),'--output',str(output),'--inline-output',str(inline)]+([] if comparison is None else ['--proposal-comparison',str(comparison)]))
    (output/'README.md').write_text('# Conditional impact comparison\n\n'+command+'\n\nEach aerodynamic/control family and final-contact case is separate. Files contain impact-conditioned10km-cell probabilities; model-domain losses and uncomputed likelihood mass remain in summary.json. Per-family vector PDFs/SVGs show the requested R600-first case and all-case latitude sensitivity. ISO HTML provides interactive access to every computed case.\n')
    print(json.dumps(dict(families=len(groups),cases=sum(len(g['cases']) for g in groups),inline_bytes=inline.stat().st_size)))


def write_browser(result,output,inline):
    coast=json.loads((Path(__file__).parents[1]/'assets/ne_110m_land.geojson').read_text())
    polygons=[]
    for feature in coast['features']:
        geometry=feature.get('geometry') or {}
        parts=[geometry['coordinates']] if geometry.get('type')=='Polygon' else geometry.get('coordinates',[])
        for rings in parts:
            if rings and any(65<x<130 and -60<y<20 for x,y in rings[0]):polygons.append(rings[0])
    # Browser drawing needs fewer digits than the reproducibility artifacts.
    # Seven significant digits preserve tiny positive masses without imposing
    # a likelihood floor and keep all 120 maps within ISO's document limit.
    def display_precision(value):
        if isinstance(value, float):return float(format(value, '.7g'))
        if isinstance(value, list):return [display_precision(v) for v in value]
        if isinstance(value, dict):return {k:display_precision(v) for k,v in value.items()}
        return value
    payload=display_precision(dict(groups=result['groups'],coast=polygons))
    packed=base64.b64encode(gzip.compress(json.dumps(payload,separators=(',',':')).encode(),mtime=0)).decode()
    rows=''
    for group in result['groups']:
        c=next(c for c in group['cases'] if c['name']==DEFAULT_CASE);d=c['diagnostics']
        q=c['impact_quantiles_05_50_95'].get('latitude_deg')
        lat='—' if q is None else f'{q[0]:.1f} to {q[2]:.1f}'
        rows+=f'<tr><td>{html.escape(group["name"])}</td><td>{group["draws"]:,}</td><td>{max(0.,100*d["fraction_of_fuel_conditioned_prior_with_uncomputed_likelihood"]):.2f}%</td><td>{100*c["impact_mass"]:.1f}%</td><td>{lat}</td><td>{c.get("impact_weight_effective_rows",0):.1f}</td></tr>'
    parent_note = ('This is the full broader million-candidate cruise pool.' if result.get('source_initial_candidates',0)>=1020000 else 'The separate cruise report includes additional candidates; they have not been substituted into this calculation.')
    body='''<h1>From 00:11 to impact: conditional comparisons</h1>
<p>These impact samples use the saved '''+f"{result.get('source_initial_candidates',680000):,}"+'''-candidate broader cruise population. '''+parent_note+'''</p>
<p>Each map starts from the same saved cruise estimate and carries fuel uncertainty into a sampled exhaustion time. Select a terminal control/aerodynamic model and a final-contact assumption. These alternatives are kept separate.</p>
<p><strong>These are provisional, conditional impact distributions.</strong> They describe the modelled impacts that can be calculated. The probability entering an uncomputed model region is reported alongside each case. A large nominal sample does not make a few heavily weighted outcomes precise.</p>
<label>Terminal model<select id="family"></select></label><label>Final-contact assumption<select id="case"></select></label>
<label>Map view<select id="view"><option value="south">Southern concentration</option><option value="all">Regional context</option></select></label>
<p id="status">Loading the saved comparison data…</p><div id="stats"></div>
<section><canvas id="map" width="1000" height="760" aria-label="Conditional impact probability density map"></canvas><p id="mapnote"></p></section>
<section><canvas id="cdf" width="1000" height="540" aria-label="Impact latitude cumulative probabilities for final-contact cases"></canvas><p>All curves here use the selected terminal model. The selected contact case is drawn more heavily. Where present, dashed black shows a second run using a corrected computational proposal and the same physical prior. Curves are conditional on computed impacts.</p><p id="numerical"></p></section>
<details><summary>R600-first comparison across all terminal models</summary><div class="scroll"><table><tr><th>Terminal model</th><th>Continuation draws</th><th>Uncomputed likelihood: incoming mass</th><th>Impact mass within scored support</th><th>Impact latitude 5–95% (°)</th><th>Effective weighted impact rows</th></tr>'''+rows+'''</table></div><p>Effective row counts describe weight concentration and do not count independent posterior samples.</p></details>
<details><summary>What each condition means</summary>
<p>The R600 record is at 00:19:29.416 UTC: BFO 182 Hz and BTO 23,000 minus the ordinary 4,600 μs channel correction, giving 18,400 μs. The R1200 BFO is −2 Hz at 00:19:37.443 UTC. Its anomalous BTO is excluded. The two BFOs share the bias uncertainty retained at 00:11; the sequential case updates this uncertainty jointly.</p>
<p>The no-offset case uses the recorded BFOs with the declared 7 Hz Gaussian noise. The startup alternative assumes a uniform second offset from 17 to 130 Hz and a uniform first-minus-second offset from 0 to 6 Hz. This joint density is an explicit sensitivity assumption within Holland’s historical bounds, not a probability law established by the paper. See <a href="https://arxiv.org/pdf/1702.02432v3">Holland, arXiv v3, pages 7–8</a>. No posterior probability is assigned to either startup model.</p>
<p>The control alternatives retain initial trim, approach the polar’s best-glide setting, or approach one, three or six sampled lift/bank targets at finite declared rates. Positive-lift and signed-lift cases are distinct. OpenAP 2.6 and the published 2020 polar are separate attached-flow approximations. They do not calibrate B777 post-stall or breakup behaviour. The supplied run configuration records every range and rate.</p>
<p>The selected terminal weather grid extends to '''+f"{result.get('terminal_weather_altitude_limit_ft',43000):,.0f}"+''' ft. Where an altitude extension is used, every original cruise weather value is checked for exact preservation. Weather-grid exits and near-vertical coordinate limits are unresolved model outcomes. An impact before a selected radio contact instead has zero likelihood for that case. SATCOM weights condition on an available transmission; APU timing, electrical restoration and outage cause are not scored by these kinematic cases. Pressure altitude is used as geometric height, and the sampled wind residual is held fixed during terminal flight.</p>
<p>The impact angle is the direction of motion relative to the horizontal, not aircraft body pitch. Kinetic energy does not determine acoustic energy without a separate water-entry and coupling model. Drift, Pléiades, hydroacoustics and searched-area evidence have not been applied to these maps.</p></details>
<p class="stamp">Generated '''+html.escape(result['generated_utc'])+'''. Raw case weights, probability grids, per-family PDF/SVG figures, input hashes and reproduction commands are retained with the report.</p>'''
    css='body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.55 system-ui,sans-serif}main{max-width:1060px;margin:auto;padding:18px}h1{font-size:1.65em}label{display:block;margin:12px 0}select{display:block;width:100%;max-width:900px;font:inherit;padding:9px;background:white;color:inherit}section,details{padding:12px;margin:18px 0;background:white}canvas{display:block;width:100%;height:auto}.scroll{overflow-x:auto}table{border-collapse:collapse;font-size:13px;width:100%}td,th{padding:8px;border-bottom:1px solid #c9d4db;text-align:right}td:first-child,th:first-child{text-align:left}.stamp{font-size:12px;color:#667980}.stat{display:inline-block;margin:5px 15px 5px 0}#status{font-weight:600}'
    script=r'''
const packed="PACKED_DATA";
const family=document.getElementById('family'),caseSelect=document.getElementById('case'),view=document.getElementById('view');
let data;
const fmt=(x,n=1)=>Number.isFinite(x)?(Math.abs(x)<.5*10**(-n)?0:x).toFixed(n):'—';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const colours=['#263c50','#d28521','#1b79a3','#965296','#287e65','#bc4034','#687b21','#6259aa','#a46c44','#bf6685'];
function group(){return data.groups[Number(family.value)]}
function selected(){return group().cases[Number(caseSelect.value)]}
function axes(canvas,limits,title,xlabel,ylabel){
 const c=canvas.getContext('2d');c.clearRect(0,0,canvas.width,canvas.height);c.fillStyle='white';c.fillRect(0,0,canvas.width,canvas.height);
 const pad={l:90,r:50,t:60,b:110},w=canvas.width-pad.l-pad.r,h=canvas.height-pad.t-pad.b;
 const [xmin,xmax,ymin,ymax]=limits;const x=v=>pad.l+(v-xmin)/(xmax-xmin)*w,y=v=>pad.t+h-(v-ymin)/(ymax-ymin)*h;
 c.fillStyle='#193240';c.font='24px system-ui';c.textAlign='center';c.fillText(title,canvas.width/2,31);
 c.font='20px system-ui';for(let i=0;i<=5;i++){let xx=xmin+(xmax-xmin)*i/5,yy=ymin+(ymax-ymin)*i/5;
 c.strokeStyle='#d6e0e6';c.beginPath();c.moveTo(x(xx),pad.t);c.lineTo(x(xx),pad.t+h);c.stroke();
 c.beginPath();c.moveTo(pad.l,y(yy));c.lineTo(pad.l+w,y(yy));c.stroke();c.fillStyle='#193240';c.textAlign='center';c.fillText(fmt(xx),x(xx),pad.t+h+30);c.textAlign='right';c.fillText(fmt(yy),pad.l-12,y(yy)+7);}
 c.textAlign='center';c.fillText(xlabel,pad.l+w/2,canvas.height-55);c.save();c.translate(26,pad.t+h/2);c.rotate(-Math.PI/2);c.fillText(ylabel,0,0);c.restore();
 return {c,x,y,pad,w,h};
}
function mapColour(t){t=Math.max(0,Math.min(1,t));const a=[251,237,166],b=[82,26,106];return `rgb(${a.map((v,i)=>Math.round(v+(b[i]-v)*t)).join(',')})`;}
function render(){
 const g=group(),s=selected(),d=s.diagnostics,q=s.impact_quantiles_05_50_95;
 document.getElementById('status').textContent=s.label;
 const ref=s.numerical_comparison;
 document.getElementById('numerical').textContent=ref?'Independent guided run for this case: effective weighted rows '+fmt(ref.row_weight_effective_count)+', compared with '+fmt(d.row_weight_effective_count)+' in the first run. Maximum latitude CDF difference: '+fmt(100*ref.maximum_latitude_cdf_difference)+' percentage points. The control-proposal test gave limited improvements for the two-BFO sequence; those narrow distributions remain unresolved.':'';
 const range=(name,scale=1)=>q[name]?q[name].map(x=>fmt(x/scale)).join(' / '):'—';
 document.getElementById('stats').innerHTML=`<p><span class="stat">Uncomputed selected-contact likelihood: <b>${fmt(100*d.fraction_of_fuel_conditioned_prior_with_uncomputed_likelihood,2)}%</b> of incoming fuel-conditioned probability</span><span class="stat">Computed impact mass within scored support: <b>${fmt(100*s.impact_mass)}%</b></span><span class="stat">Effective weighted impact rows: <b>${fmt(s.impact_weight_effective_rows)}</b></span></p><p>Impact 5th / median / 95th percentiles: latitude <b>${range('latitude_deg')}°</b>; time after 00:19:00 <b>${range('minutes_after_0019')} min</b>; true airspeed <b>${range('true_airspeed_m_s')} m/s</b>; velocity angle below horizontal <b>${range('velocity_angle_deg')}°</b>; kinetic energy <b>${range('kinetic_energy_j',1e9)} GJ</b>.</p><p>For paths reaching the R1200 time, subsequent displacement is <b>${range('post_r1200_displacement_km')} km</b> and subsequent duration <b>${range('post_r1200_seconds',60)} min</b>. This statistic covers ${fmt(100*(s.post_r1200_seconds_represented_impact_fraction||0))}% of this case’s computed impact probability.</p>`;
 const limits=view.value==='south'?[80,108,-45,-25]:[65,130,-55,15];
 const a=axes(document.getElementById('map'),limits,'Conditional impact probability density','Longitude (°E)','Latitude (°)');const {c,x,y,pad,w,h}=a;
 c.save();c.beginPath();c.rect(pad.l,pad.t,w,h);c.clip();c.fillStyle='#f1f6f9';c.fillRect(pad.l,pad.t,w,h);
 for(const ring of data.coast){c.beginPath();ring.forEach(([lon,lat],i)=>i?c.lineTo(x(lon),y(lat)):c.moveTo(x(lon),y(lat)));c.closePath();c.fillStyle='#e2e4d9';c.fill();c.strokeStyle='#9ea797';c.lineWidth=.6;c.stroke();}
 const top=s.cells.reduce((m,v)=>Math.max(m,v[2]/100),1e-15),low=top*1e-4;
 for(const [ix,iy,m] of s.cells){const density=m/100;c.fillStyle=mapColour((Math.log10(density)-Math.log10(low))/4);c.fillRect(x(s.longitude_edges[ix]),y(s.latitude_edges[iy+1]),x(s.longitude_edges[ix+1])-x(s.longitude_edges[ix])+.4,y(s.latitude_edges[iy])-y(s.latitude_edges[iy+1])+.4);}
 c.restore();for(let i=0;i<200;i++){c.fillStyle=mapColour(i/199);c.fillRect(270+i*2.3,696,2.5,14);}c.font='17px system-ui';c.fillStyle='#193240';c.textAlign='left';c.fillText(low.toExponential(1),190,710);c.textAlign='right';c.fillText(top.toExponential(1)+' per km²',910,710);
 document.getElementById('mapnote').textContent='10 × 10 km equal-area cells; no added smoothing. Logarithmic colour scale spanning four orders of magnitude; lighter positive cells remain in the saved grid. The map is normalized within computed impacts. Largest initial flight ancestor: '+fmt(100*d.largest_initial_ancestor_weight)+'% of scored probability. Browser numbers retain seven significant digits; saved grids and weights retain full precision. A sea-floor search probability has not yet been calculated.';
 const ca=axes(document.getElementById('cdf'),[-45,-20,0,1],'Final-contact sensitivity within this terminal model','Impact latitude (°)','Cumulative probability');
 ca.c.save();ca.c.beginPath();ca.c.rect(ca.pad.l,ca.pad.t,ca.w,ca.h);ca.c.clip();
 g.cases.forEach((v,i)=>{ca.c.strokeStyle=colours[i%colours.length];ca.c.lineWidth=i===Number(caseSelect.value)?4:1.4;ca.c.beginPath();v.cdf.forEach(([xx,yy],j)=>j?ca.c.lineTo(ca.x(xx),ca.y(yy)):ca.c.moveTo(ca.x(xx),ca.y(yy)));ca.c.stroke();});ca.c.restore();
 if(ref&&ref.cdf.length){ca.c.save();ca.c.beginPath();ca.c.rect(ca.pad.l,ca.pad.t,ca.w,ca.h);ca.c.clip();ca.c.strokeStyle='#111';ca.c.lineWidth=2.5;ca.c.setLineDash([8,6]);ca.c.beginPath();ref.cdf.forEach(([xx,yy],j)=>j?ca.c.lineTo(ca.x(xx),ca.y(yy)):ca.c.moveTo(ca.x(xx),ca.y(yy)));ca.c.stroke();ca.c.restore();}
 const legend=g.cases.map((v,i)=>`<span style="color:${colours[i%colours.length]};display:block">${i===Number(caseSelect.value)?'<b>':''}${esc(v.label)}${i===Number(caseSelect.value)?'</b>':''}</span>`).join('');
 let node=document.getElementById('legend');if(!node){node=document.createElement('div');node.id='legend';document.getElementById('cdf').after(node);}node.innerHTML=legend;
}
async function start(){
 const bytes=Uint8Array.from(atob(packed),c=>c.charCodeAt(0));const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));data=JSON.parse(await new Response(stream).text());
 family.innerHTML=data.groups.map((g,i)=>`<option value="${i}">${esc(g.name.replaceAll('-',' '))} · ${g.draws.toLocaleString()} continuation draws</option>`).join('');
 let index=data.groups.findIndex(g=>g.name==='openap26-initial-trim');family.value=String(Math.max(0,index));
 function choose(){const previous=caseSelect.value;caseSelect.innerHTML=group().cases.map((s,i)=>`<option value="${i}">${esc(s.label)}</option>`).join('');caseSelect.value=previous||String(group().cases.findIndex(c=>c.name==='r600-no-startup-offset'));render();}
 family.addEventListener('change',choose);caseSelect.addEventListener('change',render);view.addEventListener('change',render);choose();
}
start().catch(e=>{document.getElementById('status').textContent='Interactive data could not load in this browser: '+e.message+'. The comparison table below remains available.';});
'''.replace('PACKED_DATA',packed)
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 conditional impact comparison</title><style>'+css+'</style><main>'+body+'</main><script>'+script+'</script></html>'
    if len(document.encode())>5*1024**2:raise ValueError('Inline report exceeds 5 MiB')
    inline.write_text(document);(output/'index.html').write_text(document)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--inline-output',type=Path,required=True)
    p.add_argument('--proposal-comparison',type=Path)
    a=p.parse_args();report(a.source,a.output,a.inline_output,a.proposal_comparison)
