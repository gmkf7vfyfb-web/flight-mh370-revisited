"""Stand-in analysis (architecture, 10 Oct 2026) for results/pleiades-conditional-r600-raw-bfo-standin.md.
Assembled from the analysis session's function sources (inspect.getsource) in the order they were run; constants and the
driver lines are reproduced verbatim. Inputs: acc2/<stratum>-seed-<k>.npz from accumulate.py, parents/<stratum>-seed-<k>.pkl
(hand-off TOML parsed with parse_handoff), the Pléiades surfaces regenerated with the module's export tests
(sha256 9a3d55a9.../e7fd6ded..., identical to the module's run tree), and end of flight's family-evidence-next-run-b.json."""
import sys, json, numpy as np, pandas as pd
from pathlib import Path
WS=Path('.').resolve()
ENG=WS/'repo/Claude Science Project Sep 29/engine'
sys.path.insert(0,str(ENG/'hypotheses/pleiades/prepare'))
import branch_eof289 as be
from rerun_reference import tension, hdr_mask, dist_nm
from branch_figure import hdr_level
mp, models, P, Cm = be.load_fields(ENG/'runs/pleiades')
LG = be.build_branch(models,P,Cm,0,0)['P+C4']['both models']
STRATA=['next-free','next-repro-radar','next-descent-climb','next-routes']
ACC={(s,k):dict(np.load(f'acc2/{s}-seed-{k}.npz')) for s in STRATA for k in (1,2,3,4)}
a0=ACC[('next-free',1)]; elat,elon=a0['elat'],a0['elon']
lat=0.5*(elat[1:]+elat[:-1]); lon=0.5*(elon[1:]+elon[:-1]); LAT,LON=np.meshgrid(lat,lon,indexing='ij'); area=be.area_km2(LAT)
dummy=np.zeros_like(area,bool)
fe=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/summary/family-evidence-next-run-b.json'))
OPTKEY={'raw':'00:19 R600 BTO + Raw BFO +alive','bto':'00:19 R600 BTO Only +alive'}
PF={o:{'fixed':fe['mixtures'][OPTKEY[o]]['p_family_fixed'],'reweighted':fe['mixtures'][OPTKEY[o]]['p_family_reweighted']} for o in OPTKEY}
VARS=['rho0', 'rho0.02', 'rho0.05', 'rho0.1', 'rho0.2', 'rho0.3', 'rho0.5', 'q0.90', 'q0.98', 'independent', 'oi2018', 'oi2018-0.952', 'oi2025', 'oi2018+2025']
PARTS=[((1,2),(3,4)),((1,3),(2,4)),((1,4),(2,3))]
XC='/Users/pete/Downloads/mh370-exchange/core/next-run'
MODES=['TrueHeading','MagneticHeading','TrueTrack','MagneticTrack','LateralNavigation']

# PVARS, CAT/CONT labels: see the session; reproduced here
def parse_handoff(path, keep=None):
    rows=[]; cur=None; sec=''
    with open(path,'rb') as f:
        for line in f:
            if line.startswith(b'[[row]]'):
                cur={}; rows.append(cur); sec=''; continue
            if line.startswith(b'['):
                sec=line.strip().strip(b'[]').decode()
                if sec.startswith('row.'): sec=sec[4:]
                else: sec='#'+sec
                continue
            if cur is None or b' = ' not in line: continue
            k,v=line.rstrip(b'\n').split(b' = ',1)
            key=(sec+'.' if sec else '')+k.decode()
            if keep is not None and key not in keep: continue
            cur[key]=v.decode()
    return rows


def mixgrid(o,pf,key,seeds=(1,2,3,4)):
    return sum(pf[s]*np.mean([ACC[(s,k)][f'{o}:{key}'].astype(float)/ACC[(s,k)][f'{o}:sum_w'] for k in seeds],axis=0) for s in STRATA)


def mixscalar(o,pf,key,seeds=(1,2,3,4)):
    return sum(pf[s]*np.mean([ACC[(s,k)][f'{o}:{key}']/ACC[(s,k)][f'{o}:sum_w'] for k in seeds]) for s in STRATA)


def areas(m):
    m=m/m.sum(); dn=m/area
    return {q:float(area[dn>=hdr_level(dn,m,q)].sum()) for q in (0.5,0.9)}


def mean_mode(m):
    m=m/m.sum(); dn=m/area; i=np.unravel_index(np.argmax(dn),dn.shape)
    return float((m*LAT).sum()),float((m*LON).sum()),float(LAT[i]),float(LON[i])


