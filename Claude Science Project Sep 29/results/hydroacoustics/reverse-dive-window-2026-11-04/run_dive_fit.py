# Driver for reverse-dive-window-2026-11-04: python cells as executed (4 Nov 2026), in order. Cells that failed are omitted.
# Needs dive_fit_lib.py (same folder) and host.artifact_path for inputs; 'apply_figure_style' comes from the figure-style skill.
import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
import dive_fit_lib as D
ev=pd.read_csv(host.artifact_path('23f70536-b765-489b-abb7-cfe0e1089f7e'))  # boeing-end-of-flight-runs-table.csv

# ---- cell 2908ff9a-a4e6-4a91-88b3-8ca21a9073dc ----
import numpy as np, pandas as pd, time
D.ev=ev
print(D.bto('m0019a',-37.2,89.64,30000), D.bto_v('m0019a',np.array([-37.2]),np.array([89.64]),np.array([30000.]))[0])
print(D.OBS, D.DT11, D.DT37, D.LAGS[[0,-1]], D.ROT[[0,-1]], D.LATS[[0,-1]])
EV=ev.set_index('run')
t0=time.time(); par={}
for r in (3,4,6,10):
    s,P=D.splice(D.run_raw(f"Case {r:02d}.csv"),float(EV.loc[r,'autopilot lost s']))
    for v in ('observed','holland'):
        df=D.score_path(s,P,v); df['noLag']=df.tot-df.lag_pen
        b=df.loc[df.noLag.idxmin()]; par[(r,v)]=(round(b.noLag,1),b.L)
print(par, time.time()-t0)


# ---- cell 41c90278-add8-4cf0-8eed-bbfe20f616ec ----
import datetime as dt
D.LATS=np.round(np.arange(-41.0,-19.45,0.1),2); D.LAGS=np.arange(30,901,1); D.ROT=np.arange(-30,31,2.0)
FO_LEVEL=800.0
def first_fo_rel(r):  # first flame-out time relative to power loss (s)
    e=EV.loc[r]; return float(e['first flame-out s'])-float(e['autopilot lost s'])
runs=[(3,'alternate',None),(4,'alternate',None),(6,'alternate',None),(10,'alternate',None),(5,'normal',None)]
# run 5 one-engine-phase variants (prior session's splice gap variants), sensitivity only
e5=EV.loc[5]; native5=float(e5['autopilot lost s'])-float(e5['first flame-out s'])
runs+= [(5,'normal',g*60) for g in (4,6,8,10,12,14) if g*60<=native5-5]
print(native5, runs)
RAW={r:D.run_raw(f"Case {r:02d}.csv") for r in (3,4,5,6,10)}
FITS={}
t0=time.time()
for r,cfg,g in runs:
    e=EV.loc[r]; tu=float(e['autopilot lost s']); t1=float(e['first flame-out s'])
    s,P=D.splice(RAW[r],tu,t1=t1 if g else None,g=g)
    fo=(-g if g else first_fo_rel(r))   # first flame-out rel. power loss on the spliced axis
    for v in ('holland','observed'):
        df=D.score_path(s,P,v); df['noLag']=df.tot-df.lag_pen
        df['fo_rel_0011']=fo-(df.L-D.DT11)          # first FO minus 00:10:59 on s axis (<0: FO before 00:10:59)
        df['fo_before_0011']=df.fo_rel_0011<0
        df['keep']=(~df.fo_before_0011)|(df.vu11.abs()<=FO_LEVEL)
        FITS[(r,g,v)]=(s,P,df)
print('done', time.time()-t0)
for k,(s,P,df) in FITS.items():
    k2=df[df.keep]
    if len(k2)==0: print(k,'no kept alignment', len(df)); continue
    b=k2.loc[k2.noLag.idxmin()]
    print(k, 'n',len(df),'kept',len(k2), 'best',round(b.noLag,1),'L',b.L,'rot',b.rot,'lat11',b.lat11,'D29',round(b.D29,1),'vu11',b.vu11, 'Lrange',df.L.min(),df.L.max())


# ---- cell 44d3b484-6eb9-4aea-83ce-8fbd51b9eb65 ----
D.ROT=np.arange(-60,61,2.0)
ROTW={}
t0=time.time()
for r in (3,4,6,10):
    s,P,_=FITS[(r,None,'holland')]
    for v in ('holland','observed'):
        df=D.score_path(s,P,v); df['noLag']=df.tot-df.lag_pen; ROTW[(r,v)]=df
        b=df.loc[df.noLag.idxmin()]; prof=df.groupby('L').noLag.min(); ok=prof[prof<=prof.min()+4]
        print(r,v,'best',round(b.noLag,1),'L',b.L,'rot',b.rot,'lat11',b.lat11,'trk29',round(b.trk29), ' dchi<=4 L',ok.index.min(),ok.index.max())
print(time.time()-t0)
D.ROT=np.arange(-30,31,2.0)
# initial simulator track (deg) at run start for each run
for r in (3,4,6,10,5):
    R=RAW[r]; print(r,'initial track',round(np.degrees(np.arctan2(R['ve'][5],R['vn'][5]))%360,1))


# ---- cell a3a1decd-e7e8-4f33-a9b1-41983c358ccf ----
def end_state(r):
    R=RAW[r]; k=slice(-10,None)
    ve=R['ve'][k].mean(); vn=R['vn'][k].mean(); vz=(R['vu'][k].mean())*0.3048/60   # kt, kt, m/s
    h_end=R['h'][-1]*0.3048; dt_sea=h_end/max(-vz,5.08)
    return dict(t_end=R['t'][-1], e_imp=R['e'][-1]+ve/3600*dt_sea, n_imp=R['n'][-1]+vn/3600*dt_sea, dt_sea=dt_sea, h_end_ft=R['h'][-1])
ES={r:end_state(r) for r in (3,4,5,6,10)}
print({r:(round(v['t_end']),round(v['dt_sea'],1)) for r,v in ES.items()}, 'ev tend', EV.loc[[3,4,5,6,10],'end of record s'].tolist())

