"""Kadri unused-data analysis, 7 Nov 2026 (session export).

Core functions exactly as run in the session. The driver steps (loading, loops, table writing) were run
interactively; their order is: (1) Kadri 2019 Fig. 4 page raster -> axis calibration by tick-label centres
(labels_in, linfit) -> img_extract / analyse_img / trace_extract / col_stat; (2) Fig. 9 tick-label
re-calibration (labels_B, linfit) and the 6 Nov envelope statistic (traces_tau, traces_tau_b) against
Fig. S1 backgrounds (build_null, score8, wmax_null); (3) Scott Reef record 6 spectrogram and consistency
(consistent, pred_spans, sr_spec); (4) Fig. 9 spectrogram colour reading (getimg, LUT) and relative spectra
(spec_excess, slope, slope_se); (5) figures figA-figD and jon_versions.
Inputs: see the results note, Section 1. Requires kadrienv.py from the 6 Nov bundle.
"""
import numpy as np, pandas as pd
from scipy import ndimage as ndi
from scipy.stats import binom
import kadrienv as KE


def runs(mask1d):
    m=np.r_[0,mask1d.astype(int),0]; dd=np.diff(m); s=np.where(dd==1)[0]; e=np.where(dd==-1)[0]; return list(zip(s,e))


def labels_in(x0,x1,y0,y1,merge=(3,9)):
    m=txt[y0:y1,x0:x1]
    md=ndi.binary_dilation(m,structure=np.ones(merge))
    lab,n=ndi.label(md); out=[]
    for k in range(1,n+1):
        ys,xs=np.where((lab==k)&m)
        if len(xs)<15: continue
        out.append(dict(xc=x0+(xs.min()+xs.max())/2, yc=y0+(ys.min()+ys.max())/2, x0=x0+xs.min(),x1=x0+xs.max(),y0=y0+ys.min(),y1=y0+ys.max(),n=len(xs)))
    return pd.DataFrame(out)


def linfit(px,val):
    px=np.asarray(px,float); val=np.asarray(val,float)
    A_=np.vstack([px,np.ones_like(px)]).T; c,res,_,_=np.linalg.lstsq(A_,val,rcond=None)
    r=val-A_@c; return c, r


def img_extract(k):
    v=IMG[k]; x0,x1=v['x']; y0,y1=v['y']
    Lp=L[y0:y1+1,x0:x1+1].copy(); an=ann[y0:y1+1,x0:x1+1]
    cols=np.arange(x0,x1+1); rows=np.arange(y0,y1+1)
    tmin=v['cx'][0]*cols+v['cx'][1]; brg=v['cy'][0]*rows+v['cy'][1]
    Lm=Lp.copy(); Lm[an]=np.nan
    return Lp,Lm,an,tmin,brg


def analyse_img(k, thr=4.0, win=31):
    Lp,Lm,an,tmin,brg,bg=out[k]; v=IMG[k]
    t0=pd.Timestamp(v['t0'],tz='UTC')
    Lf=np.where(np.isnan(Lm),bg,Lm)
    base=ndi.median_filter(Lf,size=(1,win),mode='nearest')
    R=Lf-base; R[an]=np.nan
    shot=np.zeros(len(brg),bool)
    for s in SHOT_IMG: shot|=np.abs(brg-s)<=5
    # per column summaries
    cs=[]
    for j in range(Lf.shape[1]):
        col=Lm[:,j]; ok=np.isfinite(col)
        i_all=np.nanargmax(col); c2=np.where(shot|~ok,-np.inf,col); i_ns=np.argmax(c2)
        r=np.where(np.isnan(R[:,j]),-np.inf,R[:,j]); r_ns=np.where(shot,-np.inf,r); i_r=np.argmax(r_ns)
        cs.append(dict(panel=k,col_px=v['x'][0]+j,t_utc=(t0+pd.Timedelta(minutes=tmin[j])).strftime('%Y-%m-%d %H:%M:%S'),
                       t_s_rel_0800=(t0-pd.Timestamp('2014-03-08',tz='UTC')).total_seconds()+tmin[j]*60,
                       dom_brg_img=brg[i_all],dom_Lstar=col[i_all],dom_excess=col[i_all]-bg,
                       nonshot_brg_img=brg[i_ns],nonshot_Lstar=col[i_ns],nonshot_excess=col[i_ns]-bg,
                       transient_brg_img=brg[i_r],transient_resid=r_ns[i_r],annotation_in_col=bool(an[:,j].any())))
    cs=pd.DataFrame(cs)
    # blobs
    M=(R>thr)&~np.isnan(R)
    lab,n=ndi.label(M,structure=np.ones((3,3)))
    bl=[]
    for q_ in range(1,n+1):
        ys,xs=np.where(lab==q_)
        w=np.clip(R[ys,xs],0,None)
        tc=np.average(tmin[xs],weights=w); bc=np.average(brg[ys],weights=w)
        bl.append(dict(panel=k,t_utc=(t0+pd.Timedelta(minutes=tc)).strftime('%H:%M:%S'),t_s_rel_0800=(t0-pd.Timestamp('2014-03-08',tz='UTC')).total_seconds()+tc*60,
             t_start_utc=(t0+pd.Timedelta(minutes=tmin[xs].min())).strftime('%H:%M:%S'),t_end_utc=(t0+pd.Timedelta(minutes=tmin[xs].max())).strftime('%H:%M:%S'),
             brg_img=bc,brg_min=brg[ys].min(),brg_max=brg[ys].max(),npix=len(xs),peak_resid=np.nanmax(R[ys,xs]),peak_Lstar=np.nanmax(Lm[ys,xs]),
             in_shot_sector=bool(shot[ys].mean()>0.5), annotated=bool(ndi.binary_dilation(an,iterations=3)[ys,xs].any())))
    return cs, pd.DataFrame(bl), R


