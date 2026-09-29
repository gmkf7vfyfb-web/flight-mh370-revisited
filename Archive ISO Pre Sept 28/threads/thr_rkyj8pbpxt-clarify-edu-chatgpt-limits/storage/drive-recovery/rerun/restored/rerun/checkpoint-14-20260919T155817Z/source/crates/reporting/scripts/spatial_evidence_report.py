"""Report conditional transport evidence applied by the central runner."""
from __future__ import annotations
import argparse, base64, datetime as dt, gzip, html, json, shlex
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from arc_density_report import area_grid, inverse, ranked_area, scalar_quantiles, digest, draw_land, save_figure
from cruise_impact_report import LABELS, DEFAULT_CASE

MODEL_LABELS = {
    'cmems-nine-episodes':'Nine debris episodes: GLORYS12/WAVERYS',
    'cmems-flaperon-stokes-0p5':'Flaperon only: surface Stokes ×0.5',
    'cmems-flaperon-stokes-1p0':'Flaperon only: surface Stokes ×1.0',
    'cmems-flaperon-stokes-1p5':'Flaperon only: surface Stokes ×1.5',
    'pleiades-bran2016':'Pléiades identity hypothesis: BRAN2016',
    'pleiades-oscar_v2_final':'Pléiades identity hypothesis: OSCAR',
    'pleiades-glorys12_waverys':'Pléiades identity hypothesis: GLORYS12/WAVERYS',
}

def cdf(points, weights):
    order=np.argsort(points[:,0]); edges=np.arange(-55,15.001,.1)
    cum=np.cumsum(weights[order]);i=np.searchsorted(points[order,0],edges,side='right')
    return [[float(x),float(y)] for x,y in zip(edges,np.where(i>0,cum[np.maximum(0,i-1)],0.))]

def load(entry, output):
    root=Path(entry['output']);path=root/'conditional-spatial-sensitivity.json'
    manifest=json.loads((root/'run-manifest.json').read_text())
    if digest(path)!=manifest['output_sha256'][path.name]:raise ValueError('Surface output changed')
    source=json.loads(path.read_text());p=source.pop('particle_values')
    points=np.array([[r['latitude_deg'],r['longitude_deg']] for r in p])
    baseline=np.array([r['baseline_weight'] for r in p]);w=np.array([r['conditional_weight'] for r in p])
    if max(abs(w.sum()-1),abs(baseline.sum()-1))>1e-10:raise ValueError('Spatial weights not normalized')
    xe,ye,grid=area_grid(points,w,10.);lat,lon=inverse(xe,ye);iy,ix=np.nonzero(grid>0)
    value=dict(terminal_family=entry['terminal_family'],contact_case=entry['contact_case'],evidence_model=entry['evidence_model'],
               model_label=MODEL_LABELS[entry['evidence_model']],contact_label=LABELS[entry['contact_case']],
               source_summary_sha256=digest(path),diagnostics=source,
               cells=[[int(x),int(y),float(grid[y,x])] for y,x in zip(iy,ix)],latitude_edges=lat.tolist(),longitude_edges=lon.tolist(),
               baseline_cdf=cdf(points,baseline),conditional_cdf=cdf(points,w),
               baseline_latitude_quantiles=scalar_quantiles(points[:,0],baseline),conditional_latitude_quantiles=scalar_quantiles(points[:,0],w),
               maximum_latitude_cdf_change=float(np.max(np.abs(np.array(cdf(points,w))[:,1]-np.array(cdf(points,baseline))[:,1]))),
               ranked_area_km2=ranked_area(grid,10.))
    for name,weights in [('baseline',baseline),('conditional',w)]:
        value[name+'_regions']={label:float(weights[mask].sum()) for label,mask in {
            'between_35S_and_38S':(points[:,0]>=-38)&(points[:,0]<-35),'north_of_35S':points[:,0]>=-35,'north_of_30S':points[:,0]>=-30}.items()}
    np.savez_compressed(output/(entry['name']+'.npz'),probability_given_computed_impact_and_surface_support=grid,
                        cell_area_km2=100.,longitude_projection_edges_km=xe,latitude_projection_edges_km=ye)
    return value