def geom(r,g,s,P,L,th,lat11):
    e=EV.loc[r]; tu=float(e['autopilot lost s']); es=ES[r]
    t_imp_rel=es['t_end']+es['dt_sea']-tu                 # s after power loss (run's own splice axis for as-flown)
    if g: t_imp_rel=t_imp_rel   # gap variants keep the same post-power-loss segment
    imp=D.T0-dt.timedelta(seconds=float(L))+dt.timedelta(seconds=float(t_imp_rel))
    i11=np.searchsorted(s,L-D.DT11); i37=np.searchsorted(s,L+D.DT37)
    c,sn=np.cos(np.radians(th)),np.sin(np.radians(th))
    rot=lambda E,N:(E*c+N*sn,-E*sn+N*c)
    # impact position on the spliced axis: last spliced sample + tail beyond splice end to the sea
    iend=len(s)-1; R=RAW[r]
    # for as-flown, spliced index iend maps to run time s+tu; the extrapolated impact is in run (e,n)
    if g is None:
        e_imp,n_imp=es['e_imp'],es['n_imp']; e37,n37=P['e'][i37],P['n'][i37]; e11,n11=P['e'][i11],P['n'][i11]
    else:  # gap splice positions are chained; offset run end by the chain shift at s>=0
        itu=int(round(tu)); shift_e=P['e'][np.searchsorted(s,0)]-R['e'][min(itu,len(R['e'])-1)]; shift_n=P['n'][np.searchsorted(s,0)]-R['n'][min(itu,len(R['n'])-1)]
        e_imp,n_imp=es['e_imp']+shift_e,es['n_imp']+shift_n; e37,n37=P['e'][i37],P['n'][i37]; e11,n11=P['e'][i11],P['n'][i11]
    de,dn=rot(e_imp-e37,n_imp-n37)
    ue,un=rot(P['ve'][i11],P['vn'][i11]); nu=np.hypot(ue,un); ue,un=ue/nu,un/nu
    along=de*ue+dn*un; cross=de*un-dn*ue      # cross-track positive to the right of the 00:10:59 track
    lon0=D.arc6(lat11,P['h'][i11])
    def ll(E,N):
        d_e,d_n=rot(E-e11,N-n11); return lat11+d_n/60.0, lon0+d_e/(60*np.cos(np.radians(lat11)))
    lat37,lon37=ll(e37,n37); latI,lonI=ll(e_imp,n_imp)
    trk11=np.degrees(np.arctan2(ue,un))%360
    return dict(impact=imp,t_imp_after_0019_37=(imp-(D.T0+dt.timedelta(seconds=D.DT37))).total_seconds(),along_nm=along,cross_nm=cross,dist_nm=np.hypot(de,dn),
                lat37=lat37,lon37=lon37,lat_imp=latI,lon_imp=lonI,trk0011=trk11,first_fo=(D.T0-dt.timedelta(seconds=float(L))+dt.timedelta(seconds=(-g if g else first_fo_rel(r)))))

rows=[]; prof_all={}
for (r,g,v),(s,P,df) in FITS.items():
    k=df[df.keep].copy()
    for crit in ('noLag','tot'):
        idx=k.groupby('L')[crit].idxmin(); prof=k.loc[idx].set_index('L')
        m=prof[crit].min(); ok=prof[prof[crit]<=m+4]; best=prof[crit].idxmin()
        G=pd.DataFrame([geom(r,g,s,P,L,q.rot,q.lat11)|dict(L=L,chi2=q[crit],rot=q.rot,D29=q.D29,lat11=q.lat11) for L,q in ok.iterrows()]).set_index('L')
        prof_all[(r,g,v,crit)]=(prof,G)
        b=G.loc[best]; bq=prof.loc[best]
        rows.append(dict(run=r,configuration=EV.loc[r,'configuration'],one_engine_phase=('as flown' if g is None else f'{g//60} min'),
            treatment=('Holland transient bias added' if v=='holland' else 'as observed'),
            delay_prior=('not used' if crit=='noLag' else 'gamma(8, 14.875 s) used'),
            chi2_min=round(m,1), chi2_bfo=round(bq.chi_bfo,1), chi2_bto=round(bq.chi_bto,1),
            fit_quality=('acceptable' if m<=11.1 else ('marginal' if m<=30 else 'poor')),
            delay_best_s=int(best), delay_lo_s=int(ok.index.min()), delay_hi_s=int(ok.index.max()),
            first_flameout_utc_best=b.first_fo.strftime('%H:%M:%S'),
            impact_utc_best=b.impact.strftime('%H:%M:%S'), impact_utc_lo=G.impact.min().strftime('%H:%M:%S'), impact_utc_hi=G.impact.max().strftime('%H:%M:%S'),
            impact_s_after_001937_best=round(b.t_imp_after_0019_37), 
            along_nm_best=round(b.along_nm,1), along_nm_lo=round(G.along_nm.min(),1), along_nm_hi=round(G.along_nm.max(),1),
            cross_nm_best=round(b.cross_nm,1), cross_nm_lo=round(G.cross_nm.min(),1), cross_nm_hi=round(G.cross_nm.max(),1),
            dist_nm_best=round(b.dist_nm,1),
            lat_001937_best=round(b.lat37,2), lon_001937_best=round(b.lon37,2), lat_impact_best=round(b.lat_imp,2), lon_impact_best=round(b.lon_imp,2),
            track_0011_best_deg=round(b.trk0011), rotation_best_deg=bq.rot, holland_bias_001929_hz=round(bq.D29,1),
            bfo_res_0011=round(bq.e11,1), bfo_res_001929=round(bq.e29,1), bfo_res_001937=round(bq.e37,1),
            descent_001929_fpm=round(bq.vu29), descent_001937_fpm=round(bq.vu37), n_alignments_dchi2_le4=len(ok)))
T=pd.DataFrame(rows)
pd.set_option('display.width',250)
print(T[T.delay_prior=='not used'][['run','one_engine_phase','treatment','chi2_min','fit_quality','delay_best_s','delay_lo_s','delay_hi_s','first_flameout_utc_best','impact_utc_best','impact_utc_lo','impact_utc_hi','along_nm_best','cross_nm_best','lat_001937_best']].to_string(index=False))


# ---- cell bcb25f93-a047-494e-9e22-a9b915819222 ----
LMAX=int(np.floor(D.DT11))  # 510 s
rows=[]; prof_all={}
for (r,g,v),(s,P,df) in FITS.items():
    k=df[df.keep&(df.L<=LMAX)].copy()
    for crit in ('noLag','tot'):
        idx=k.groupby('L')[crit].idxmin(); prof=k.loc[idx].set_index('L')
        m=prof[crit].min(); ok=prof[prof[crit]<=m+4]; best=prof[crit].idxmin()
        G=pd.DataFrame([geom(r,g,s,P,L,q.rot,q.lat11)|dict(L=L,chi2=q[crit],rot=q.rot,D29=q.D29,lat11=q.lat11) for L,q in ok.iterrows()]).set_index('L')
        prof_all[(r,g,v,crit)]=(prof,G)
        b=G.loc[best]; bq=prof.loc[best]
        rows.append(dict(run=r,configuration=EV.loc[r,'configuration'],one_engine_phase=('as flown' if g is None else f'{g//60} min'),
            treatment=('Holland transient bias added' if v=='holland' else 'as observed'),
            delay_prior=('not used' if crit=='noLag' else 'gamma(8, 14.875 s) used'),
            chi2_min=round(m,1), chi2_bfo=round(bq.chi_bfo,1), chi2_bto=round(bq.chi_bto,1), chi2_delay_prior=round(bq.lag_pen,1),
            fit_quality=('acceptable' if m<=11.1 else ('marginal' if m<=30 else 'poor')),
            delay_best_s=int(best), delay_lo_s=int(ok.index.min()), delay_hi_s=int(ok.index.max()),
            power_loss_utc_best=(D.T0-dt.timedelta(seconds=float(best))).strftime('%H:%M:%S'),
            first_flameout_utc_best=b.first_fo.strftime('%H:%M:%S'),
            impact_utc_best=b.impact.strftime('%H:%M:%S'), impact_utc_lo=G.impact.min().strftime('%H:%M:%S'), impact_utc_hi=G.impact.max().strftime('%H:%M:%S'),
            impact_s_after_001937_best=round(b.t_imp_after_0019_37),
            along_nm_best=round(b.along_nm,1), along_nm_lo=round(G.along_nm.min(),1), along_nm_hi=round(G.along_nm.max(),1),
            cross_nm_best=round(b.cross_nm,1), cross_nm_lo=round(G.cross_nm.min(),1), cross_nm_hi=round(G.cross_nm.max(),1),
            dist_nm_best=round(b.dist_nm,1),
            lat_001937_best=round(b.lat37,2), lon_001937_best=round(b.lon37,2), lat_impact_best=round(b.lat_imp,2), lon_impact_best=round(b.lon_imp,2),
            track_0011_best_deg=round(b.trk0011), rotation_best_deg=bq.rot, holland_bias_001929_hz=round(bq.D29,1),
            bfo_res_0011=round(bq.e11,1), bfo_res_001929=round(bq.e29,1), bfo_res_001937=round(bq.e37,1),
            descent_001929_fpm=round(bq.vu29), descent_001937_fpm=round(bq.vu37), n_alignments_dchi2_le4=len(ok)))