def trace_extract(k):
    v=TR[k]; x0,x1,y0,y1=v['frame']; t0=pd.Timestamp(v['t0'],tz='UTC')
    rows=[]
    for x in range(x0+1,x1):
        col=blue[y0+1:y1,x]; ys=np.where(col)[0]+y0+1
        tm=v['cx'][0]*x+v['cx'][1]
        if len(ys)==0: rows.append(dict(panel=k,col_px=x,t_min=tm)); continue
        ytop,ybot=ys.min(),ys.max()
        vtop=v['cy'][0]*ytop+v['cy'][1]; vbot=v['cy'][0]*ybot+v['cy'][1]
        rows.append(dict(panel=k,col_px=x,t_min=tm,t_s_rel_0800=(t0-pd.Timestamp('2014-03-08',tz='UTC')).total_seconds()+tm*60,
                         t_utc=(t0+pd.Timedelta(minutes=tm)).strftime('%Y-%m-%d %H:%M:%S'),
                         y_top_px=ytop,y_bot_px=ybot,v_max=vtop,v_min=vbot,
                         clipped_top=bool(ytop<=y0+1),clipped_bot=bool(ybot>=y1-1),n_blue=len(ys)))
    return pd.DataFrame(rows)


def bin_extremes(t,p,centres,half):
    mx=[];mn=[]
    for c in centres:
        m=(t>=c-half)&(t<c+half); mx.append(p[m].max() if m.any() else np.nan); mn.append(p[m].min() if m.any() else np.nan)
    return np.array(mx),np.array(mn)


def col_stat(dfk,val):
    v=dfk[val].values.astype(float); n=len(v); E=np.full(n,np.nan)
    for j in range(n):
        w=[j] if j+1>=n else [j,j+1]
        ring=[i for i in list(range(j-14,j-2))+list(range(j+4,j+16)) if 0<=i<n]
        rv=v[ring]; rv=rv[np.isfinite(rv)]; wv=v[w]
        if len(rv)<8 or not np.isfinite(wv).all(): continue
        E[j]=10*np.log10(np.mean(wv**2)/np.median(rv**2))
    return E


def tailp(null,x):
    null=np.sort(null[np.isfinite(null)]); N=len(null)
    return (N-np.searchsorted(null,x,side='left')+1)/(N+1)


def build_null(segs):
    nul=pd.concat([d.assign(seg=i) for i,d in enumerate(segs)],ignore_index=True)
    # null's own F: rank p within null (leave-in), as 6 Nov did in-sample
    nul['p_E']=KE.rank_p(nul.E.values); nul['p_pers']=KE.rank_p(nul.pers.values)
    nul['F']=-2*(np.log(nul.p_E)+np.log(nul.p_pers)); return nul


def score8(s8x,nul):
    o=s8x.copy(); o['p_E']=tailp(nul.E.values,o.E.values); o['p_pers']=tailp(nul.pers.values,o.pers.values)
    o['F']=-2*(np.log(o.p_E)+np.log(o.p_pers)); o['p_F']=tailp(nul.F.values,o.F.values); return o


def wmax_null(nul,nwin,mode,rng,ndraw=20000,Lb=24):
    segF=[g.F.values for _,g in nul.groupby('seg')]
    out=[]
    if mode=='within':
        for _ in range(ndraw):
            f=segF[rng.integers(len(segF))]; n=min(nwin,len(f)); i=rng.integers(0,len(f)-n+1); out.append(f[i:i+n].max())
    else:
        allblocks=[(f,i) for f in segF for i in range(len(f)-Lb+1)]
        for _ in range(ndraw):
            m=-np.inf; got=0
            while got<nwin:
                f,i=allblocks[rng.integers(len(allblocks))]; take=min(Lb,nwin-got); m=max(m,f[i:i+take].max()); got+=take
            out.append(m)
    return np.sort(np.array(out))


def insample(sx):
    sx=sx.copy(); sx['p_E']=KE.rank_p(sx.E.values); sx['p_pers']=KE.rank_p(sx.pers.values); sx['F']=-2*(np.log(sx.p_E)+np.log(sx.p_pers)); sx['p_F']=KE.rank_p(sx.F.values); return sx


def window_ps(o,nul,rng,with_null=True):
    r={}
    for m_ in (4,6,8,10):
        nw=m_*12; w=o[(o.t_s>=PEAK-nw*5/2)&(o.t_s<PEAK+nw*5/2)]; Fm=w.F.max(); r[f'window_{m_}min_look_setting_max']=hmsx(w.t_s[w.F.idxmax()])
        if with_null:
            r[f'window_{m_}min_p_within_segment']=tailp(wmax_null(nul,nw,'within',rng,ndraw=8000),Fm)
            r[f'window_{m_}min_p_block_bootstrap']=tailp(wmax_null(nul,nw,'block',rng,ndraw=8000),Fm)
    return r


def insample_window(o,rng):
    F_=o.F.values; r={}
    for m_ in (4,6,8,10):
        nw=m_*12; w=o[(o.t_s>=PEAK-nw*5/2)&(o.t_s<PEAK+nw*5/2)]; Fm=w.F.max()
        st=rng.integers(0,len(F_)-nw+1,size=4000); v=np.sort([F_[i:i+nw].max() for i in st])
        r[f'window_{m_}min_p_within_segment']=(len(v)-np.searchsorted(v,Fm,'left')+1)/(len(v)+1); r[f'window_{m_}min_look_setting_max']=hmsx(w.t_s[w.F.idxmax()])
    return r


def labels_B(x0,x1,y0,y1,merge=(3,9),minn=15):
    m=txtB[y0:y1,x0:x1]; md=ndi.binary_dilation(m,structure=np.ones(merge)); lab,n=ndi.label(md); out=[]
    for k in range(1,n+1):
        ys,xs=np.where((lab==k)&m)
        if len(xs)<minn: continue
        out.append(dict(xc=x0+(xs.min()+xs.max())/2,yc=y0+(ys.min()+ys.max())/2,w=xs.max()-xs.min()+1,h=ys.max()-ys.min()+1,n=len(xs)))
    return pd.DataFrame(out)