def summary(o,pf,seeds=(1,2,3,4)):
    pre_=mixgrid(o,pf,'h_pre',seeds)
    t=tension(pre_,LG,area,lat,lon,dummy,dummy,dummy)
    preH=pre_*LG
    r=dict(ln_R=t['ln_R'],ln_S=t['ln_S'],uncond_in_cond_hdr90=t['uncond_in_cond_hdr90'],cond_in_uncond_hdr90=t['cond_in_uncond_hdr90'],
           mode_shift_nm=t['mode_shift_nm'],mean_shift_nm=t['mean_shift_nm'],uncond_mass_in_grid=t['uncond_mass_in_domain'],
           lnZ_H_abs=float(np.log((pre_/pre_.sum()*LG).sum())))
    for tag,m in (('noH',pre_),('H',preH)):
        a=areas(m); mm=mean_mode(m)
        r.update({f'{tag}_hdr50':a[0.5],f'{tag}_hdr90':a[0.9],f'{tag}_mean_lat':mm[0],f'{tag}_mean_lon':mm[1],f'{tag}_mode_lat':mm[2],f'{tag}_mode_lon':mm[3]})
    # median latitude under H (module's cond_median)
    pj=preH/preH.sum(); r['H_median_lat']=float(np.interp(0.5,np.cumsum(pj.sum(axis=1)),lat))
    pn=pre_/pre_.sum(); r['noH_median_lat']=float(np.interp(0.5,np.cumsum(pn.sum(axis=1)),lat))
    # searches
    for v in VARS:
        zH=mixscalar(o,pf,f'sum_wH_s:{v}',seeds)/mixscalar(o,pf,'sum_wH',seeds)
        z0=mixscalar(o,pf,f'sum_w_s:{v}',seeds)  # whole flight posterior (normalised per seed)
        r[f'retainH:{v}']=zH; r[f'retain0_all:{v}']=z0
    for v in ('rho0.05','oi2018+2025'):
        post=mixgrid(o,pf,f'h_post:{v}',seeds); postH=post*LG
        r[f'retain0_grid:{v}']=post.sum()/pre_.sum(); r[f'retainH_grid:{v}']=postH.sum()/preH.sum()
        for tag,m in (('noH',post),('H',postH)):
            a=areas(m); mm=mean_mode(m)
            r.update({f'{tag}_post_hdr50:{v}':a[0.5],f'{tag}_post_hdr90:{v}':a[0.9],f'{tag}_post_mean_lat:{v}':mm[0],f'{tag}_post_mean_lon:{v}':mm[1]})
    return r


def cut(x,edges,fmt):
    lab=[fmt(edges[i],edges[i+1]) for i in range(len(edges)-1)]
    i=np.clip(np.searchsorted(edges,x,side='right')-1,0,len(edges)-2)
    return np.where(np.isfinite(x),np.array(lab,dtype=object)[i],'none')


def hm(t): 
    t=(t-T0)%86400; return f"{int(t//3600):02d}:{int(t%3600//60):02d}"


def cfk(o,pf,s,k,seeds,H):
    # mixture weight constant per (stratum, seed): P(f)/n_seeds / sum_w ; H weights normalised later
    return pf[s]/len(seeds)/ACC[(s,k)][f'{o}:sum_w']


def parent_shares(o,pf,var,seeds=(1,2,3,4)):
    num0={};numH={};sq0={};sqH={}
    for s in STRATA:
        for k in seeds:
            c=cfk(o,pf,s,k,seeds,False); d=PAR[(s,k)]; cat=PVARS[var](d,s)
            w0=ACC[(s,k)][f'{o}:par_w']*c; wH=ACC[(s,k)][f'{o}:par_wH']*c
            n=len(d); w0=w0[:n] if len(w0)>=n else np.pad(w0,(0,n-len(w0))); wH=wH[:n] if len(wH)>=n else np.pad(wH,(0,n-len(wH)))
            for cv in np.unique(cat):
                m=cat==cv
                num0[cv]=num0.get(cv,0)+w0[m].sum(); numH[cv]=numH.get(cv,0)+wH[m].sum()
                sq0[cv]=sq0.get(cv,0)+(w0[m]**2).sum(); sqH[cv]=sqH.get(cv,0)+(wH[m]**2).sum()
    T0_=sum(num0.values()); TH=sum(numH.values())
    return {cv:dict(share0=num0[cv]/T0_,shareH=numH[cv]/TH,essH_par=(numH[cv]**2/sqH[cv]) if sqH[cv]>0 else 0.0,ess0_par=num0[cv]**2/sq0[cv] if sq0[cv]>0 else 0) for cv in num0}


def table(o,wn,var):
    pf=PF[o][wn]; full=parent_shares(o,pf,var)
    hal=[(parent_shares(o,pf,var,A),parent_shares(o,pf,var,B)) for A,B in PARTS]
    rows=[]
    for cv,r in full.items():
        sh=[(h[0].get(cv,{}).get('shareH',0),h[1].get(cv,{}).get('shareH',0)) for h in hal]
        rt=[((h[0].get(cv,{}).get('shareH',0)/max(h[0].get(cv,{}).get('share0',0),1e-300)),(h[1].get(cv,{}).get('shareH',0)/max(h[1].get(cv,{}).get('share0',0),1e-300))) for h in hal]
        rows.append(dict(variable=var,value=cv,share_noH=r['share0'],share_H=r['shareH'],sigma_share_H=np.sqrt(np.mean([((a-b)/2)**2 for a,b in sh])),
                         ratio=r['shareH']/r['share0'] if r['share0']>0 else np.nan,sigma_ratio=np.sqrt(np.mean([((a-b)/2)**2 for a,b in rt])),
                         ess_H_parents=r['essH_par'],ess_noH_parents=r['ess0_par']))
    return pd.DataFrame(rows).sort_values('share_noH',ascending=False)


def impact_cat_shares(o,pf,k_,seeds=(1,2,3,4),mapper=None):
    n0=nH=s0=sH=0
    for s in STRATA:
        for k in seeds:
            A=ACC[(s,k)]; c=pf[s]/len(seeds)/A[f'{o}:sum_w']
            n0=n0+A[f'{o}:cat0:{k_}']*c; nH=nH+A[f'{o}:catH:{k_}']*c; s0=s0+A[f'{o}:cat0sq:{k_}']*c*c; sH=sH+A[f'{o}:catHsq:{k_}']*c*c
    if mapper is not None:
        labs=sorted(set(mapper.values()))
        agg=lambda v: np.array([sum(v[i] for i in mapper if mapper[i]==l) for l in labs])
        n0,nH,s0,sH=agg(n0),agg(nH),agg(s0),agg(sH)
    else: labs=list(range(len(n0)))
    return labs,n0/n0.sum(),nH/nH.sum(),np.where(sH>0,nH**2/np.maximum(sH,1e-300),0),np.where(s0>0,n0**2/np.maximum(s0,1e-300),0)