def figure(family, values, category, output):
    cases=[v for v in values if v['terminal_family']==family and v['contact_case']==DEFAULT_CASE]
    if not cases:return
    selected=next((v for v in cases if v['evidence_model']=='cmems-nine-episodes'),cases[0])
    fig,axes=plt.subplots(1,2,figsize=(10.5,6.5));ax=axes[0];draw_land(ax)
    grid=np.zeros((len(selected['latitude_edges'])-1,len(selected['longitude_edges'])-1))
    for x,y,m in selected['cells']:grid[y,x]=m/100
    top=grid.max();pic=ax.pcolormesh(selected['longitude_edges'],selected['latitude_edges'],np.ma.masked_where(grid<=0,grid),
        cmap='magma_r',norm=LogNorm(vmin=max(top*1e-4,1e-12),vmax=top),rasterized=True)
    fig.colorbar(pic,ax=ax,orientation='horizontal',pad=.14,fraction=.045,label='Conditional probability density per km²')
    ax.set(xlim=(80,108),ylim=(-45,-25),xlabel='Longitude (°E)',ylabel='Latitude (°)',title=selected['model_label'],facecolor='#f1f6f9');ax.grid(alpha=.15)
    base=np.array(selected['baseline_cdf']);axes[1].plot(base[:,0],base[:,1],color='#222',lw=2,label='Flight + fuel + R600')
    for v in cases:
        xy=np.array(v['conditional_cdf']);axes[1].plot(xy[:,0],xy[:,1],lw=1.4,label=v['model_label'])
    axes[1].set(xlim=(-43,-20),ylim=(0,1),xlabel='Impact latitude (°)',ylabel='Cumulative probability',title='Separate evidence conditions')
    axes[1].grid(alpha=.2);axes[1].legend(fontsize=7,loc='lower right')
    fig.suptitle(family.replace('-',' ')+' · R600 BTO + BFO, no startup offset',fontsize=11)
    fig.tight_layout(rect=(0,.11,1,.94));d=selected['diagnostics']
    caption=('Different debris evidence sets are labelled; only the three flaperon curves isolate Stokes response.' if category=='drift' else 'Each curve assumes one of the 12 selected image objects is associated with MH370; identity is unproved.')
    fig.text(.5,.015,caption+'\n'+f"Surface-supported parent impact mass: {100*d['supported_baseline_mass']:.2f}%; conditional weight effective rows: {d['conditional_effective_sample_size']:.1f}.\n"
             '10 × 10 km cells; no added smoothing. Conditions on computed impacts and native surface support; source calibration and Monte Carlo limits apply.',ha='center',fontsize=7.5)
    save_figure(fig,output,category+'--'+family)