def getimg(xref):
    pix=fitz.Pixmap(d24,xref)
    if pix.n>3 or pix.colorspace.n!=3: pix=fitz.Pixmap(fitz.csRGB,pix)
    return np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)[...,:3].astype(float)


def fig9_corr(p):
    x=f9[p].copy(); k_,y0_,_=LABCAL[p]; x['pressure_pa_label_cal']=(y0_-x.pdf_y_pt)/k_; return x


def consistent(station,t_arr,tol=10.0):
    g=Sb[Sb.station==station].copy(); out=[]
    for model in ('Kadri 1.45-1.57 km/s','WOA23 path bounds'):
        if model.startswith('Kadri'): vlo=np.full(len(g),1.45); vhi=np.full(len(g),1.57)
        else: vlo=g.v_lo_w.values; vhi=g.v_hi_w.values
        a=t_arr-tol-g.dist_km.values/vlo; b=t_arr+tol-g.dist_km.values/vhi
        a2=np.maximum(a,IW[0]); b2=np.minimum(b,IW[1]); ok=b2>=a2
        gg=g.assign(model=model,t_imp_lo=a2,t_imp_hi=b2,ok=ok,vlo=vlo,vhi=vhi); out.append(gg[gg.ok])
    return pd.concat(out)


def pred_spans(cset):
    rows=[]
    for model,cc in cset.groupby('model'):
        for st in STS:
            g=Sb[Sb.station==st].set_index('point_id')
            m=cc[cc.point_id.isin(g.index)]
            if len(m)==0: rows.append(dict(model=model,station=st,n_pts=0)); continue
            gg=g.loc[m.point_id]
            if model.startswith('Kadri'): vlo,vhi=1.45,1.57
            else: vlo=gg.v_lo_2sd.values/1.05/1000; vhi=gg.v_hi_2sd.values/1000
            a=m.t_imp_lo.values+gg.dist_km.values/vhi; b=m.t_imp_hi.values+gg.dist_km.values/vlo
            cls=gg.path_class.values
            rows.append(dict(model=model,station=st,n_pts=len(m),n_blocked=int((cls=='blocked').sum()),arr_lo=a.min(),arr_hi=b.max(),classes=','.join(sorted(set(cls)))))
    return pd.DataFrame(rows)


def imos_check(st,a,b):
    x=s[(s.station==st)&(s.t_s>=a)&(s.t_s<=b)]
    if len(x)==0: return dict(n_looks=0)
    i=x.p_F.idxmin(); return dict(n_looks=len(x),covered_s=round(len(x)*5,0),min_pF=x.p_F.min(),t_min=hmsx(x.t_s[i]),winner=x.winner[i])


def sr_spec(a,b):
    me=(tabs_>=a)&(tabs_<=b); out=[]
    for c in bands_:
        mf=(f_>=c*2**(-1/6))&(f_<c*2**(1/6)); pe=Sxx[np.ix_(mf,me)].mean(); pb=med[mf].mean()
        out.append(dict(band_centre_Hz=c,excess_dB=10*np.log10(pe/pb),signal_dB_rel_bg=10*np.log10((pe-pb)/pb) if pe>pb else np.nan))
    return pd.DataFrame(out)


def lin(D): return 10**(D/10)


def band_level(k,t1,t2,f1=2,f2=40,stat='median'):
    S=SPEC[k]; mt=(S['t']>=t1)&(S['t']<t2); mf=(S['f']>=f1)&(S['f']<=f2); sub=S['D'][np.ix_(mf,mt)]
    return np.median(sub) if stat=='median' else 10*np.log10(np.mean(lin(sub)))


def bands_of(k):
    fmax=SPEC[k]['f'].max(); fmin=SPEC[k]['f'].min()
    return [c for c in BC if c*2**(-1/6)>=fmin-0.01 and c*2**(1/6)<=fmax+0.01]


def spec_excess(k,tc,ev=(-3,12),bgo=(20,90)):
    S=SPEC[k]; t=S['t']; f=S['f']; P=lin(S['D'])
    me=(t>=tc+ev[0])&(t<tc+ev[1]); mb=((t>=tc-bgo[1])&(t<tc-bgo[0]))|((t>=tc+ev[1]+bgo[0]-ev[1]+10)&(t<tc+bgo[1]+10))
    if me.sum()<3 or mb.sum()<20: return None
    rows=[]
    for c in bands_of(k):
        mf=(f>=c*2**(-1/6))&(f<c*2**(1/6))
        pe=P[np.ix_(mf,me)].mean(); pb=P[np.ix_(mf,mb)].mean()
        # noise on pb via column bootstrap would be costly; use per-column band means
        rows.append(dict(fc=c,ev_dB=10*np.log10(pe),bg_dB=10*np.log10(pb),excess_dB=10*np.log10(pe/pb),sig_dB=10*np.log10(pe-pb) if pe>pb else np.nan,
                         n_ev_cols=int(me.sum()),n_bg_cols=int(mb.sum())))
    return pd.DataFrame(rows)


def slope(df,col,fmin=3.0,fmax=40):
    d=df[(df.fc>=fmin)&(df.fc<=fmax)&np.isfinite(df[col])]
    if len(d)<4: return np.nan,len(d)
    return np.polyfit(np.log2(d.fc),d[col],1)[0],len(d)


def slope_se(df,col,fmin=3.0,fmax=40):
    d=df[(df.fc>=fmin)&(df.fc<=fmax)&np.isfinite(df[col])]
    if len(d)<4: return np.nan,np.nan
    x=np.log2(d.fc.values); y=d[col].values; c_,cov=np.polyfit(x,y,1,cov=True); return c_[0],np.sqrt(cov[0,0])