T=pd.DataFrame(rows)
cols=['run','one_engine_phase','treatment','delay_prior','chi2_min','fit_quality','delay_best_s','delay_lo_s','delay_hi_s','impact_utc_best','impact_utc_lo','impact_utc_hi','along_nm_best','along_nm_lo','along_nm_hi','cross_nm_best','cross_nm_lo','cross_nm_hi','lat_001937_best']
print(T[cols].to_string(index=False))


# ---- cell dbfec660-64ba-410f-9a0b-ed7d0e16546e ----
R=RAW[3]; tu=152; L=390; i37=int(round(tu+L+D.DT37)); 
print('run3 t37',R['t'][i37], 'pos37',round(R['e'][i37],2),round(R['n'][i37],2),'end',round(R['e'][-1],2),round(R['n'][-1],2),'h37',R['h'][i37],'gs end kt',round(np.hypot(R['ve'][-10:],R['vn'][-10:]).mean()))
print('run3 horizontal path length 00:19:37->end NM', round(np.sum(np.hypot(np.diff(R['e'][i37:]),np.diff(R['n'][i37:]))),2))
# run 5: impact time vs delay (no data fit), power loss = second flame-out
t5=ES[5]['t_end']+ES[5]['dt_sea']-float(EV.loc[5,'autopilot lost s'])
def imp5(L): return (D.T0-dt.timedelta(seconds=L)+dt.timedelta(seconds=t5)).strftime('%H:%M:%S')
q=D.lag.ppf([0.025,0.5,0.975]); print('t5 after power loss',round(t5,1),'L30',imp5(30),'L510',imp5(510),'delay prior 2.5/50/97.5%',q.round(0),[imp5(x) for x in q])
Lcut=t5-((dt.datetime(2014,3,8,0,29,44)-D.T0).total_seconds()); print('delay needed for run 5 impact <= 00:29:44:',round(Lcut,1), 'P(delay>=that) under prior', D.lag.sf(Lcut))
# alternate runs, same sweep (no data fit) for context
for r in (3,4,6,10):
    tr=ES[r]['t_end']+ES[r]['dt_sea']-float(EV.loc[r,'autopilot lost s'])
    lmax=FITS[(r,None,'holland')][2].L.max()
    print(r,'t_imp after power loss',round(tr,1),'impact at L=30',(D.T0-dt.timedelta(seconds=30)+dt.timedelta(seconds=tr)).strftime('%H:%M:%S'),'at L max',lmax,(D.T0-dt.timedelta(seconds=float(lmax))+dt.timedelta(seconds=tr)).strftime('%H:%M:%S'),
          'prior 95%',[(D.T0-dt.timedelta(seconds=float(x))+dt.timedelta(seconds=tr)).strftime('%H:%M:%S') for x in q[[2,0]]])


# ---- cell 6c841416-4007-4a60-b1a3-17556779ea7a ----
# skill:figure-style kernel.py (auto-injected on skill load)
META_GREY = "#888888"


def apply_figure_style(*, frame="open", font=None, sizes=(8, 7, 6), grid=False):
    """Set matplotlib rcParams for publication-grade output. Call once before plotting.

    This sets mechanics (role-mapped font-size ladder, outward ticks, frameless
    legends, 300-dpi save, Type-42 embedded fonts) — not a house aesthetic.
    Frame, font and the size ladder are parameters.

    frame : 'open' (bottom+left spines, default) | 'boxed' (all four) | 'none'
    font  : sans-serif family name; None = system default sans-serif
    sizes : (base, secondary, tick) — titles/axis-labels, legend/annotation, ticks
    grid  : whether to draw axes.grid (default False)
    """
    import matplotlib as mpl
    if frame not in ("open", "boxed", "none"):
        raise ValueError(f"frame must be 'open'|'boxed'|'none', got {frame!r}")

    try:
        import os, sys, glob, matplotlib.font_manager as fm
        fdir = os.path.join(os.environ.get("CONDA_PREFIX") or sys.prefix, "fonts")
        if os.path.isdir(fdir):
            known = {f.fname for f in fm.fontManager.ttflist}
            for f in glob.glob(os.path.join(fdir, "*.ttf")):
                if f not in known:
                    fm.fontManager.addfont(f)
    except Exception:
        pass
    base, secondary, tick = sizes
    boxed = (frame == "boxed")
    rc = {
        "font.family": "sans-serif",
        "font.size": base,
        "axes.labelsize": base,
        "axes.titlesize": base,
        "legend.fontsize": secondary,
        "xtick.labelsize": tick,
        "ytick.labelsize": tick,
        "axes.linewidth": 0.6,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 3,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.spines.top": boxed, "axes.spines.right": boxed,
        "axes.spines.left": frame != "none", "axes.spines.bottom": frame != "none",
        "axes.grid": bool(grid),
        "legend.frameon": False,
        "figure.dpi": 200,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.labelweight": "normal",
        "lines.linewidth": 1.2,
        "patch.linewidth": 0.6,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    }
    if font:
        rc["font.sans-serif"] = [font, "DejaVu Sans"]
    mpl.rcParams.update(rc)


def set_frame(ax, style="open"):
    """§3: set spine visibility on an existing axes. style ∈ {'open','boxed','none'}."""
    show = {"open": (False, False, True, True),
            "boxed": (True, True, True, True),
            "none": (False, False, False, False)}[style]
    for side, vis in zip(("top", "right", "bottom", "left"), show):
        ax.spines[side].set_visible(vis)
        if vis:
            ax.spines[side].set_linewidth(0.6)
    ax.tick_params(direction="out", length=0 if style == "none" else 3, width=0.6)