def impact_table(o,wn,name,k_,mapper=None,labels=None):
    pf=PF[o][wn]
    labs,a,b,eH,e0=impact_cat_shares(o,pf,k_,mapper=mapper)
    hal=[(impact_cat_shares(o,pf,k_,A,mapper),impact_cat_shares(o,pf,k_,B,mapper)) for A,B in PARTS]
    rows=[]
    for i,l in enumerate(labs):
        if a[i]<1e-6 and b[i]<1e-6: continue
        sh=[(h[0][2][i],h[1][2][i]) for h in hal]; rt=[(h[0][2][i]/max(h[0][1][i],1e-300),h[1][2][i]/max(h[1][1][i],1e-300)) for h in hal]
        rows.append(dict(variable=name,value=labels(l) if labels else l,share_noH=a[i],share_H=b[i],sigma_share_H=np.sqrt(np.mean([((x-y)/2)**2 for x,y in sh])),
                         ratio=b[i]/a[i] if a[i]>0 else np.nan,sigma_ratio=np.sqrt(np.mean([((x-y)/2)**2 for x,y in rt])),ess_H_rows=eH[i],ess_noH_rows=e0[i]))
    return pd.DataFrame(rows).sort_values('share_noH',ascending=False)


def all_tables(o,wn):
    out=[table(o,wn,v) for v in PVARS]
    out+=[impact_table(o,wn,n,k_,m) for n,k_,m,_ in IMPT]
    return pd.concat(out,ignore_index=True)


def wq(h,lo,hi,q):
    x=np.linspace(lo,hi,len(h)+1); c=np.cumsum(h)/h.sum(); return float(np.interp(q,c,x[1:]))


def cont_hist(o,pf,k_,tag,seeds=(1,2,3,4)):
    h=0
    for s in STRATA:
        for k in seeds:
            A=ACC[(s,k)]; h=h+A[f'{o}:cont{tag}:{k_}']*pf[s]/len(seeds)/A[f'{o}:sum_w']
    return h


def cont_rows(o,wn):
    pf=PF[o][wn]; rows=[]
    for k_,(lo,hi,nb) in CONT.items():
        for tag,lab in (('0','without H'),('H','under H')):
            vals={q:wq(cont_hist(o,pf,k_,tag),lo,hi,q) for q in (0.05,0.5,0.95)}
            sig={q:np.sqrt(np.mean([((wq(cont_hist(o,pf,k_,tag,A),lo,hi,q)-wq(cont_hist(o,pf,k_,tag,B),lo,hi,q))/2)**2 for A,B in PARTS])) for q in (0.05,0.5,0.95)}
            rows.append(dict(variable=CNAME[k_],case=lab,q05=vals[0.05],q50=vals[0.5],q95=vals[0.95],sigma_q05=sig[0.05],sigma_q50=sig[0.5],sigma_q95=sig[0.95]))
    return pd.DataFrame(rows)


def mix_ess(o,pf,H=True):
    S=SQ=0; SP=SQP=0
    for s in STRATA:
        for k in (1,2,3,4):
            A=ACC[(s,k)]; c=pf[s]/4/A[f'{o}:sum_w']
            key='wH' if H else 'w'
            S+=A[f'{o}:sum_{key}']*c; SQ+=A[f'{o}:sum_{key}2']*c*c
            pw=A[f'{o}:par_{key}']*c; SP+=pw.sum(); SQP+=(pw**2).sum()
    return S*S/SQ, SP*SP/SQP


def zf(o,s): return np.mean([ACC[(s,k)][f'{o}:sum_wH']/ACC[(s,k)][f'{o}:sum_w'] for k in (1,2,3,4)])


def stratum_shares(o,wn,H):
    pf=PF[o][wn]; v={s:pf[s]*(zf(o,s) if H else 1) for s in STRATA}; t=sum(v.values()); return {s:v[s]/t for s in STRATA}


def path_draws(o,wn,H,N=240):
    sh=stratum_shares(o,wn,H); out=[]
    for s in STRATA:
        nf=int(round(N*sh[s]))
        for k in (1,2,3,4):
            D=ACC[(s,k)][f'draws:{o}:{"H" if H else "0"}']
            take=D[np.argsort(D[:,0])[-max(1,int(np.ceil(nf/4))):]] if nf>0 else D[:0]
            if len(take)==0: continue
            meta=json.load(open(f'{XE}/{s}/seed-{k}/run.json')); ci={c:i for i,c in enumerate(meta['impact_columns'])}
            A=np.load(f'{XE}/{s}/seed-{k}/impacts.npy',mmap_mode='r')
            Hh=PAR[(s,k)]
            for r in take:
                row=int(r[1]); x=A[row]
                par=int(x[ci['parent']]); hp=Hh.iloc[par]
                pts=[(1394237459.0,hp['latitude_deg'],hp['longitude_deg']),(x[ci['takeover_unix_s']],x[ci['takeover_latitude_deg']],x[ci['takeover_longitude_deg']])]
                if np.isfinite(x[ci['latent:last_burst_latitude_deg']]): pts.append((T_B,x[ci['latent:last_burst_latitude_deg']],x[ci['latent:last_burst_longitude_deg']]))
                pts.append((x[ci['unix_s']],x[ci['latitude_deg']],x[ci['longitude_deg']]))
                pts=sorted([p for p in pts if np.isfinite(p[1])])
                out.append(dict(stratum=s,seed=k,parent=par,pts=np.array(pts),mode=hp['filter_mode']))
    return out