def arc_series(k):
    Lp,Lm,an,tmin,brg,bg=out[k]; cs=res[k][0]
    rows=(brg>=lo_img)&(brg<=hi_img); sub=np.where(np.isnan(Lm[rows]),bg,Lm[rows])-bg
    i=np.argmax(sub,0)
    return pd.DataFrame(dict(panel=k,t_s=cs.t_s_rel_0800.values,t_utc=cs.t_utc.values,arc_max_excess=sub.max(0),arc_brg_img=brg[rows][i],annot=cs.annotation_in_col.values))


def arc_scan(k,t1,t2):
    Lp,Lm,an,tmin,brg,bg=out[k]; cs,bl,R=res[k]
    tt=cs.t_s_rel_0800.values; m=(tt>=t1)&(tt<=t2); rows=(brg>=lo_img)&(brg<=hi_img)
    sub=np.where(np.isnan(Lm[np.ix_(rows,m)]),bg,Lm[np.ix_(rows,m)])-bg; Rs=R[np.ix_(rows,m)]
    i,j=np.unravel_index(np.nanargmax(sub),sub.shape); i2,j2=np.unravel_index(np.nanargmax(Rs),Rs.shape)
    nz=(sub>0.5).sum()
    return dict(panel=k,cols=m.sum(),max_excess=sub[i,j],t_max=cs.t_utc.values[m][j],brg_max=brg[rows][i],max_resid=Rs[i2,j2],t_resid=cs.t_utc.values[m][j2],brg_resid=brg[rows][i2],n_px_excess_gt0p5=int(nz),n_px=sub.size)


def figA(jon=False):
    W_in=5.0 if jon else 7.5; H_in=6.4 if jon else 9.0
    fig=plt.figure(figsize=(W_in,H_in))
    gs=fig.add_gridspec(3,1,height_ratios=[1,0.8,2.2],left=0.13 if jon else 0.11,right=0.97,top=0.98 if jon else 0.95,bottom=0.08 if jon else 0.25,hspace=0.12)
    ax1=fig.add_subplot(gs[0]); ax2=fig.add_subplot(gs[1],sharex=ax1); ax3=fig.add_subplot(gs[2],sharex=ax1)
    for a_ in (ax1,ax2): a_.axvspan(EARLY,LATEST,color='0.88',zorder=0,lw=0)
    d_=F4o[F4o.t_s_rel_0800>=0].sort_values('t_s_aligned_to_fig9')
    ax1.plot(d_.t_s_aligned_to_fig9,d_.half_peak_to_peak_Pa,color='k',lw=0.8,label='Kadri (2019) Fig. 4')
    cen=np.arange(3607.5,4800,15.0); mx,mn=bin_extremes(f9c.t.values,f9c.pressure_pa_label_cal.values,cen,7.5)
    ax1.plot(cen,(mx-mn)/2,color='0.45',lw=0.8,ls='--',label='Kadri (2024) Fig. 9, re-calibrated')
    ax1.set_ylabel('Half peak-to-peak\npressure (Pa)'); ax1.set_ylim(0,4.4)
    ax1.legend(loc='upper left',frameon=False,fontsize=6,ncol=2)
    ax1.annotate('01:10:15',xy=(4215,3.2),xytext=(4215+900,3.2),fontsize=6,va='center',arrowprops=dict(arrowstyle='-',lw=0.5))
    ax1.text(EARLY+60,0.25,'span of possible arrivals from the 7th arc',fontsize=6)
    d2=d_.dropna(subset=['xcorr_rms_upper'])
    ax2.plot(d2.t_s_aligned_to_fig9,d2.xcorr_rms_upper,color='k',lw=0.8); ax2.set_ylabel('Cross-correlation\nRMS, upper edge')
    for k in ('HA31','HA32'):
        Lp,Lm,an,tmin,brg,bg=out[k]; cs=res[k][0]; ex=np.nan_to_num(Lm,nan=bg)-bg; t_=cs.t_s_rel_0800.values; b_=brg-OFF
        ax3.imshow(np.clip(ex,0,40),aspect='auto',cmap='Greys',vmin=0,vmax=20,extent=[t_[0],t_[-1],b_[-1],b_[0]],origin='upper',interpolation='nearest',zorder=1)
    ax3.set_ylim(0,360); ax3.set_ylabel('Bearing from Diego Garcia South (deg)')
    for yy in (ARC_LO,ARC_HI): ax3.axhline(yy,color='k',ls='--',lw=0.7,zorder=2)
    for yy in (ARC_LO-MARG,ARC_HI+MARG): ax3.axhline(yy,color='k',ls=':',lw=0.6,zorder=2)
    ax3.text(120,141,'directions to the 7th arc, 20-41 S (dashed)\nwith 6 deg margin (dotted)',fontsize=6,va='center',zorder=3)
    ax3.text(120,309+7,'309 deg shot train',fontsize=6,zorder=3); ax3.text(120,219+7,'219 deg shot train',fontsize=6,zorder=3)
    for xx in (EARLY,LATEST): ax3.axvline(xx,color='k',lw=0.7,ls='-',zorder=2)
    for a_ in (ax1,ax2,ax3): a_.axvline(4215,color='k',lw=0.6,ls='-.',zorder=2)
    tr_=TT[TT.in_arrival_span&(TT.shot_label=='')&(TT.panel!='HA30')]
    ax3.scatter(tr_.t_s_rel_0800,tr_.brg_kadri_ref,s=26,facecolors='none',edgecolors='k',lw=0.6,zorder=3,label='transient outside the shot-train directions')
    kn=TT[TT.note!='']; kn=kn[kn.panel!='HA30']
    ax3.scatter(kn.t_s_rel_0800,kn.brg_kadri_ref,s=30,marker='s',facecolors='none',edgecolors='k',lw=0.7,zorder=3,label='Kadri (2019) Table 3 signal')
    ax3.legend(loc='lower left',frameon=True,framealpha=0.9,edgecolor='none',fontsize=6)
    ax3.set_xlim(0,7140); ax3.set_xlabel('Time on 8 March 2014 (UTC)'); tfmt(ax3); ax3.xaxis.set_major_locator(mpl.ticker.MultipleLocator(900))
    plt.setp(ax1.get_xticklabels(),visible=False); plt.setp(ax2.get_xticklabels(),visible=False)
    if not jon:
        fig.suptitle('Diego Garcia South, 00:00 to 02:00 UTC: no transient points towards the 7th arc',x=0.11,ha='left',fontsize=9)
        add_footnote(fig,
          'Data are read from the published figure of Kadri (2019), Fig. 4, not from raw recordings. Vertical lines and grey bands show when sound from an impact on the 7th arc between 00:19:38 and 00:55:00 can arrive. '
          'No transient in that time points towards the arc. The two strong lines are airgun shot trains that Kadri names. They are labels only; they do not remove data. The direction bias of this station is not calibrated.',
          'Source raster 1650 x 1613 px (lossless). Image: 10.4-10.8 s/px, 0.577 deg/px; trace and cross-correlation: 15.0-15.6 s/px, 0.0148-0.0317 Pa/px. Tick-fit residual <= 0.43 px (image), <= 0.61 px (trace). '
          'Image intensity: CIELAB L* above background (parula, no colour bar; relative only). Bearing = image reading minus 2.58 deg (sd 0.51, n = 5 checks against Kadri text values). '
          'Trace time shifted -19 s to match Fig. 9 (best lag; correlation within 0.02 of best over -35 to 0 s). Fig. 9 re-calibrated from its tick labels; Fig. 4 amplitude is 0.74 x Fig. 9 (median), correlation 0.86. Gap 00:15-00:18 is missing data in the source. '
          'Arrival span 00:56:34-01:42:18 (1.465-1.520 km/s, unblocked points within 150 NM). Arc directions: grid_ext_paths_wide.csv, H08S, 114.5-168.6 deg. Assumed bearing uncertainty 6 deg. '
          'Transient: connected pixels > 4 L* above a 31-column running median, outside +-5 deg of the shot lines.')
    return fig