def panel_letter(ax, letter, dx=-0.18, dy=1.02, case="lower", fontsize=None):
    """§5.7: bold panel letter outside top-left of axes. case ∈ {'lower','upper'}."""
    import matplotlib.pyplot as plt
    if fontsize is None:
        fontsize = plt.rcParams.get("font.size", 8) + 1
    s = letter.lower() if case == "lower" else letter.upper()
    ax.text(dx, dy, s, transform=ax.transAxes,
            fontweight="bold", fontsize=fontsize, va="bottom", ha="left")


def focal_palette(labels, focal, focal_color, other="muted", base_colors=None):
    """§4.2: map labels → colors with the focal series visually dominant.

    other='muted'   — desaturate base_colors (or a default cycle) toward gray
    other='grey'    — uniform light gray for all non-focal
    other='ordinal' — non-focal on a single light→dark gray ramp (input order)
    """
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    focal_set = {focal} if isinstance(focal, str) else set(focal)
    n = len(labels)
    if not focal_set & set(labels):
        raise ValueError(f"focal {focal!r} not found in labels")
    if base_colors is None:
        base_colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["#444444"])
    base_colors = [base_colors[i % len(base_colors)] for i in range(n)]
    if other == "grey":
        rest = ["#BCBCBC"] * n
    elif other == "ordinal":
        nf = max(1, n - len(focal_set))
        ramp = [mcolors.to_hex((v, v, v)) for v in
                ([0.55] if nf == 1 else [0.80 - 0.35 * i / (nf - 1) for i in range(nf)])]
        rest, k = [], 0
        for l in labels:
            rest.append(ramp[min(k, nf - 1)]); k += (l not in focal_set)
    else:
        def mute(c):
            r, g, b = mcolors.to_rgb(c)
            m = (r + g + b) / 3
            return mcolors.to_hex((0.3 * r + 0.7 * m, 0.3 * g + 0.7 * m, 0.3 * b + 0.7 * m))
        rest = [mute(c) for c in base_colors]
    return [focal_color if l in focal_set else rest[i] for i, l in enumerate(labels)]


def bar_with_points(ax, x, ymat, labels, colors, jitter=0.08, show_points=True,
                    errorbar=None, point_alpha=0.5, point_size=8):
    """§6.1: bar = mean; optionally overlay raw points or draw an interval.

    colors   : per-label color list (e.g. from focal_palette)
    errorbar : None | 'sd' | 'ci95' — drawn only when show_points is False.
               'ci95' is the t-distribution 95% CI of the mean
               (half-width t_{0.975,n-1} · s/√n); correct at small n where the
               z-approximation (1.96·s/√n) is markedly too narrow.
    """
    import numpy as np
    means = np.array([np.mean(y) for y in ymat], float)
    err = None
    if errorbar and not show_points:
        if errorbar == "sd":
            err = np.array([np.std(y, ddof=1) if np.asarray(y).size > 1 else 0 for y in ymat])
        elif errorbar == "ci95":
            from scipy.stats import t
            def _hw(y):
                n = np.asarray(y).size
                return t.ppf(0.975, n - 1) * np.std(y, ddof=1) / np.sqrt(n) if n > 1 else 0
            err = np.array([_hw(y) for y in ymat])
    ax.bar(x, means, color=colors, width=0.7, edgecolor="none",
           yerr=err, error_kw={"elinewidth": 0.8, "capsize": 0})
    if show_points:
        for xi, ys in zip(x, ymat):
            ys = np.asarray(ys)
            if ys.ndim and ys.size > 1:
                jit = (np.random.rand(ys.size) - 0.5) * 2 * jitter
                ax.scatter(np.full(ys.size, xi) + jit, ys, s=point_size, color="black",
                           alpha=point_alpha, zorder=3, linewidths=0)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    return ax


def strip_with_median(ax, groups, values, colors=None, jitter=0.12):
    """§6.1: jittered points + bold horizontal median tick per group."""
    import numpy as np
    labs = list(groups)
    if colors is None:
        colors = ["#444444"] * len(labs)
    for i, (ys, c) in enumerate(zip(values, colors)):
        ys = np.asarray(ys)
        jit = (np.random.rand(ys.size) - 0.5) * 2 * jitter
        ax.scatter(np.full(ys.size, i) + jit, ys, s=10, color=c, alpha=0.6, linewidths=0, zorder=2)
        m = np.median(ys)
        ax.plot([i - 0.22, i + 0.22], [m, m], color="black", lw=1.6, zorder=3)
    ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs)
    return ax


def goodness_arrow(ax, text="higher = better", loc="upper left", axis="y", fontsize=None):
    """§3.6: small upright direction-of-goodness cue in the margin."""
    import matplotlib.pyplot as plt
    if fontsize is None:
        fontsize = plt.rcParams["legend.fontsize"]
    pos = {"upper left": (0.02, 0.98), "upper right": (0.98, 0.98),
           "lower left": (0.02, 0.02), "lower right": (0.98, 0.02)}[loc]
    ha = "left" if "left" in loc else "right"
    va = "top" if "upper" in loc else "bottom"
    arrow = "↑ " if axis == "y" else "→ "
    ax.text(pos[0], pos[1], arrow + text, transform=ax.transAxes,
            fontsize=fontsize, color=META_GREY, ha=ha, va=va)


def two_tier_label(name, meta):
    """§5: two-line label string (name / metadata). Meta line styled separately by caller."""
    return f"{name}\n{meta}"


def end_of_line_labels(ax, xs, ys, labels, colors=None, dx=0.01, fontsize=None):
    """§6.3 / §7.3: label each line series at its right end instead of a legend box."""
    import matplotlib.pyplot as plt
    if fontsize is None:
        fontsize = plt.rcParams["font.size"]
    if colors is None:
        colors = [None] * len(labels)
    span = ax.get_xlim()[1] - ax.get_xlim()[0]
    for x, y, lab, c in zip(xs, ys, labels, colors):
        ax.text(x[-1] + dx * span, y[-1], lab, color=c, va="center", ha="left", fontsize=fontsize)