def mode_ratio(o,wn,s):
    num0={};numH={}
    for k in (1,2,3,4):
        c=1/ACC[(s,k)][f'{o}:sum_w']; d=PAR[(s,k)]
        for m_ in MODES:
            msk=(d['filter_mode']==m_).values
            num0[m_]=num0.get(m_,0)+ACC[(s,k)][f'{o}:par_w'][:len(d)][msk].sum()*c; numH[m_]=numH.get(m_,0)+ACC[(s,k)][f'{o}:par_wH'][:len(d)][msk].sum()*c
    t0=sum(num0.values()); tH=sum(numH.values())
    return {m_:(numH[m_]/tH)/(num0[m_]/t0) if num0[m_]>0 else 0 for m_ in MODES}


def route_draws(o,wn,H,N=240,seed=7):
    rng=np.random.default_rng(seed); sh=stratum_shares(o,wn,H); out=[]
    for s in STRATA:
        nf=int(round(N*sh[s])); 
        if nf==0: continue
        R=[];W=[]
        mr=mode_ratio(o,wn,s) if H else None
        for k in (1,2,3,4):
            rr=np.load(f'{XC}/{s}/bto-bfo/seed-{k}/routes.npy'); dg=json.load(open(f'{XC}/{s}/bto-bfo/seed-{k}/diagnostics.json'))['modes']
            p=np.array([m_['posterior_probability'] for m_ in dg]); names=[m_['mode'] for m_ in dg]
            bounds=np.round(np.cumsum(p)/p.sum()*len(rr)).astype(int); lab=np.searchsorted(bounds,np.arange(len(rr)),side='right')
            for i in range(len(rr)):
                R.append(rr[i]); W.append(mr[names[lab[i]]] if H else 1.0)
        W=np.array(W)/np.sum(W); idx=rng.choice(len(R),size=nf,replace=False,p=W)
        out+= [R[i] for i in idx]
    return out


def low(r): 
    e=r['ess_H_parents'] if np.isfinite(r.get('ess_H_parents',np.nan)) else np.nan
    er=r.get('ess_H_rows',np.nan)
    return (np.isfinite(e) and e<100) or (np.isfinite(er) and er<1000)