def browser(values, category, output, inline):
    # The two debris evidence sets are scientifically distinct and together
    # exceed ISO's inline document limit. Give the matched Stokes experiment
    # its own companion view while retaining every case in the saved report.
    if category=='drift' and any(v['evidence_model']=='cmems-nine-episodes' for v in values) and any(v['evidence_model'].startswith('cmems-flaperon') for v in values):
        companion=inline.with_name('mh370-stokes-comparison.html')
        browser([v for v in values if v['evidence_model'].startswith('cmems-flaperon')],category,output,companion)
        (output/'stokes.html').write_bytes(companion.read_bytes())
        values=[v for v in values if v['evidence_model']=='cmems-nine-episodes']
    # Full precision remains in summary.json, weight CSVs and NPZ grids.
    def compact(x, digits):
        if isinstance(x,float):return float(format(x,f'.{digits}g'))
        if isinstance(x,list):return [compact(v,digits) for v in x]
        if isinstance(x,dict):return {k:compact(v,digits) for k,v in x.items()}
        return x
    for digits in [7,6]:
        payload=base64.b64encode(gzip.compress(json.dumps(compact(values,digits),separators=(',',':')).encode(),mtime=0)).decode()
        if len(payload)<5*1024**2-20000:break
    title='Ocean drift and the broader flight estimate' if category=='drift' else 'Pléiades conditional object comparisons'
    explanation=('The nine-episode case uses the broader GLORYS12/WAVERYS debris-recovery surface. The three Stokes cases use the flaperon and its conditional isotope screen only. Compare those three with each other when assessing Stokes response. They are not additional independent observations to multiply together.' if category=='drift' else 'These alternatives assume exactly one latent association among 12 selected, highly rated Pléiades objects, with equal association weights. BRAN2016, OSCAR and GLORYS12/WAVERYS are separate transport hypotheses. Object identity has not been established; none of these maps turns an image object into a confirmed MH370 observation.')
    body=f'''<h1>{title}</h1><p>{explanation}</p>
<p>Each comparison starts from one named flight, fuel and final-contact estimate. The additional transport likelihood is applied once. These are conditional sensitivities; source calibration and finite sampling remain limitations.</p>
<label>Terminal model<select id="family"></select></label><label>Final contacts<select id="contact"></select></label><label>Additional evidence model<select id="evidence"></select></label>
<p id="status">Loading saved comparison data…</p><div id="stats"></div>
<canvas id="map" width="1000" height="700"></canvas><p>10 × 10 km equal-area cells, no added smoothing. Colour shows log probability density per km² within computed impacts and surface support. Full probability grids retain small positive cells.</p>
<canvas id="cdf" width="1000" height="540"></canvas><p>Black: flight, fuel and selected final contacts. Blue: additionally conditioned on the selected transport surface.</p>
<details><summary>Conditions and missing information</summary><div id="limits"></div>
<p>Stored transport surfaces start at 00:19:00. Applying them to impacts in the following minutes approximates the effect of that release-time difference. It has not been calibrated here. The maximum source-time allowance in this comparison is two hours; the actual range for each case is shown above.</p>
<p>Ocean surfaces use their supplied nearest-source rule, within 75 nautical miles of a sampled source location. This is an approximation to a two-dimensional impact likelihood. Pléiades uses its native grid boundary and the nearest node within five nautical miles. Neither is extrapolated. Geographic or numerical source gaps remain unassessed, rather than receiving zero or neutral likelihood.</p>
<p>No additional likelihood floor or subjective mixture between transport families is introduced. Existing floors, encounter bandwidths, object-response and detection assumptions inside the source models remain visible limitations. Effective row counts measure concentration and do not count independent flight ancestors.</p>
<p>These maps have not been conditioned on searched-area evidence and do not establish an operational search plan. The R600-only and both-BFO terminal cases have different numerical support; that uncertainty is inherited. Browser drawing uses {digits} significant digits; the saved calculations and grids retain full precision.</p></details>'''
    css='body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.5 system-ui,sans-serif}main{max-width:1060px;margin:auto;padding:18px}h1{font-size:1.65em}label{display:block;margin:12px 0}select{display:block;width:100%;font:inherit;padding:9px;background:white;color:inherit}canvas{display:block;width:100%;height:auto;background:white;margin-top:24px}details{padding:15px;margin:20px 0;background:white}#status{font-weight:600}'
    js=r'''
const packed="PACKED";let data;
const family=document.getElementById('family'),contact=document.getElementById('contact'),evidence=document.getElementById('evidence');
const fmt=(x,n=1)=>Number.isFinite(x)?(Math.abs(x)<.5*10**(-n)?0:x).toFixed(n):'—';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function options(node,values,label){const old=node.value;node.innerHTML=values.map(v=>`<option value="${esc(v)}">${esc(label(v))}</option>`).join('');node.value=values.includes(old)?old:values[0];}
function axes(id,box,title){const cv=document.getElementById(id),c=cv.getContext('2d'),p={l:90,r:50,t:60,b:95},w=cv.width-p.l-p.r,h=cv.height-p.t-p.b;
 c.clearRect(0,0,cv.width,cv.height);c.fillStyle='white';c.fillRect(0,0,cv.width,cv.height);const [a,b,d,e]=box,x=v=>p.l+(v-a)/(b-a)*w,y=v=>p.t+h-(v-d)/(e-d)*h;
 c.font='23px system-ui';c.fillStyle='#193240';c.textAlign='center';c.fillText(title,cv.width/2,32);c.font='19px system-ui';
 for(let i=0;i<=5;i++){const xx=a+(b-a)*i/5,yy=d+(e-d)*i/5;c.strokeStyle='#d9e2e8';c.beginPath();c.moveTo(x(xx),p.t);c.lineTo(x(xx),p.t+h);c.stroke();c.beginPath();c.moveTo(p.l,y(yy));c.lineTo(p.l+w,y(yy));c.stroke();c.fillStyle='#193240';c.textAlign='center';c.fillText(fmt(xx),x(xx),p.t+h+30);c.textAlign='right';c.fillText(fmt(yy),p.l-12,y(yy)+7);}
 c.textAlign='center';c.fillText(id==='map'?'Longitude (°E)':'Impact latitude (°)',p.l+w/2,cv.height-38);c.save();c.translate(25,p.t+h/2);c.rotate(-Math.PI/2);c.fillText(id==='map'?'Latitude (°)':'Cumulative probability',0,0);c.restore();return {c,x,y,p,w,h};}
function colour(t){t=Math.max(0,Math.min(1,t));return `rgb(${[251,237,166].map((v,i)=>Math.round(v+([82,26,106][i]-v)*t)).join(',')})`;}
function selected(){return data.find(v=>v.terminal_family===family.value&&v.contact_case===contact.value&&v.evidence_model===evidence.value);}
function render(){const s=selected();if(!s)throw Error('No selected result');const d=s.diagnostics;
 document.getElementById('status').textContent=s.model_label+' · '+s.contact_label;
 document.getElementById('stats').innerHTML=`<p>Surface-supported parent impact probability: <b>${fmt(100*d.supported_baseline_mass,2)}%</b>. Effective weighted rows: <b>${fmt(d.baseline_effective_sample_size)}</b> before, <b>${fmt(d.conditional_effective_sample_size)}</b> after.</p><p>Latitude 5th / median / 95th percentiles: <b>${s.baseline_latitude_quantiles.map(x=>fmt(x)).join(' / ')}°</b> before; <b>${s.conditional_latitude_quantiles.map(x=>fmt(x)).join(' / ')}°</b> after. Parent impact times relative to 00:19: <b>${d.impact_time_offset_range_s.map(x=>fmt(x/60)).join(' to ')} minutes</b>.</p>`;
 const m=axes('map',[75,110,-47,-20],'Conditional impact probability density'),top=s.cells.reduce((a,v)=>Math.max(a,v[2]/100),1e-15),low=top*1e-4;
 m.c.save();m.c.beginPath();m.c.rect(m.p.l,m.p.t,m.w,m.h);m.c.clip();for(const [ix,iy,p] of s.cells){m.c.fillStyle=colour((Math.log10(p/100)-Math.log10(low))/4);m.c.fillRect(m.x(s.longitude_edges[ix]),m.y(s.latitude_edges[iy+1]),m.x(s.longitude_edges[ix+1])-m.x(s.longitude_edges[ix])+.4,m.y(s.latitude_edges[iy])-m.y(s.latitude_edges[iy+1])+.4);}m.c.restore();m.c.font='16px system-ui';m.c.textAlign='right';m.c.fillStyle='#193240';m.c.fillText('Light '+low.toExponential(1)+' → dark '+top.toExponential(1)+' per km²',940,688);
 const f=axes('cdf',[-45,-15,0,1],'Change after conditional transport evidence');f.c.save();f.c.beginPath();f.c.rect(f.p.l,f.p.t,f.w,f.h);f.c.clip();for(const [values,color] of [[s.baseline_cdf,'#222'],[s.conditional_cdf,'#1676a1']]){f.c.strokeStyle=color;f.c.lineWidth=3;f.c.beginPath();values.forEach(([x,y],i)=>i?f.c.lineTo(f.x(x),f.y(y)):f.c.moveTo(f.x(x),f.y(y)));f.c.stroke();}f.c.restore();
 document.getElementById('limits').innerHTML=d.limitations.map(s=>'<p>'+esc(s)+'</p>').join('');}
function chooseEvidence(){const v=data.filter(v=>v.terminal_family===family.value&&v.contact_case===contact.value);options(evidence,[...new Set(v.map(x=>x.evidence_model))],x=>v.find(z=>z.evidence_model===x).model_label);render();}
function chooseContact(){const v=data.filter(v=>v.terminal_family===family.value);options(contact,[...new Set(v.map(x=>x.contact_case))],x=>v.find(z=>z.contact_case===x).contact_label);chooseEvidence();}
async function start(){const bytes=Uint8Array.from(atob(packed),c=>c.charCodeAt(0));data=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());options(family,[...new Set(data.map(x=>x.terminal_family))],x=>x.replaceAll('-',' '));family.value='openap26-positive-lift-3-targets';chooseContact();contact.value='r600-no-startup-offset';chooseEvidence();family.addEventListener('change',chooseContact);contact.addEventListener('change',chooseEvidence);evidence.addEventListener('change',render);}
start().catch(e=>{document.getElementById('status').textContent='Report could not load: '+e.message;});
'''.replace('PACKED',payload)
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>'+css+'</style><main>'+body+'</main><script>'+js+'</script></html>'
    if len(document.encode())>5*1024**2:raise ValueError('ISO document limit exceeded')
    inline.write_text(document);(output/'index.html').write_text(document)