def panel_crops(fig, dpi=None, pad_px=6, bbox_inches=None, pad_inches=None):
    """§9.2: pixel-space crop boxes for each lettered panel in the SAVED PNG.

    Returns ``{letter: (x0, y0, x1, y1)}`` in image-space pixels (origin
    top-left, matching ``host.view_image(path, crop=...)`` and PIL's
    ``Image.crop``). Panels are detected as bold single-character ``Text``
    objects placed by :func:`panel_letter`; each panel's crop is its axes'
    tightbbox mapped into the saved file's pixel space, padded by ``pad_px``.
    For §3.4 composites (abutting subplots sharing an axis, letter on the
    leftmost only) the crop unions in letterless ``sharex``/``sharey`` siblings
    on the same grid row/col so the whole composite is covered. When no axes
    carries a panel letter (standalone plot, or a figure-composer sub-agent),
    falls back to one crop per axes keyed by index.

    ``bbox_inches`` mirrors ``Figure.savefig`` semantics: ``None`` means
    *consult rcParams* (so under :func:`apply_figure_style` it resolves to
    ``'tight'``); pass an explicit ``Bbox`` only if you saved with one. The
    boxes are clamped to the saved image extent regardless.

        >>> fig.savefig("fig.png")            # bbox_inches='tight' via rcParams
        >>> for letter, box in panel_crops(fig).items():
        ...     host.view_image("fig.png", crop=box)
    """
    import matplotlib as mpl
    import matplotlib.text
    if dpi is None:
        dpi = mpl.rcParams.get("savefig.dpi", fig.dpi)
        if dpi == "figure":
            dpi = fig.dpi
    dpi = float(dpi)
    if bbox_inches is None:
        bbox_inches = mpl.rcParams.get("savefig.bbox")
    fig.canvas.draw()
    r = fig.canvas.get_renderer()

    if bbox_inches == "tight":
        if pad_inches is None:
            pad_inches = mpl.rcParams.get("savefig.pad_inches", 0.1)
        tb = fig.get_tightbbox(r).padded(pad_inches)
        ox_in, oy_in = tb.x0, tb.y0
        W_in, H_in = tb.width, tb.height
    elif isinstance(bbox_inches, mpl.transforms.BboxBase):
        ox_in, oy_in = bbox_inches.x0, bbox_inches.y0
        W_in, H_in = bbox_inches.width, bbox_inches.height
    else:
        ox_in, oy_in = 0.0, 0.0
        W_in, H_in = fig.get_size_inches()
    W_px, H_px = int(round(W_in * dpi)), int(round(H_in * dpi))
    lettered = {}
    for ax in fig.axes:
        for t in ax.findobj(matplotlib.text.Text):
            s = (t.get_text() or "").strip()
            if len(s) == 1 and s.isalpha() and t.get_fontweight() in ("bold", 700):
                lettered[ax] = s
                break



    if not lettered:
        lettered = {ax: str(i) for i, ax in enumerate(fig.axes)}
    out = {}
    for ax, letter in lettered.items():
        bbs = [ax.get_tightbbox(r)]




        ss = ax.get_subplotspec()
        for sib in fig.axes:
            if sib is ax or sib in lettered:
                continue
            ssib = sib.get_subplotspec()
            same_row = ss is None or ssib is None or ss.rowspan == ssib.rowspan
            same_col = ss is None or ssib is None or ss.colspan == ssib.colspan
            if ((ax.get_shared_y_axes().joined(ax, sib) and same_row)
                    or (ax.get_shared_x_axes().joined(ax, sib) and same_col)):
                bbs.append(sib.get_tightbbox(r))
        bb = mpl.transforms.Bbox.union(bbs)

        bx0 = (bb.x0 / fig.dpi - ox_in) * dpi
        bx1 = (bb.x1 / fig.dpi - ox_in) * dpi
        by0 = H_px - (bb.y1 / fig.dpi - oy_in) * dpi
        by1 = H_px - (bb.y0 / fig.dpi - oy_in) * dpi
        out[letter] = (
            max(int(bx0) - pad_px, 0),
            max(int(by0) - pad_px, 0),
            min(int(bx1) + pad_px, W_px),
            min(int(by1) + pad_px, H_px),
        )
    return out


# ---- cell b703f0d0-4114-400b-96b2-39694d757dac ----
NORM={}
for r in (1,2,5,7,8,9):
    Rr=D.run_raw(f"Case {r:02d}.csv"); k=slice(-10,None); vz=Rr['vu'][k].mean()*0.3048/60; dts=Rr['h'][-1]*0.3048/max(-vz,5.08)
    tr=Rr['t'][-1]+dts-float(EV.loc[r,'autopilot lost s'])
    NORM[r]=dict(t_after=round(tr,1), at_L510=(D.T0-dt.timedelta(seconds=510)+dt.timedelta(seconds=tr)).strftime('%H:%M:%S'),
                 prior95=[(D.T0-dt.timedelta(seconds=float(x))+dt.timedelta(seconds=tr)).strftime('%H:%M:%S') for x in q[[2,0]]])
print(NORM)


# ---- cell f5f2c3ed-b939-4dd0-92af-27b670085024 ----
import os, matplotlib as mpl, matplotlib.pyplot as plt, textwrap
OUT='reverse-dive-window-2026-11-04'; os.makedirs(OUT,exist_ok=True)
T['fit_note']=np.where(T.run==5,'normal configuration: no fit to the 00:19 data (latitude at grid limit); sensitivity only',
              np.where(T.fit_quality=='poor','poor fit','') )
order={3:0,4:1,6:2,10:3,5:4}
T=T.sort_values(['delay_prior','one_engine_phase','run','treatment'],key=lambda c: c.map(order) if c.name=='run' else c).reset_index(drop=True)
T.to_csv(f'{OUT}/dive-impact-time-fits.csv',index=False)
# no-fit delay sweep table
sw=[]
for r in (3,4,6,10,1,2,5,7,8,9):
    Rr=RAW.get(r) or D.run_raw(f"Case {r:02d}.csv"); k=slice(-10,None); vz=Rr['vu'][k].mean()*0.3048/60; dts=Rr['h'][-1]*0.3048/max(-vz,5.08)
    tr=Rr['t'][-1]+dts-float(EV.loc[r,'autopilot lost s'])
    lmax=min(LMAX, int(tr-D.DT37-8))  # aircraft must be airborne at 00:19:37
    f=lambda L:(D.T0-dt.timedelta(seconds=float(L))+dt.timedelta(seconds=tr)).strftime('%H:%M:%S')
    sw.append(dict(run=r,configuration=EV.loc[r,'configuration'],impact_s_after_power_loss=round(tr,1),
        impact_utc_delay_30s=f(30),impact_utc_delay_max=f(lmax),delay_max_s=lmax,
        impact_utc_delay_model_2p5pct=f(q[0]),impact_utc_delay_model_median=f(q[1]),impact_utc_delay_model_97p5pct=f(q[2])))
SW=pd.DataFrame(sw); SW.to_csv(f'{OUT}/dive-impact-time-vs-delay-no-fit.csv',index=False); print(SW.to_string(index=False))


# ---- cell 357bdf22-1e3b-42eb-b8e3-33821f7503e6 ----
SW=SW.rename(columns={'impact_utc_delay_model_2p5pct':f'impact_utc_delay_{q[0]:.0f}s_2p5pct','impact_utc_delay_model_median':f'impact_utc_delay_{q[1]:.0f}s_median','impact_utc_delay_model_97p5pct':f'impact_utc_delay_{q[2]:.0f}s_97p5pct'})
SW.to_csv(f'{OUT}/dive-impact-time-vs-delay-no-fit.csv',index=False)
apply_figure_style(sizes=(8,7,6))
base=dt.datetime(2014,3,8,0,0,0)
def mins(x): 
    if isinstance(x,str): h,m,s_=map(int,x.split(':')); x=base+dt.timedelta(hours=h if h<12 else h-24,minutes=m,seconds=s_)
    return (x-base).total_seconds()/60