# ---- figures (final versions as rendered)
def fig1():
    fig=plt.figure(figsize=(7.1,7.6))
    for j,o in enumerate(['raw','bto']):
        f,sg=RES[(o,'reweighted')]; ff,_=RES[(o,'fixed')]
        ax=fig.add_axes([0.065+0.49*j,0.535,0.42,0.345])
        fc.searches(ax,oi=True,zorder=1,alpha_scale=0.6)
        pre_=mixgrid(o,PF[o]['reweighted'],'h_pre')
        fc.points_bg(ax,pre_,lat,lon)
        fc.density(ax,pre_*LG,area,lat,lon)
        fc.arc7(ax); fc.objects(ax)
        ax.plot(f['H_mode_lon'],f['H_mode_lat'],'*',ms=6,color='#08306b',mec='white',mew=0.4,zorder=8)
        fc.frame(ax)
        share=float((pre_/pre_.sum())[np.ix_((lat>=-38)&(lat<=-32),(lon>=88)&(lon<=96))].sum())
        ax.set_title(f"{'ab'[j]}   {ONAME[o]}, before the searches",loc='left',fontsize=6.3)
        ax.text(0.01,0.01,f"{100*share:.0f} % of the PDF without H lies in this frame\n(its mode, {abs(f['noH_mode_lat']):.1f} S {f['noH_mode_lon']:.1f} E, is outside it)",transform=ax.transAxes,fontsize=5,va='bottom',color='#222222',zorder=9,bbox=dict(fc='white',ec='none',alpha=0.7,pad=1))
        ta=fig.add_axes([0.02+0.49*j,0.255,0.475,0.225]); ta.axis('off')
        er,fr=ESSM[o]['reweighted'],ESSM[o]['fixed']
        rows=[["50 % region under H",pm(f['H_hdr50'],sg['H_hdr50'],',.0f')+" km²",f"{ff['H_hdr50']:,.0f} km²"],
              ["90 % region under H",pm(f['H_hdr90'],sg['H_hdr90'],',.0f')+" km²",f"{ff['H_hdr90']:,.0f} km²"],
              ["90 % region without H",pm(f['noH_hdr90'],sg['noH_hdr90'],',.0f')+" km²",f"{ff['noH_hdr90']:,.0f} km²"],
              ["mean under H",f"{abs(f['H_mean_lat']):.3f} S {f['H_mean_lon']:.3f} E (± {sg['H_mean_lat']:.3f}°)",f"{abs(ff['H_mean_lat']):.3f} S {ff['H_mean_lon']:.3f} E"],
              ["log evidence ratio ln R",pm(f['ln_R'],sg['ln_R'],'.2f'),f"{ff['ln_R']:.2f}"],
              ["share without H inside H's 90 % region",pm(f['uncond_in_cond_hdr90'],sg['uncond_in_cond_hdr90'],'.3f'),f"{ff['uncond_in_cond_hdr90']:.3f}"],
              ["share under H inside 90 % region without H",pm(f['cond_in_uncond_hdr90'],sg['cond_in_uncond_hdr90'],'.3f'),f"{ff['cond_in_uncond_hdr90']:.3f}"],
              ["mode displacement",pm(f['mode_shift_nm'],sg['mode_shift_nm'],'.0f')+" NM",f"{ff['mode_shift_nm']:.0f} NM"],
              ["mean displacement",pm(f['mean_shift_nm'],sg['mean_shift_nm'],'.0f')+" NM",f"{ff['mean_shift_nm']:.0f} NM"],
              ["ESS under H, impacts / 00:11 paths",f"{er[0]:,.0f} / {er[1]:,.0f}",f"{fr[0]:,.0f} / {fr[1]:,.0f}"]]
        t=ta.table(cellText=rows,colLabels=["quantity","family weights re-weighted\nby the 00:19 data (drawn)","fixed family\nweights"],
                   loc='upper left',cellLoc='left',edges='horizontal',colWidths=[0.50,0.32,0.18],bbox=[0,0,1,1])
        t.auto_set_font_size(False); t.set_fontsize(5.0)
        for (r_,c_),cell in t.get_celld().items(): cell.PAD=0.03
    h=[Patch(fc="#2171b5",label="probability density under H (relative)"),plt.Line2D([],[],color="#08306b",lw=1.4,label="50 % region under H"),
       plt.Line2D([],[],color="#08306b",lw=0.7,label="90 % region under H"),plt.Line2D([],[],ls='',marker='*',color='#08306b',label='mode under H'),
       plt.Line2D([],[],ls="",marker="o",ms=1.5,color="#222222",alpha=0.6,label="impact PDF without H (sampled points)"),
       Patch(fc="#7f7f7f",alpha=0.18,label="searched seabed (shown only; not applied here)"),
       plt.Line2D([],[],color="#333333",lw=0.7,ls=":",label="7th arc, FL400"),
       plt.Line2D([],[],ls="",marker="x",color="#d62728",label="Pléiades rating-5 objects"),
       plt.Line2D([],[],ls="",marker="o",mfc="white",mec="#e6550d",label="COSMO-SkyMed radar contacts")]
    fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.02,0.975),ncol=4,frameon=False,fontsize=5.2,columnspacing=1.0,handlelength=1.6)
    fig.suptitle("If the imaged objects are from the aircraft (H): where the aircraft hit the sea, with the tension against the flight data alone — UNCONVERGED",
                 x=0.01,ha='left',y=0.995,fontsize=7)
    ste=("The blue shading shows where the aircraft hit the sea if the floating objects seen by the satellites came from it. The grey points show the same "
         "without that assumption. The searches of the seabed are not applied in this chart. Panel a uses the 00:19 range and frequency values; panel b uses only the 00:19 range value. "
         "The objects move the estimate 100 to 135 NM (mean) north-east, into a small part of the area that the flight data alone allow. The flight model is not stable yet (it has not converged), so all values can change. "
         "This work was done by a stand-in for the Pléiades team, which must review it. The ± values are the differences between two halves of the runs.")
    tech=(f"p(x | D, H) = mixture over core (b) families of the end-of-flight +alive impact posterior x L_H, L_H = Pléiades rating-5 (6 clusters, equal weights) + COSMO-SkyMed C4 pass-marginal, "
          f"GLORYS12+ERA5 and GlobCurrent daily+ERA5 at equal weight, transport errors independent (rho = 0; rho = 0.5 not supported by the hook, see note), GlobCurrent windage as run (drift audit F1), debris released 00:20 UTC; "
          f"surfaces sha256 9a3d55a9/e7fd6ded (hypothesis/pleiades 74332d0). Impacts mh370-exchange/end-of-flight/next-run (4 strata x 4 seeds, 51.2 M rows; EoF physics provisional; two-tank bookkeeping only); log-on cause other. "
          f"Strata mixed by end of flight's 00:19-re-weighted P(family) (family-evidence-next-run-b.json; ruling C), fixed P(family) beside. 0.05 deg grid 85-103 E, 43-25 S (in-grid mass without H {RES[('raw','reweighted')][0]['uncond_mass_in_grid']:.3f}). "
          f"Tension (rerun_reference.tension): ln R = ln[E_flight(L_H) / grid-mean(L_H)]; HDR overlaps two-way; mode on the unsmoothed grid (noisy without H). ± = split-half sigma, rms over the three 2+2 seed partitions of (half A - half B)/2. "
          f"ESS = Kish, mixture weights. Holland H1/H2 not estimable. Searches not applied. Stand-in run 10 Oct 2026, module to review.")
    fc.footnotes(fig,ste,tech,top=0.235,width=172,fs=5.0)
    fig.savefig(FIG/'fig1-conditional-impact-pdf.png',dpi=300); fig.savefig(FIG/'fig1-conditional-impact-pdf.pdf')
    plt.close(fig)