def add_footnote(fig, ste, tech, frac=0.24, fs=6.2, width=170):
    s='\n'.join(textwrap.wrap('Plain summary: '+ste,width))+'\n'+'\n'.join(textwrap.wrap('Technical: '+tech,width))
    fig.text(0.01,0.005,s,ha='left',va='bottom',fontsize=fs,family='sans-serif',linespacing=1.15)


def tfmt(ax,t0=0):
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v,p: f"{int((v%86400)//3600):02d}:{int((v%3600)//60):02d}"))


def jon_versions(name,fn):
    fig=fn(jon=True); fig.savefig(O+f'/{name}-word.png',dpi=600); fig.savefig(O+f'/{name}-jon.pdf'); plt.close(fig)
    open(O+f'/{name}-caption.txt','w').write(CAP[name]+'\n')
    # proof: image + caption below
    img=PImage.open(O+f'/{name}-word.png'); wpx,hpx=img.size
    fig=plt.figure(figsize=(5.0,hpx/wpx*5.0+1.3)); ax=fig.add_axes([0,1.3/(hpx/wpx*5.0+1.3),1,1-1.3/(hpx/wpx*5.0+1.3)]); ax.imshow(np.asarray(img.convert('L')),cmap='gray',vmin=0,vmax=255); ax.axis('off')
    fig.text(0.02,0.01,'\n'.join(textwrap.wrap('Figure X. '+CAP[name],115)),fontsize=6.5,va='bottom',ha='left')
    fig.savefig(O+f'/{name}-proof.png',dpi=200); plt.close(fig)


def traces_tau(kv, station, tau_fixed=None, binw=0.1):
    d = kv[kv.station == station].sort_values('t_s')
    t0, t1 = np.floor(d.t_s.min()), np.ceil(d.t_s.max())
    edges = np.arange(t0, t1 + binw, binw); idx = np.digitize(d.t_s.values, edges) - 1
    env = np.full(len(edges) - 1, np.nan); a = np.abs(d.pressure_pa.values)
    np.fmax.at(env, idx[(idx>=0)&(idx<len(env))], a[(idx>=0)&(idx<len(env))])
    isn = np.isnan(env); lab, n = ndi.label(isn)
    for k in range(1, n + 1):
        w = np.where(lab == k)[0]
        if len(w) <= 2 and w[0] > 0: env[w] = env[w[0] - 1]
    t=edges[:-1]
    y = 20 * np.log10(np.maximum(env, 1e-12)); y[~np.isfinite(env)] = np.nan
    p2 = env ** 2; tau = KE.thin_lag(y) if tau_fixed is None else tau_fixed
    cent = np.arange(t[0] + 15, t[-1] - 15 + 1e-6, 5.0)
    E = np.full(len(cent), np.nan); P = np.full(len(cent), np.nan)
    nb=int(round(0.1/binw))
    for j, c in enumerate(cent):
        w = (t >= c - 15) & (t < c + 15)
        r = ((t >= c - 225) & (t < c - 45)) | ((t >= c + 45) & (t < c + 225))
        wv, rv = p2[w], p2[r]
        if np.isfinite(wv).mean() < 0.8 or np.isfinite(rv).sum() < 60.0/binw: continue
        E[j] = 10 * np.log10(np.nanmean(wv) / np.nanmedian(rv))
        yw = y[w][::tau]; yw = yw[np.isfinite(yw)]; k = int((yw > np.nanmedian(y[r])).sum())
        P[j] = -np.log10(max(binom.sf(k - 1, len(yw), 0.5), 1e-300))
    return pd.DataFrame(dict(station=station, t_s=cent, E=E, pers=P, tau=tau)).dropna(subset=['E','pers']).reset_index(drop=True)