W0,W1=mins('00:19:38'),mins('00:29:44')
P0=T[(T.delay_prior=='not used')&(T.one_engine_phase=='as flown')]
colors={'Holland transient bias added':'#1f6fb4','as observed':'#e08214'}
fig,ax=plt.subplots(figsize=(7.2,5.6))
ax.axvspan(W0,W1,color='0.90',zorder=0)
ax.text((W0+W1)/2,-0.75,'Ruled source-time window, 00:19:38 to 00:29:44',ha='center',va='center',fontsize=7)
for tl,lab in ((mins('00:19:29'),'00:19:29 log-on request'),(mins('00:19:37'),'00:19:37 log-on acknowledge')):
    ax.axvline(tl,color='0.35',lw=0.7,ls='--',zorder=1)
ax.text(mins('00:19:29')-0.1,9.85,'00:19:29 and 00:19:37\nsatellite log-on',ha='right',va='center',fontsize=6,color='0.3')
yt=[];yl=[];y=0
for r in (3,4,6,10,5):
    swr=SW.set_index('run').loc[r]
    lo,hi=mins(swr[f'impact_utc_delay_{q[2]:.0f}s_97p5pct']),mins(swr[f'impact_utc_delay_{q[0]:.0f}s_2p5pct'])
    ax.plot([lo,hi],[y+0.5,y+0.5],color='0.55',lw=1.0,solid_capstyle='butt',zorder=2)
    ax.plot([lo,hi],[y+0.5,y+0.5],'|',color='0.55',ms=5,zorder=2)
    for j,(tr,c) in enumerate(colors.items()):
        row=P0[(P0.run==r)&(P0.treatment==tr)].iloc[0]; yy=y+j
        b,l,h=mins(row.impact_utc_best),mins(row.impact_utc_lo),mins(row.impact_utc_hi)
        good=row.chi2_min<=30
        ax.plot([l,h],[yy,yy],color=c,lw=4,solid_capstyle='butt',zorder=3)
        ax.plot(b,yy,'o',ms=5,mfc=(c if good else 'white'),mec=c,mew=1.2,zorder=4)
        ax.text(max(h,b)+0.12,yy,f"{row.impact_utc_best}   misfit {row.chi2_min:.0f}",va='center',fontsize=6,color='0.15')
    yt.append(y+0.5); yl.append(f"Run {r}\n({'normal' if r==5 else 'alternate'} electrical\nconfiguration)")
    y+=2.4
ax.set_yticks(yt); ax.set_yticklabels(yl); ax.invert_yaxis()
ax.set_ylim(y-0.4,-1.2)
xt=np.arange(19,37,1); ax.set_xticks(xt); ax.set_xticklabels([f"00:{int(x):02d}" for x in xt],rotation=90)
ax.set_xlim(18.6,36.4)
ax.set_xlabel('Time the aircraft reaches the sea, UTC, 8 March 2014')
ax.set_title('Dives that fit the 00:19 satellite data reach the sea at 00:19:58 to 00:22:18,\ninside the ruled source-time window',loc='left')
from matplotlib.lines import Line2D
hand=[Line2D([],[],color=colors['Holland transient bias added'],lw=4,marker='o',mfc=colors['Holland transient bias added'],label='Both 00:19 frequencies with Holland transient bias added'),
      Line2D([],[],color=colors['as observed'],lw=4,marker='o',mfc=colors['as observed'],label='Both 00:19 frequencies as observed'),
      Line2D([],[],color='0.4',lw=0,marker='o',mfc='white',label='Open marker: misfit above 30 (poor fit)'),
      Line2D([],[],color='0.55',lw=1,marker='|',label='No fit: log-on delay 51 to 215 s (95 % range of delay model)')]
ax.legend(handles=hand,loc='lower right',fontsize=6,frameon=False)
foot=("Notes. Source: Boeing 2016 engineering-simulator runs (traces released 19 Aug 2018), 1 s position and altitude, no pilot input after fuel exhaustion. "
"Main electrical power is lost at the first engine stop (alternate configuration) or the second engine stop (normal configuration, run 5). "
"Each run is placed with its 00:10:59 point on the 00:10:59 timing arc (41 to 19.5 S, 0.1 degree steps), its track turned -30 to +30 degrees, "
"and its power loss set 30 to 510 s before 00:19:29.4 (1 s steps; the satellite unit answered at 00:10:59, so power was on then). "
"Misfit = chi-squared on the burst timing offsets at 00:19:29 (sigma 63 us) and 00:19:37 (43 us) and the burst frequency offsets at 00:10:59, 00:19:29 and 00:19:37 (sigma 7 Hz), "
"with the frequency bias fitted under a 150 +/- 5 Hz prior. Holland transient bias: fitted 17 to 136 Hz at 00:19:29, 0 to 6 Hz less at 00:19:37 (Holland 2017, arXiv:1702.02432). "
"Bars: all delays within a misfit of 4 of the best (log-on delay model not applied); dot: best fit. "
"Alignments with the first engine stop before 00:10:59 are kept only if the descent rate then is 800 ft/min or less. "
"Sea contact = end of record (473 to 1,131 ft) plus the remaining height at the final 10 s descent rate. Simulator wind is kept. "
"Late-dive speeds near Mach 1.0 are outside Boeing's simulator data. Run 5 has no fit (misfit 296 to 332, latitude at the grid limit) and is a sensitivity only. "
"Grey bars: impact time for a log-on delay from the gamma(8, 14.875 s) delay model, without the satellite data. "
"Normal runs 1, 2, 7, 8 and 9 reach the sea at 00:33:26 or later for every allowed delay (off this chart).")
fig.text(0.01,0.005,textwrap.fill(foot,175),fontsize=5.2,va='bottom',ha='left',color='0.25')
fig.subplots_adjust(left=0.16,right=0.98,top=0.90,bottom=0.33)
fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.png',dpi=300); fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.pdf')
r_=fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print(ov); fb=fig.bbox; print([t.get_text()[:30] for t,bb in texts if bb.x1>fb.x1+1 or bb.x0<-1 or bb.y0<-1 or bb.y1>fb.y1+1])


# ---- cell d62d64c9-5f2c-487a-971a-d026ec3b3d0d ----
leg=ax.get_legend(); leg.remove()
ax.legend(handles=hand,loc='upper right',bbox_to_anchor=(1.0,0.80),fontsize=6,frameon=False)
for t in ax.texts:
    if t.get_text().startswith('00:19:29 and'): t.set_position((mins('00:19:29')-0.1,-0.75)); t.set_va('center')
fig.subplots_adjust(left=0.16,right=0.98,top=0.90,bottom=0.36)
fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.png',dpi=300); fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.pdf')
texts=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print(ov)


# ---- cell 78873cfd-8317-4790-8c26-e3780fe36224 ----
for t in ax.texts:
    if t.get_text().startswith('00:19:29 and'): t.set_position((mins('00:19:29')-0.12,-0.75)); t.set_ha('right'); t.set_multialignment('right')
fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.png',dpi=300); fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.pdf')
bb=[t for t in ax.texts if t.get_text().startswith('00:19:29 and')][0].get_window_extent(r_); print(bb.x1, ax.transData.transform((mins('00:19:29'),0))[0])


# ---- cell 50cf6fbe-d961-44de-a77e-63d41f94c3af ----
for ln in ax.lines:
    xd=ln.get_xdata()
    if ln.get_linestyle()=='--' and len(xd)==2 and xd[0]==xd[1]: ln.set_ydata([0,0.93])
fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.png',dpi=300); fig.savefig(f'{OUT}/dive-impact-time-vs-ruled-window.pdf')


# ---- cell 92dcff0e-d2cb-4d4d-9253-42477021543f ----
P0=T[(T.delay_prior=='not used')&(T.one_engine_phase=='as flown')]
def span(df): 
    lo=min(df.impact_utc_lo); hi=max(df.impact_utc_hi); return lo,hi
alt=P0[P0.configuration=='alternate']
K={}
K['alternate_all_fits']=span(alt)
K['alternate_misfit_le30']=span(alt[alt.chi2_min<=30])
K['alternate_misfit_le11']=span(alt[alt.chi2_min<=11.1])
K['run5_no_fit_best']=span(P0[P0.run==5])
K['all_as_flown_incl_run5']=span(P0)
Pw=T[T.delay_prior!='not used']; K['alternate_with_delay_model']=span(Pw[(Pw.configuration=='alternate')&(Pw.one_engine_phase=='as flown')])
K['run5_variants_all']=span(T[T.run==5])
def sec(a,b): 
    f=lambda x: sum(int(v)*m for v,m in zip(x.split(':'),(3600,60,1)))
    return f(b)-f(a)
K['margin_early_s']=sec('00:19:38',K['alternate_all_fits'][0]); K['margin_late_alt_s']=sec(K['alternate_all_fits'][1],'00:29:44'); K['margin_late_run5_s']=sec(K['all_as_flown_incl_run5'][1],'00:29:44')
alt_sw=SW[SW.configuration=='alternate']; nor_sw=SW[SW.configuration=='normal']
K['alt_delay_model_only']=(min(alt_sw.iloc[:,-1]),max(alt_sw.iloc[:,-3]))
K['normal_any_delay']=(min(nor_sw.impact_utc_delay_max),max(nor_sw.impact_utc_delay_30s))
for k,v in K.items(): print(k,v)
print(P0[['run','treatment','chi2_min','delay_best_s','delay_lo_s','delay_hi_s','first_flameout_utc_best','impact_utc_best','impact_utc_lo','impact_utc_hi','impact_s_after_001937_best','along_nm_best','along_nm_lo','along_nm_hi','cross_nm_best','cross_nm_lo','cross_nm_hi','dist_nm_best','lat_001937_best','lon_001937_best','lat_impact_best','lon_impact_best','track_0011_best_deg','holland_bias_001929_hz','descent_001929_fpm','descent_001937_fpm']].to_string(index=False))


# ---- cell 369e01c4-2f6b-4c0d-bd5b-193c337efecb ----
md=f"""# Boeing dive fits to the 00:19 satellite data: impact times and outer bound

Date: 4 November 2026. Branch claude-science-sep29, folder results/hydroacoustics/reverse-dive-window-2026-11-04/.
Purpose: give the hydroacoustic reverse search an impact (source) time window, conditional on the Boeing dive cases.

## Result

1. The four alternate-configuration Boeing dives (runs 3, 4, 6, 10) reach the sea at **00:19:58 to 00:22:18 UTC**. This span covers both treatments of the 00:19 frequencies and every alignment within a misfit of 4 of each run's best.
2. The ruled source-time window, 00:19:38 to 00:29:44, contains all these fits. The margin is **20 s** at the early end and **7 min 26 s** at the late end.
3. Only run 3 fits well (misfit 4.0 with Holland transient bias added, 5.9 as observed). Its impact is 00:19:58 to 00:20:05. Run 3 needs a power loss 390 to 397 s before 00:19:29, which is in the far tail of the log-on delay model (95 % range 51 to 215 s).
4. Runs 4 and 10 fit marginally with Holland transient bias added (misfit 21 and 27) and poorly as observed (32 and 35). Their impacts are 00:21:57 to 00:22:18, at a delay of 157 to 167 s.
5. Run 6 fits poorly under both treatments (misfit 93 and 116). Its impacts are 00:20:08 to 00:21:06.
6. Adding the log-on delay model to the misfit does not move any best delay or impact-time range (table rows marked 'gamma(8, 14.875 s) used').
7. Run 5 (normal configuration, sensitivity) has no fit: misfit 296 to 356 under every treatment and every one-engine phase of 4 to 14 min, with the 00:19:37 point at the 19.5 S grid limit. Its 'best' impact, 00:29:12 to 00:29:15, is 29 s inside the window end. This number comes from a non-fit and has no weight.

## Impact time and offset per run and treatment (log-on delay model not used)

Offsets are from the 00:19:37 position to the sea contact. Along-track is positive in the direction of the 00:10:59 track. Cross-track is positive to the right of that track.

| Run | 00:19 frequencies | Misfit | Delay to 00:19:29, s (best; range) | Impact UTC (best; range) | Along-track NM (best; range) | Cross-track NM (best; range) | 00:19:37 latitude |
|---|---|---|---|---|---|---|---|
"""
for _,r in P0.iterrows():
    md+=f"| {r.run} | {r.treatment} | {r.chi2_min:.1f} | {r.delay_best_s}; {r.delay_lo_s}-{r.delay_hi_s} | {r.impact_utc_best}; {r.impact_utc_lo}-{r.impact_utc_hi} | {r.along_nm_best}; {r.along_nm_lo} to {r.along_nm_hi} | {r.cross_nm_best}; {r.cross_nm_lo} to {r.cross_nm_hi} | {abs(r.lat_001937_best):.2f} S |\n"