def fig3():
    tr=TB[('raw','reweighted')]; tb=TB[('bto','reweighted')]
    items=[]
    for var,vals in SEL:
        sub=tr[tr.variable==var]
        if vals is None: vals=[v for v in sub.sort_values('share_noH',ascending=False).value if sub.set_index('value').loc[v,'share_noH']>0.005]
        items.append(('hdr',PLAIN[var]))
        for v in vals: items.append(('row',var,v))
    n=len(items); fig=plt.figure(figsize=(7.1,9.6)); ax=fig.add_axes([0.36,0.25,0.42,0.71])
    y=0; yt=[];yl=[]
    for it in items:
        if it[0]=='hdr':
            ax.text(-0.02,y,it[1],transform=ax.get_yaxis_transform(),ha='right',va='center',fontsize=5.8,fontweight='bold'); y-=1; continue
        _,var,v=it
        for off,T,mk,col in ((0.18,tr,'o','#08306b'),(-0.18,tb,'s','#9e9e9e')):
            r=T[(T.variable==var)&(T.value==v)]
            if not len(r): continue
            r=r.iloc[0]; lo_=max(r.ratio-2*r.sigma_ratio,1e-3); hi_=r.ratio+2*r.sigma_ratio
            ax.plot([lo_,hi_],[y+off,y+off],color=col,lw=0.8)
            ax.plot(r.ratio,y+off,mk,ms=3.2,mfc=('white' if low(r) else col),mec=col,mew=0.8)
            if T is tr: ax.text(1.02,y,f"{r.share_noH:.3f} → {r.share_H:.3f}",transform=ax.get_yaxis_transform(),fontsize=5,va='center')
        yt.append(y); yl.append(v); y-=1
    ax.set_yticks(yt); ax.set_yticklabels(yl,fontsize=5.2); ax.set_xscale('log'); ax.axvline(1,color='k',lw=0.6,ls=':')
    ax.set_xlim(0.05,20); ax.set_ylim(y+0.5,0.8); ax.set_xlabel('Ratio of the share under H to the share without H (log scale)')
    ax.text(1.02,1.0,'share without H → under H\n(R600 BTO + Raw BFO)',transform=ax.transAxes,fontsize=5,va='bottom')
    h=[plt.Line2D([],[],ls='',marker='o',color='#08306b',label='00:19 R600 BTO + Raw BFO'),plt.Line2D([],[],ls='',marker='s',color='#9e9e9e',label='00:19 R600 BTO Only (comparison)'),
       plt.Line2D([],[],ls='',marker='o',mfc='white',mec='#08306b',label='too few effective samples under H\n(< 100 paths at 00:11 or < 1,000 impacts)'),
       plt.Line2D([],[],color='#08306b',lw=0.8,label='± 2 split-half σ')]
    ax.legend(handles=h,loc='lower left',bbox_to_anchor=(-0.85,-0.105),ncol=4,frameon=False,fontsize=5.2)
    fig.suptitle('Which kinds of flight the imaged-object hypothesis (H) favours — UNCONVERGED',x=0.01,ha='left',y=0.995,fontsize=7)
    ste=("A point to the right of the dotted line means that this kind of flight path becomes more probable if the floating objects came from the aircraft. A point to the left means less probable. "
         "The bars show the run-to-run spread. Rows for 00:11 and earlier come from the flight model; rows for the descent come from the end-of-flight model. "
         "The flight model has not converged, so treat the values as provisional. A stand-in made this chart for the Pléiades team, which must review it.")
    tech=("Shares are posterior shares of the mixture over core (b) strata (P(family) re-weighted by the 00:19 data, ruling C), without H (EoF arm weights w x exp(ll) x alive, log-on cause other) and under H "
          "(x L_H: Pléiades rating-5 + COSMO C4, two ocean models, rho = 0, GlobCurrent windage as run). 00:11 and earlier: aggregated over impacts to hand-off parents (`parent` -> handoff-m0011 rows: "
          "handoff.npy + handoff.toml state). Descent rows: end-of-flight latents per impact. sigma = split-half, rms over the three 2+2 seed partitions of (half A - half B)/2; bars +- 2 sigma. "
          "ESS = Kish under H per category (paths: hand-off parents; descent: impacts). Bins with share < 0.5 % without H omitted from the chart (all bins in the CSV). EoF physics provisional; known coverage gaps (architecture list): EoF commanded descent rates capped at 6,500 ft/min, free flight cannot unload, family B onset; Holland H1/H2 not estimable.")
    fc.footnotes(fig,ste,tech,top=0.17,width=172)
    fig.savefig(FIG/'fig3-trajectory-shares.png',dpi=300); fig.savefig(FIG/'fig3-trajectory-shares.pdf'); plt.close(fig)