def report(state, category, output, inline, browser_only=False):
    if browser_only:
        saved=json.loads((output/'summary.json').read_text())
        browser(saved['comparisons'],category,output,inline)
        return
    source=json.loads(state.read_text());output.mkdir(parents=True,exist_ok=True)
    entries=[e for e in source['completed'] if e['evidence_model'].startswith('pleiades-')==(category=='pleiades')]
    if not entries:raise ValueError('No completed selected comparisons')
    values=[load(e,output) for e in entries]
    plt.rcParams.update({'svg.fonttype':'none','font.size':10})
    for family in sorted({v['terminal_family'] for v in values}):figure(family,values,category,output)
    result=dict(generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),source_state_sha256=digest(state),report_source_sha256=digest(__file__),category=category,comparisons=values)
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');browser(values,category,output,inline)
    command=shlex.join(['python',str(Path(__file__).resolve()),'--state',str(state),'--category',category,'--output',str(output),'--inline-output',str(inline)])
    (output/'README.md').write_text('# Conditional spatial evidence comparison\n\n'+command+'\n\nFull precision grids and summaries are retained. Individual central-runner configurations, input hashes, weighted particles and figures are identified by the source status manifest. No transport family is pooled with another.\n')
    print(json.dumps(dict(category=category,comparisons=len(values),inline_bytes=inline.stat().st_size)))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--state',required=True,type=Path);p.add_argument('--category',required=True,choices=['drift','pleiades']);p.add_argument('--output',required=True,type=Path);p.add_argument('--inline-output',required=True,type=Path)
    p.add_argument('--browser-only',action='store_true')
    a=p.parse_args();report(a.state,a.category,a.output,a.inline_output,a.browser_only)