md+=f"""
The full table, with residuals, descent rates, Holland transient bias values, positions and the delay-model rows, is dive-impact-time-fits.csv. The impact time for any delay without the satellite data is in dive-impact-time-vs-delay-no-fit.csv.

## Outer bound as a sensitivity against the ruled window (00:19:38 to 00:29:44)

| Case | Impact span UTC | Inside ruled window? |
|---|---|---|
| Alternate runs, all fits (misfit within 4 of best) | {K['alternate_all_fits'][0]} to {K['alternate_all_fits'][1]} | Yes; margins 20 s early, 446 s late |
| Alternate runs, misfit 30 or less | {K['alternate_misfit_le30'][0]} to {K['alternate_misfit_le30'][1]} | Yes |
| Alternate runs, misfit 11.1 or less (run 3 only) | {K['alternate_misfit_le11'][0]} to {K['alternate_misfit_le11'][1]} | Yes |
| Run 5 (normal), no fit | {K['run5_no_fit_best'][0]} to {K['run5_no_fit_best'][1]} | Yes, by 29 s |
| Alternate runs, delay model only (no satellite data), 95 % | {K['alt_delay_model_only'][0]} to {K['alt_delay_model_only'][1]} | Yes |
| Normal runs 1, 2, 5, 7, 8, 9, any delay 30-510 s (no satellite data) | {K['normal_any_delay'][0]} to {K['normal_any_delay'][1]} | Mostly no |

Judgement: the ruled window contains every dive that fits the 00:19 frequencies, under both treatments. The early margin (20 s) is small but physical: the aircraft must still transmit at 00:19:37, and the earliest fitted contact is 21 s after that. The late end has wide spare margin for the alternate configuration. The window would not contain normal-configuration glides if the 00:19 frequencies were held out: those reach the sea at 00:28:00 to 00:43:07. So the window is conditional on the 00:19 frequencies (either treatment), which exclude the normal configuration.

## Method (reused, not rebuilt)

1. Code: the 2 Nov 2026 configuration-fit functions, copied verbatim (dive_fit_lib.py). Parity check: the earlier best misfits (run 3: 5.9 / 4.6; run 4: 34.3 / 20.8; run 6: 131.1 / 93.2; run 10: 34.8 / 26.6) reproduce exactly on the earlier grid.
2. Each Boeing trace (1 s X, Y, altitude) is placed with its 00:10:59 point on the 00:10:59 timing arc, then turned through -30 to +30 degrees of track. Main power is lost at the first engine stop (alternate) or the second (normal). The power loss is set 30 to 510 s before 00:19:29.4 in 1 s steps.
3. Changes from 2 Nov: the 00:10:59 latitude grid is widened from 30-40 S to 19.5-41 S, and the delay grid from 40-400 s (2 s steps) to 30-510 s (1 s steps). 510 s is a hard limit: the satellite unit answered at 00:10:59, so main power was on then.
4. Misfit = chi-squared on the burst timing offsets at 00:19:29 (sigma 63 us) and 00:19:37 (43 us, empirical offset applied) and the burst frequency offsets at 00:10:59, 00:19:29 and 00:19:37 (sigma 7 Hz). The frequency bias is fitted under a 150 +/- 5 Hz prior.
5. Treatment (a), Holland transient bias added: a transient bias is fitted within Holland's 17 to 136 Hz at 00:19:29 and is 0 to 6 Hz smaller at 00:19:37 (Holland 2017, arXiv:1702.02432). Treatment (b): both frequencies as observed.
6. Pete's 18 Oct rule: an alignment that puts the first engine stop before 00:10:59 is kept only if the descent rate at 00:10:59 is 800 ft/min or less. For the alternate runs no fitted alignment puts the first engine stop before 00:10:59. For run 5 the rule removes 11,036 of 27,001 alignment cells on the widened grid.
7. Sea contact = end of record (473 to 1,131 ft) plus the remaining height at the mean descent rate of the last 10 s (at least 1,000 ft/min). The horizontal offset continues at the last 10 s ground velocity. Simulator wind is kept as flown.
8. Ranges: all delays with a profile misfit within 4 of the run's best. At each delay, the best latitude and track turn are used.

## Checks and caveats

1. Track-turn limit. Runs 4 and 10 reach the -30 degree limit (00:10:59 track 149 degrees). A test with -60 to +60 degrees lowers their misfit by at most 1.5 and moves their delay ranges by no more than 3 s. So impact times do not change by more than about 3 s.
2. Run 6 as observed and run 5 put the 00:19:37 point at the 19.5 to 20.0 S grid limit, north of the ruled 20-41 S arc span. Both are poor fits.
3. Run 3 reaches the sea only 27-28 s after 00:19:37, at 0.3 NM from the 00:19:37 point (0.52 NM of path in a steep spiral from 15,668 ft).
4. Dive speeds near Mach 1.0 are outside Boeing's simulator data. The late-dive timing is therefore indicative.
5. The fits use the six data items only. The misfit levels (dof about 2) say that only run 3 matches both 00:19 frequencies well. Runs 4 and 10 need Holland transient bias added to approach an acceptable fit.
6. The 'misfit' bound of 11.1 (about 95 % for 5 items) is the reference used on 2 Nov. It is a rough guide only.
"""
open(f'{OUT}/README.md','w').write(md)
# verify count claimed for run-5 rule removal
s5,P5,df5=FITS[(5,None,'holland')]; print(len(df5), (~df5.keep).sum(), (df5[df5.L<=LMAX].shape[0]), (~df5[df5.L<=LMAX].keep).sum())
for r in (3,4,6,10):
    df=FITS[(r,None,'holland')][2]; print(r, df.fo_before_0011.sum())


# ---- cell c30bf020-4502-4db9-ae6b-3c657cb3075b ----
md=md.replace("For run 5 the rule removes 11,036 of 27,001 alignment cells on the widened grid.","For run 5 (as flown, delay 30-510 s) the rule removes 682 of 14,911 alignment cells (delay x track turn).")
open(f'{OUT}/README.md','w').write(md); print('682 of 14,911' in md)


# ---- cell e17406bb-57ae-4bc3-96cc-88b25f2f1057 ----
r=host.query("SELECT id, created_at, length(source) FROM execution_log WHERE frame_id='17dd7473-1479-424f-9a5d-490f260d7d6b' AND language='python' AND exit_status='ok' ORDER BY created_at")
rows=r['rows']; print(len(rows))
keep=[]
for cid,ts,L in rows:
    parts=[]
    for off in range(1,L+1,800):
        parts.append(host.query(f"SELECT substr(source,{off},800) FROM execution_log WHERE id='{cid}'")['rows'][0][0])
    src=''.join(parts); keep.append((cid,src))
sel=[s for c,s in keep if any(k in s for k in ['dive_fit_lib','D.LATS=','def end_state','LMAX=','SW=pd.DataFrame','apply_figure_style(sizes','leg=ax.get_legend','set_multialignment','ln.get_linestyle','K={}','md=f','md=md.replace','ROTW={}','NORM={}'])]
print(len(sel))
import json; json.dump(sel,open('handoff/cells.json','w')) if __import__('os').path.isdir('handoff') else (__import__('os').makedirs('handoff'),json.dump(sel,open('handoff/cells.json','w')))


# ---- cell a023df9f-7b60-48fb-835c-c302031050c8 ----
try:
    hist=list(In)
except NameError:
    hist=None
print(type(hist), len(hist) if hist else None)


# ---- cell d887f44d-5cbc-44c2-9228-ccec5fab13ed ----
r=host.query("SELECT exit_status, language, count(*) FROM execution_log WHERE frame_id='17dd7473-1479-424f-9a5d-490f260d7d6b' GROUP BY 1,2")
print(r['rows'])


# ---- cell 610f2718-b639-4700-aff6-20f84c2857d8 ----
r=host.query("SELECT frame_id, count(*), min(created_at) FROM execution_log WHERE source LIKE '%dive_fit_lib%' OR source LIKE '%def end_state%' GROUP BY 1")
print(r['rows'])