def fig2():
    fig=plt.figure(figsize=(7.1,7.4))
    axs=[fig.add_axes([0.05,0.30,0.25,0.60]),fig.add_axes([0.32,0.30,0.25,0.60]),fig.add_axes([0.63,0.42,0.36,0.48])]
    cols={False:'#555555',True:'#2171b5'}
    for j,H in enumerate((False,True)):
        ax=axs[j]
        for r in RD[('raw',H)]: ax.plot(r[:,1],r[:,0],color='#999999' if not H else '#9ecae1',lw=0.35,alpha=0.35,zorder=1)
        for d in PD[('raw',H)]: ax.plot(d['pts'][:,2],d['pts'][:,1],color=cols[H],lw=0.45,alpha=0.5,zorder=2)
        ax.plot([99.048],[5.625],'k^',ms=4,zorder=5); ax.text(99.3,6.0,'18:01',fontsize=5)
        fc.arc7(ax); fc.objects(ax)
        ax.set_xlim(84,102); ax.set_ylim(-40,8); ax.set_aspect(1.0)
        ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°)' if j==0 else '')
        ax.set_title(f"{'ab'[j]}   {'without H' if not H else 'under H'}",loc='left')
    ax=axs[2]
    fc.searches(ax,oi=True,alpha_scale=0.5)
    for H in (False,True):
        for d in PD[('raw',H)]:
            ax.plot(d['pts'][:,2],d['pts'][:,1],color=cols[H],lw=0.5,alpha=0.45,zorder=2+H)
            ax.plot(d['pts'][-1,2],d['pts'][-1,1],'.',ms=1.8,color=cols[H],alpha=0.8,zorder=3+H)
    fc.arc7(ax); fc.objects(ax)
    a6=None
    ax.set_xlim(87,99); ax.set_ylim(-40,-30); ax.set_aspect(1/np.cos(np.radians(35)))
    ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°)'); ax.set_title('c   00:11 to impact, both cases',loc='left')
    h=[plt.Line2D([],[],color='#555555',lw=0.8,label='00:11 to impact, without H (one line per drawn path)'),
       plt.Line2D([],[],color='#2171b5',lw=0.8,label='00:11 to impact, under H'),
       plt.Line2D([],[],color='#999999',lw=0.8,label='18:01 to 00:11, flight-model route sample'),
       plt.Line2D([],[],color='#9ecae1',lw=0.8,label='18:01 to 00:11, same sample re-weighted by\nautopilot mode only (see footnote)'),
       plt.Line2D([],[],ls='',marker='^',color='k',label='start, 18:01'),plt.Line2D([],[],color='#333333',lw=0.7,ls=':',label='7th arc, FL400'),
       plt.Line2D([],[],ls='',marker='x',color='#d62728',label='Pléiades rating-5 objects'),plt.Line2D([],[],ls='',marker='o',mfc='white',mec='#e6550d',label='COSMO-SkyMed radar contacts')]
    fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.62,0.40),frameon=False,fontsize=5.2)
    fig.suptitle('Which flight paths are left if the imaged objects are from the aircraft (H) — 00:19 R600 BTO + Raw BFO — UNCONVERGED',x=0.01,ha='left',y=0.99,fontsize=7)
    ste=("Each line is one flight path drawn at random in proportion to its probability (about 240 per panel). Grey: the flight data alone. Blue: if the floating objects came from the aircraft. "
         "From 00:11 to the sea, each blue line is the same calculated path that the objects support. Before 00:11 the files keep no link from a path to its later part, so the light-blue lines "
         "are the general route sample, given more weight only for the autopilot modes that the objects support. They are not the exact earlier part of the blue lines. "
         "Under H the paths at 00:11 are further north (34-35 S), slower and turned less to the west. The flight model has not converged.")
    tech=("Option r600/no-offset+alive (log-on cause other); strata mixed by EoF's 00:19-re-weighted P(family), under H by P(f) Z_f(H)/sum. 00:11-to-impact lines: Efraimidis-Spirakis weighted draws without "
          "replacement (80 per seed and case, weights w x exp(ll) x alive, and x L_H under H), n_f per stratum in proportion to the stratum share; vertices hand-off m0011 (handoff.npy via `parent`), EoF take-over, "
          "position at 00:19:37 (latent last_burst), impact, in time order. 18:01-00:11 lines: core routes.npy (2,000 per seed, 600 s, final-posterior mode sample, NOT linked to hand-off rows; final_row = i64::MAX at m0011); "
          "mode of each route assigned from diagnostics.json posterior_probability boundaries (+-1 route per boundary); under H re-weighted by that stratum's hand-off share ratio H/no-H for the filter mode. "
          "L_H as Fig. 1 (P + C4, two ocean models, rho = 0). Core (b) split-half NOT converged; EoF physics provisional.")
    fc.footnotes(fig,ste,tech,top=0.235,width=172)
    fig.savefig(FIG/'fig2-trajectories.png',dpi=300); fig.savefig(FIG/'fig2-trajectories.pdf'); plt.close(fig)