def traces_tau_b(kv, station, tau_fixed=None, binw=0.1, boundary=None):
    d = kv[kv.station == station].sort_values('t_s')
    t0, t1 = np.floor(d.t_s.min()), np.ceil(d.t_s.max())
    edges = np.arange(t0, t1 + binw, binw); idx = np.digitize(d.t_s.values, edges) - 1
    env = np.full(len(edges) - 1, np.nan); a = np.abs(d.pressure_pa.values)
    np.fmax.at(env, idx[(idx>=0)&(idx<len(env))], a[(idx>=0)&(idx<len(env))])
    isn = np.isnan(env); lab, n = ndi.label(isn)
    for k in range(1, n + 1):
        w = np.where(lab == k)[0]
        if len(w) <= 2 and w[0] > 0: env[w] = env[w[0] - 1]
    t=edges[:-1]
    y = 20 * np.log10(np.maximum(env, 1e-12)); y[~np.isfinite(env)] = np.nan
    p2 = env ** 2; tau = KE.thin_lag(y) if tau_fixed is None else tau_fixed
    cent = np.arange(t[0] + 15, t[-1] - 15 + 1e-6, 5.0)
    E = np.full(len(cent), np.nan); P = np.full(len(cent), np.nan)
    nb=int(round(0.1/binw))
    for j, c in enumerate(cent):
        w = (t >= c - 15) & (t < c + 15)
        r = ((t >= c - 225) & (t < c - 45)) | ((t >= c + 45) & (t < c + 225))
        if boundary is not None:
            r = r & ((t >= boundary) == (c >= boundary)); w = w & ((t >= boundary) == (c >= boundary))
        wv, rv = p2[w], p2[r]
        if np.isfinite(wv).mean() < 0.8 or np.isfinite(rv).sum() < 60.0/binw: continue
        E[j] = 10 * np.log10(np.nanmean(wv) / np.nanmedian(rv))
        yw = y[w][::tau]; yw = yw[np.isfinite(yw)]; k = int((yw > np.nanmedian(y[r])).sum())
        P[j] = -np.log10(max(binom.sf(k - 1, len(yw), 0.5), 1e-300))
    return pd.DataFrame(dict(station=station, t_s=cent, E=E, pers=P, tau=tau)).dropna(subset=['E','pers']).reset_index(drop=True)


def figB(jon=False):
    W_in=5.0 if jon else 7.5; H_in=5.6 if jon else 8.2
    fig=plt.figure(figsize=(W_in,H_in))
    gs=fig.add_gridspec(3,1,height_ratios=[1,1.2,1.1],left=0.13 if jon else 0.11,right=0.97,top=0.98 if jon else 0.95,bottom=0.09 if jon else 0.26,hspace=0.42)
    ax1=fig.add_subplot(gs[0]); ax2=fig.add_subplot(gs[1],sharex=ax1); ax3=fig.add_subplot(gs[2])
    JC2=[]
    for c in np.arange(3600,4800,30.0):
        m=(tt>=c)&(tt<c+30); mc=(ttc>=c)&(ttc<c+30); JC2.append((c+15,np.median(pp[m]),np.median(ppc[mc])))
    JC2=np.array(JC2)
    ax1.plot(JC2[:,0],JC2[:,1],color='0.45',ls='--',marker='o',ms=2.5,lw=0.8,label='as held in the project database (used 6 Nov)')
    ax1.plot(JC2[:,0],JC2[:,2],color='k',marker='s',ms=2.5,lw=0.8,label='re-calibrated from the figure tick labels')
    ax1.axvline(4200,color='k',lw=0.6,ls=':'); ax1.text(4210,0.04,'join of panels d and e (01:10:00)',fontsize=6)
    ax1.set_ylabel('Median |pressure|\nper 30 s (Pa)'); ax1.set_ylim(0,0.6); ax1.legend(loc='upper left',frameon=False,fontsize=6)
    s_db=series_store[list(variants)[0]][0]; nul1=series_store[list(variants)[0]][1]
    ax2.plot(s8.t_s,s8.E,color='0.45',ls='--',lw=0.8,label='as held in the database')
    ax2.plot(sC.t_s,sC.E,color='k',lw=0.9,label='re-calibrated')
    ax2.axhline(nul1.E.max(),color='k',lw=0.6,ls='-.'); ax2.text(4790,nul1.E.max()-0.75,'maximum on 7 March (Fig. S1 a-c)',fontsize=6,ha='right')
    ax2.axvline(4215,color='k',lw=0.6,ls=':'); ax2.text(4225,7.6,'01:10:15',fontsize=6)
    ax2.set_ylabel('Band energy over\nlocal ring (dB)'); ax2.legend(loc='upper left',frameon=False,fontsize=6); ax2.set_xlabel('Time on 8 March 2014 (UTC)')
    tfmt(ax2); ax2.xaxis.set_major_locator(mpl.ticker.MultipleLocator(120)); ax2.set_xlim(3600,4800)
    # panel 3: per-look p at 01:10:15
    labs_=['same 8 March\ntrace (6 Nov\nmethod)','7 March,\nas digitised','7 March,\nfixed\nthinning lag','7 March,\nthinned to 8\nMarch rate','7 March,\n1 s envelope\nbins']
    bt_db=Bt[Bt.input.str.startswith('Fig. 9 d-e as held')].per_look_p_F.values; bt_c=Bt[Bt.input.str.startswith('Fig. 9 d-e re-cal')].per_look_p_F.values
    x_=np.arange(5)
    ax3.scatter(x_-0.08,bt_db,marker='o',facecolors='none',edgecolors='0.35',s=24,label='as held in the database')
    ax3.scatter(x_+0.08,bt_c,marker='s',color='k',s=20,label='re-calibrated')
    ax3.set_yscale('log'); ax3.set_ylim(1e-3,1.5); ax3.axhline(0.01,color='0.6',lw=0.5,ls=':')
    ax3.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v,p: f'{v:g}'))
    ax3.set_xticks(x_); ax3.set_xticklabels(labs_,fontsize=6); ax3.set_ylabel('Per-look p at 01:10:15\n(lower = more unusual)'); ax3.set_xlim(-0.5,4.5)
    ax3.legend(loc='lower left',bbox_to_anchor=(0,1.0),ncol=2,frameon=False,fontsize=6); ax3.set_xlabel('Background used for the test')
    if not jon:
        fig.suptitle('Diego Garcia South 01:10:15: the peak came from a scale error at a figure-panel join',x=0.11,ha='left',fontsize=9)
        add_footnote(fig,
          'The 6 November peak at 01:10:15 starts exactly where two panels of Kadri (2024) Fig. 9 join. The digitised pressure scale of both panels was wrong, so the background level stepped up by 8 dB at the join. '
          'With the scale read again from the tick labels, the step goes, and 01:10:15 is an ordinary look. The airgun shots on 8 March keep the level above the 7 March maximum for most of the trace, so the 7 March background is not fully comparable. The 7 March traces of Fig. S1 serve as an independent background. The trace is a digitised figure, not a raw recording.',
          'Database table dg_data_kadri_fig9_* panels d, e used 16.33 and 8.16 pt/Pa with zero at 404.72 and 511.70 pt; the tick labels give 10.87 and 7.25 pt/Pa with zero at 404.61 and 508.00 pt (fit residual <= 0.007 Pa). '
          'Panel c (Cape Leeuwin) is also off: 32.65 against 29.63 pt/Pa and 1.8 pt zero offset. Fig. S1 a-c digitisation checked against its text labels: exact. Statistic: 6 Nov band energy E (30 s window over the median of a 180 s ring outside a 30 s guard) and envelope persistence, combined by Fisher; '
          'per-look p = (count of background F >= F + 1)/(N + 1); background N = 349-355 looks (30 min). Spectrogram median level 2-40 Hz: 72.3 dB before and 71.7 dB after the join (no step). Window p for 4-10 min windows: see dgs_envelope_null_rescore_0110.csv.')
    return fig


