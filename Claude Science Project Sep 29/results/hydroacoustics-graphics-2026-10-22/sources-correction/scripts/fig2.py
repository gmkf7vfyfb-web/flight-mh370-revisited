exec(open('fig_common.py').read())
R=pd.read_csv(S1B+'charge_h10n_residuals.csv'); S=json.load(open(S1B+'stage1b_summary.json'))
K=pd.read_csv(S1B+'event_tl_kraken.csv'); RM=pd.read_csv(S1B+'event_tl_ram.csv')
fig, axs = plt.subplots(1,3, figsize=(7.2,3.9)); fig.subplots_adjust(left=0.08,right=0.99,top=0.84,bottom=0.47,wspace=0.42)
ax=axs[0]; z=33.0
r=R[(R.src_depth_m==z)]
o=r[r.model=='RAM']; ax.plot(o.fc_hz,o.obs_esd_db,'o-',color='k',ms=3,lw=1,label='observed (Nielsen et al. 2021)')
for mname,col,lab in (('KRAKEN',C_K,'predicted, normal modes'),('RAM',C_V,'predicted, parabolic equation')):
    q=r[r.model==mname]; ax.plot(q.fc_hz,q.model_esd_db,'s--',color=col,ms=3,lw=1,label=lab)
ax.fill_between(o.fc_hz,o.obs_esd_db-3,o.obs_esd_db+3,color='0.85',lw=0,label='observed, signal 5 to 20 s')
ax.set_xscale('log'); ax.set_xticks([5,10,20,40]); ax.set_xticklabels(['5','10','20','40']); ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Energy density (dB re 1 µPa² s/Hz)')
ax.set_title('Charge: model is 14 dB too loud', loc='left'); ax.legend(frameon=False,fontsize=5.6,loc='upper left',bbox_to_anchor=(0,-0.2)); panel_letter(ax,'a')
ax=axs[1]
for mname,col,mk in (('KRAKEN',C_K,'s'),('RAM',C_V,'o')):
    for zz,ls in ((33.0,'-'),(47.0,':')):
        q=R[(R.model==mname)&(R.src_depth_m==zz)]
        if len(q): ax.plot(q.fc_hz,q.residual_db,ls,marker=mk,color=col,ms=3,lw=1,label=f"{'normal modes' if mname=='KRAKEN' else 'parabolic equation'}, {zz:g} m")
ax.axhspan(-4,4,color='0.9',lw=0); ax.axhline(0,color='0.4',lw=0.6)
ax.set_xscale('log'); ax.set_xticks([5,10,20,40]); ax.set_xticklabels(['5','10','20','40']); ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter()); ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Observed minus predicted (dB)')
s=S['charge']['RAM|z33|T10']
ax.set_title('Residual: level fails, shape passes', loc='left')
ax.text(0.02,0.96,f"level {s['stats']['level_median']:+.1f} dB; slope {s['stats']['slope_db_per_oct']:+.1f} dB/octave;\nshape {s['stats']['shape_rms']:.1f} dB r.m.s.", transform=ax.transAxes, fontsize=5.6, va='top')
ax.legend(frameon=False,fontsize=5.6,loc='upper left',bbox_to_anchor=(0,-0.2)); panel_letter(ax,'b')
ax=axs[2]
for pth,col,zk,zr,lab in (('af447-H10S',C_M,10.0,10.0,'aircraft path, 2,210 km, 10 m'),('sanjuan-charge-H10N',C_N,33.0,33.0,'charge path, 5,989 km, 33 m')):
    a=K[(K.path==pth)&np.isclose(K.src_depth_m,zk)]; b=RM[(RM.path==pth)&np.isclose(RM.src_depth_m,zr)].sort_values('fc_hz')
    ax.plot(a.fc_hz,a.tl_db,'s--',color=col,ms=3,lw=1,label=lab+', normal modes'); ax.plot(b.fc_hz,b.tl_db,'o-',color=col,ms=3,lw=1,label=lab+', parabolic eq.')
ax.set_xscale('log'); ax.set_xticks([5,10,20,40]); ax.set_xticklabels(['5','10','20','40']); ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter()); ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Transmission loss (dB re 1 m)')
ax.invert_yaxis(); ax.set_title('Models agree on the charge path only', loc='left'); ax.legend(frameon=False,fontsize=5.6,loc='upper left',bbox_to_anchor=(0,-0.2)); panel_letter(ax,'c')
fig.suptitle('Known South Atlantic sources: the propagation shape is right, the predicted charge level is too high', x=0.01, ha='left', fontsize=8)
af=S['af447']
foot(fig, "We predicted the sound of the 2017 calibration charge at Ascension Island with our two sound models and compared it with the published spectrum. The shape across frequency agrees to about 1 dB, but the predicted level is 11 to 17 dB higher than the measured level. The two models agree with each other on this path, so the difference comes from the charge source estimate or from the published spectrum units, not from the path. We cannot test the aircraft case: the published window does not contain the expected arrival time.",
     f"Pre-registered stage 1b (module 5230679; criteria.md C1 with C4 level thresholds 4/7 dB). Source: Gaspin & Shuler (1971) construction (audit gs_reconstruct, kappa 4, sin^2), 108 kg TNT = 238 lb, outside G&S's stated range (few lb); depths 33 m (primary), 38, 47 m. Observed: Nielsen et al. (2021) Fig. 5c H10N PSD (digitised), noise removed in power, + 10 log10(10 s) (Vergoz p. 2529); grey band = 5-20 s. Verdict, parabolic equation (pyram, hard bottom + Francois-Garrison) at 33 m: LEVEL {s['stats']['level_median']:+.1f} dB FAIL, SLOPE {s['stats']['slope_db_per_oct']:+.2f} +/- {s['stats']['slope_se']:.2f} dB/oct PARTIAL, SHAPE {s['stats']['shape_rms']:.2f} dB PASS -> FAIL; normal modes (KRAKEN adiabatic, hard bottom): {S['charge']['KRAKEN|z33|T10']['stats']['level_median']:+.1f} / {S['charge']['KRAKEN|z33|T10']['stats']['slope_db_per_oct']:+.2f} / {S['charge']['KRAKEN|z33|T10']['stats']['shape_rms']:.2f} -> FAIL. Peak check (descriptive, impact-template peak ratio 3.013/s): model 135.3 dB vs printed 130 dB re 1 uPa. AF447 same-figure ratio upper bound +{af['RAM|total']['min']:.1f} to +{af['RAM|total']['max']:.1f} dB (parabolic eq., total KE) is NOT APPLICABLE: Kadri's window starts 101 s after the predicted arrival. On the aircraft path the two models differ by up to 10 dB above 25 Hz. Paths: ocean transport paths-calibration (dafb0d1). PREDICTIVE, NOT CALIBRATED; caveats C1, C2.")
fig.savefig(OUT+'/hydroacoustics-calibration-events-known-sources.png', dpi=300); fig.savefig(OUT+'/hydroacoustics-calibration-events-known-sources.pdf'); check(fig)