def fig4():
    o='raw'; f,sg=RES[(o,'reweighted')]; ff,_=RES[(o,'fixed')]
    fig=plt.figure(figsize=(7.1,7.8))
    for j,(v,ttl,oi) in enumerate((('rho0.05','after Phase 2 + Bluefin-21 (official)',False),('oi2018+2025','after + Ocean Infinity 2018 and 2025-26 (grade C)',True))):
        ax=fig.add_axes([0.06+0.49*j,0.545,0.42,0.345])
        fc.searches(ax,oi=oi,zorder=1)
        post=mixgrid(o,PF[o]['reweighted'],f'h_post:{v}')
        fc.points_bg(ax,post,lat,lon); fc.density(ax,post*LG,area,lat,lon); fc.arc7(ax); fc.objects(ax); fc.frame(ax)
        ax.set_title(f"{'ab'[j]}   {ttl}",loc='left',fontsize=6.2)
    # rho panel
    ax=fig.add_axes([0.08,0.285,0.36,0.175])
    rh=[0,0.02,0.05,0.1,0.2,0.3,0.5]
    for oo,mk,ls in (('raw','o','-'),('bto','s','--')):
        F,S=RES[(oo,'reweighted')]
        for H,col in ((True,'#2171b5'),(False,'#555555')):
            y=[1-F[f'retain{"H" if H else "0_all"}:rho{r:g}'] for r in rh]; e=[2*S[f'retain{"H" if H else "0_all"}:rho{r:g}'] for r in rh]
            ax.errorbar(rh,y,yerr=e,color=col,ls=ls,marker=mk,ms=2.5,lw=0.9,capsize=1.5,label=f"{'under H' if H else 'without H'}, {ONAME[oo][6:]}")
    ax.axvline(0.05,color='#888',lw=0.6,ls=':'); ax.text(0.055,0.12,'reference ρ = 0.05',fontsize=5)
    ax.set_xlabel('ρ, probability that the wreck could not be found where the sonar looked'); ax.set_ylabel('Share of probability removed\nby Phase 2 + Bluefin-21')
    ax.set_ylim(0.1,0.75); ax.legend(fontsize=4.8,frameon=False,loc='upper right'); ax.set_title('c   Sensitivity to ρ (± 2 split-half σ)',loc='left',fontsize=6.2)
    ta=fig.add_axes([0.51,0.255,0.48,0.225]); ta.axis('off')
    rows=[]
    for v,lab in (('rho0.05','Phase 2 + Bluefin-21'),('oi2018+2025','+ OI 2018 + 2025-26')):
        rows.append([f"removed, {lab}",f"{1-f[f'retainH_grid:{v}']:.3f} ± {sg[f'retainH_grid:{v}']:.3f}",f"{1-f[f'retain0_grid:{v}']:.3f} ± {sg[f'retain0_grid:{v}']:.3f}"])
        for q in ('50','90'):
            rows.append([f"{q} % region after, {lab}",f"{f[f'H_post_hdr{q}:{v}']:,.0f} ± {sg[f'H_post_hdr{q}:{v}']:,.0f} km²",f"{f[f'noH_post_hdr{q}:{v}']:,.0f} ± {sg[f'noH_post_hdr{q}:{v}']:,.0f} km²"])
    rows.insert(0,["50 % / 90 % region before",f"{f['H_hdr50']:,.0f} / {f['H_hdr90']:,.0f} km²",f"{f['noH_hdr50']:,.0f} / {f['noH_hdr90']:,.0f} km²"])
    t=ta.table(cellText=rows,colLabels=['00:19 R600 BTO + Raw BFO','under H','without H'],loc='upper left',cellLoc='left',edges='horizontal',colWidths=[0.47,0.28,0.25],bbox=[0,0,1,1])
    t.auto_set_font_size(False); t.set_fontsize(5.0)
    for (r_,c_),cell in t.get_celld().items(): cell.PAD=0.03
    h=[Patch(fc="#2171b5",label="probability density under H, after the searches"),plt.Line2D([],[],color="#08306b",lw=1.4,label="50 % region under H"),
       plt.Line2D([],[],color="#08306b",lw=0.7,label="90 % region under H"),plt.Line2D([],[],ls="",marker="o",ms=1.5,color="#222222",alpha=0.6,label="impact PDF without H after the same searches (points)")]
    h+=[Patch(fc=c,alpha=a,ec=c,label=l) for _,c,a,l in fc.cs.SEARCH_FILL if l]
    h+=[plt.Line2D([],[],ls="",marker="x",color="#d62728",label="Pléiades rating-5 objects"),plt.Line2D([],[],ls="",marker="o",mfc="white",mec="#e6550d",label="COSMO-SkyMed radar contacts")]
    fig.legend(handles=h,loc='upper left',bbox_to_anchor=(0.02,0.975),ncol=3,frameon=False,fontsize=5.2)
    fig.suptitle('If the imaged objects are from the aircraft (H): what the seabed searches leave — 00:19 R600 BTO + Raw BFO — UNCONVERGED',x=0.01,ha='left',y=0.995,fontsize=7)
    ste=("The searches of the seabed found nothing. If the floating objects came from the aircraft, the searches remove about 64 % of the probability, against about 49 % without that assumption, "
         "because the objects point to places near searched ground. The blue area that remains is next to the searched strips. The value of ρ (the chance that the sonar missed the wreck) changes "
         "the removed share most. Ocean Infinity areas are traced from public sources (grade C). The flight model has not converged. A stand-in made this chart; the teams must review it.")
    tech=("Searched areas' likelihood, its own code: P(no find) = rho + (1-rho) prod_k(1 - q_k f_k c_k), shared misses, point target; c_k = covered_fraction_<campaign> from `mh370 evaluate hypotheses/seabed-search/run.toml "
          "+ OI 2018 and 2025 campaign lists` (binary at e9cca3b; base loglik reproduced to 0.0); Phase 2 q 0.945, Bluefin-21 q 0.9, OI 2018 q 0.9 f 0.889, OI 2025-26 SE band q 0.9 f 0.7808. "
          "Removed = 1 - Z_search; in-grid (85-103 E, 43-25 S) values in the table, whole-posterior values in panel c and the CSV (without H whole: 0.494). H as Fig. 1 (P + C4, two ocean models, rho_transport = 0). "
          "Strata re-weighted by 00:19 P(family). sigma = split-half over 2+2 seed partitions. Other sensitivities (q 0.90/0.98, independent misses, OI 2018 coverage 0.952) in the note. Core (b) NOT converged; EoF provisional.")
    fc.footnotes(fig,ste,tech,top=0.235,width=172)
    fig.savefig(FIG/'fig4-searches-under-H.png',dpi=300); fig.savefig(FIG/'fig4-searches-under-H.pdf'); plt.close(fig)

# driver, as run: RES[(o,wn)] = (summary(o,PF[o][wn]), split-half sigma over PARTS); TB = all_tables; CT = cont_rows;
# PD/RD = path_draws/route_draws('raw','reweighted',H); then fig1(), fig2(), fig3(), fig4().