def figC(jon=False):
    W_in=5.0 if jon else 7.5; H_in=6.0 if jon else 8.4
    fig=plt.figure(figsize=(W_in,H_in))
    gs=fig.add_gridspec(3,1,height_ratios=[1.3,0.9,1.0],left=0.13 if jon else 0.11,right=0.97,top=0.98 if jon else 0.95,bottom=0.09 if jon else 0.26,hspace=0.45)
    ax1=fig.add_subplot(gs[0]); ax2=fig.add_subplot(gs[1],sharex=ax1); ax3=fig.add_subplot(gs[2])
    mf=(f_>=5)
    SdBn=SdB-np.median(SdB,axis=1,keepdims=True)
    im=ax1.pcolormesh(tabs_,f_[mf],SdBn[mf],cmap='Greys',vmin=0,vmax=30,shading='nearest',rasterized=True)
    cb=fig.colorbar(im,ax=ax1,pad=0.01,fraction=0.04); cb.set_label('dB above the\nrecord median',fontsize=6); cb.ax.tick_params(labelsize=6)
    ax1.set_ylabel('Frequency (Hz)'); ax1.axvline(TP,color='k',lw=0.7,ls='--'); ax1.text(TP+3,112,'pick 01:32:51',fontsize=6)
    ax2.plot(tabs_,be,color='0.5',lw=0.6,label='band energy 8-40 Hz, 2 s steps (dB above record median)')
    ax2.set_ylabel('Band energy (dB)'); ax2.axvline(TP,color='k',lw=0.7,ls='--')
    ax2b=ax2.twinx(); ax2b.plot(sr_look.t_s,sr_look.p_F,color='k',lw=1.0,marker='o',ms=2,label='combined detector p (6 Nov), 30 s looks')
    ax2b.set_yscale('log'); ax2b.set_ylim(1e-4,1.2); ax2b.set_ylabel('Detector p',fontsize=7); ax2b.tick_params(labelsize=6)
    ax2b.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v,p: f'{v:g}'))
    h1,l1=ax2.get_legend_handles_labels(); h2,l2=ax2b.get_legend_handles_labels(); ax2.legend(h1+h2,l1+l2,loc='lower left',bbox_to_anchor=(0,1.0),ncol=2,frameon=False,fontsize=6)
    ax2.set_ylim(-15,40)
    tfmt(ax2); ax2.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v,p: hmsx(v)[:8])); ax2.set_xlim(tabs_[0],tabs_[-1]); ax2.set_xlabel('Time on 8 March 2014 (UTC, clock-corrected)')
    plt.setp(ax1.get_xticklabels(),visible=False)
    for (lbl,mk,ls) in (('01:32:40-01:32:46 (first pulse)','o','--'),('01:32:47.5-01:32:54 (pulse at the pick)','s','-')):
        d_=SRspec[SRspec.window==lbl]; ax3.plot(np.log2(d_.band_centre_Hz),d_.excess_dB,marker=mk,ls=ls,color='k',ms=3,lw=0.8,label=lbl.replace('(',' ').replace(')',''))
    xx=np.log2(np.array([10,100])); ax3.plot(xx,26-7*(xx-np.log2(10)),color='0.55',lw=0.8,ls=':',label='slope of the impact families (-7 dB/octave)')
    ax3.set_xticks(np.log2(bands_)); ax3.set_xticklabels([f'{b:g}' for b in bands_],fontsize=6); ax3.set_xlabel('One-third-octave band centre (Hz)')
    ax3.set_ylabel('Excess over record\nmedian (dB)'); ax3.legend(loc='lower right',frameon=False,fontsize=6); ax3.set_ylim(-28,36)
    if not jon:
        fig.suptitle('Scott Reef 01:32:51: a broadband pulse peaking at 50-63 Hz, not impact-like',x=0.11,ha='left',fontsize=9)
        add_footnote(fig,
          'This is the raw Scott Reef recording (logger 3250) at the time of the third pick in the report to the ATSB. Calls at 20-45 Hz repeat through the record. A strong short broadband pulse is present at the pick. Its energy is highest at 50-63 Hz and does not fall with frequency as an impact would. '
          'Only arc points at 32-34 S with impact at 00:51:30-00:55:00 fit its time inside the project grid; those paths have large attenuation. No other site shows a matching event in the predicted spans.',
          'Record 531A... (seq 6), start 01:29:44.9 UTC after clock correction (logger 15.1 s late), 250 Hz after resampling, 8 Hz hardware high-pass; spectrogram 512-sample Hann windows (2.05 s, 0.49 Hz), 75 % overlap. '
          'Combined detector p from run14v5_final/station_point_series.csv (calibrated on the background records of 8 March); p = 0.0138-0.0153 at 01:32:50-01:32:55, winning clutter class "earthquake". '
          'Pick time from the 7 Nov audit (Kadri, Crivelli and Parsons 2017, Fig. 6; logger 01:33:06). Arc consistency: speeds 1.45-1.57 km/s and WOA23 March path bounds (slow side divided by 1.05), pick tolerance +-10 s, impact window 00:19:38-00:55:00. Excess dB is not corrected for the hydrophone response.')
    return fig


def figD(jon=False):
    W_in=5.0 if jon else 7.5; H_in=6.4 if jon else 9.0
    fig,axs=plt.subplots(4,2,figsize=(W_in,H_in),sharex=True,sharey=True)
    fig.subplots_adjust(left=0.12,right=0.98,top=0.98 if jon else 0.95,bottom=0.08 if jon else 0.27,hspace=0.35,wspace=0.06)
    names={'00:36:07.0':'Cape Leeuwin 00:36:07','00:47:04.0':'Cape Leeuwin 00:47:04','00:49:58.0':'Cape Leeuwin 00:49:58','00:51:50.0':'Cape Leeuwin 00:51:50',
           '00:54:30.0':'Cape Leeuwin 00:54:30','00:55:07.0':'Cape Leeuwin 00:55:07','01:10:15.0':'Diego Garcia South 01:10:15'}
    for ax,(t_,nm) in zip(axs.flat,names.items()):
        g=DB_[(DB_.t==t_)&(DB_.ev=='-3 to +12 s')]; g2=DB_[(DB_.t==t_)&(DB_.ev=='-2 to +5 s')]
        k=g.panel.iloc[0] if 'panel' in g else None
        k=[x[1] for x in TARG if hmsx(x[2])==t_][0]
        nl,nb,q95=NULLW[(k,(-3,12))]; q05=nl.groupby('fc').excess_dB.quantile(0.05)
        xb=np.log2(q95.index.values)
        ax.fill_between(xb,q05.values,q95.values,color='0.85',lw=0)
        ax.plot(np.log2(g.fc),g.excess_dB,color='k',marker='s',ms=2.5,lw=0.9)
        ax.plot(np.log2(g2.fc),g2.excess_dB,color='0.4',marker='o',ms=2.2,lw=0.7,ls='--')
        ax.axhline(0,color='0.5',lw=0.4)
        r=DR[(DR.t==t_)&(DR.ev=='-3 to +12 s')].iloc[0]
        ss='n/a' if not np.isfinite(r.signal_slope_dB_oct_3_40) else f'{r.signal_slope_dB_oct_3_40:+.1f} +- {r.signal_slope_se:.1f}'
        ax.text(0.02,0.97,f'{nm}\nbroadband {r.broadband_excess_dB:+.1f} dB (p {r.p_broadband:.2f})\nsignal slope {ss} dB/oct',transform=ax.transAxes,fontsize=5.6,va='top')
    ax=axs.flat[-1]; ax.axis('off')
    ax.plot([],[],color='k',marker='s',ms=2.5,label='event window -3 to +12 s'); ax.plot([],[],color='0.4',marker='o',ls='--',ms=2.2,label='event window -2 to +5 s')
    ax.fill_between([],[],[],color='0.85',label='5-95 % range of the same\nstatistic at random times'); ax.legend(loc='center',frameon=False,fontsize=6)
    for a_ in axs[-1]: a_.set_xticks(np.log2([2.5,5,10,20,40])); a_.set_xticklabels(['2.5','5','10','20','40'])
    axs[-1,0].set_xlabel('One-third-octave band centre (Hz)'); axs[2,1].tick_params(labelbottom=True); axs[2,1].set_xlabel('One-third-octave band centre (Hz)')
    for a_ in axs[:,0]: a_.set_ylabel('Excess over local\nbackground (dB)')
    axs[0,0].set_ylim(-12,14)
    if not jon:
        fig.suptitle('Relative spectra at the candidate times (Kadri 2024 Fig. 9): no clear impact-shaped excess',x=0.12,ha='left',fontsize=9)
        add_footnote(fig,
          'Each panel compares the spectrum at one candidate time with the spectrum 20-90 s before and after it in the same panel of the figure. The colours are read as relative levels only; the absolute reading is about 15 dB low. '
          'Impact sound is expected to fall by about 7 dB per octave above 3 Hz. 00:51:50 comes nearest (low-frequency excess), but its slope is shallower. 00:36:07 is a 10-25 Hz band, 00:47:04 is flat, 00:54:30 peaks at 3 Hz. 00:49:58, 00:55:07 and 01:10:15 show no clear excess.',
          'Source: embedded JPEG rasters 754-762 x 272-277 px; 0.785-0.791 s/px; 0.141 Hz/px (Diego Garcia South 0-60 Hz panel: 0.211 Hz/px); JPEG chroma subsampling halves colour resolution. '
          'Band 1.8-40 Hz (lowest row 1.8-1.9 Hz). Colour-bar mapping by nearest colour, 0.17-0.19 dB per colour-bar row; median colour distance 15-18 RGB units. Tick-fit residual <= 1.3 px (time), <= 0.33 px (frequency). '
          'Background: columns 20-90 s before and 30-100 s after the event, same panel. Random-time reference: 400 windows per panel, excluding +-30 s of the candidates. Signal slope: least-squares fit of 10 log10(P_event - P_background) over 3-40 Hz bands with positive excess; +- is the fit standard error. Bearings are not used.')
    return fig
