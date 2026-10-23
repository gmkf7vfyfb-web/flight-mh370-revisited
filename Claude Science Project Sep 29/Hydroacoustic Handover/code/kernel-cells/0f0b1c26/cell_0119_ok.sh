cat > fig3.py <<'EOF'
exec(open('fig_common.py').read())
T=pd.read_csv(S1B+'kadri_crash_timing_EXPLORATORY.csv')
T['lab']=T.event+' at '+T.receiver+' ('+T.range_km.round(0).astype(int).map('{:,}'.format)+' km)'
T=T.iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(7.2,4.6)); fig.subplots_adjust(left=0.30,right=0.97,top=0.90,bottom=0.36)
y=np.arange(len(T))
ax.axvspan(-60,60,color='0.9',lw=0,label='within 1 minute of the prediction')
for i,r in T.iterrows():
    col = C_K if r.box_source=='digitised' else '0.45'
    ax.plot([0,r.obs_minus_pred_s/60],[i,i],color=col,lw=0.8); ax.plot(r.obs_minus_pred_s/60,i,'o',color=col,ms=4, mfc=col if r.window_contains_prediction else 'white')
ax.axvline(0,color='0.3',lw=0.6); ax.set_yticks(y); ax.set_yticklabels(T.lab)
ax.set_xlabel('Time of the highlighted signal minus the predicted sound-channel arrival (min)')
ax.set_xlim(-13,10); ax.margins(y=0.05)
from matplotlib.lines import Line2D
h=[Line2D([],[],marker='o',color=C_K,ls='',label='box read from the figure'),Line2D([],[],marker='o',color='0.45',ls='',label='window centre (Kadri: signal near the middle)'),
   Line2D([],[],marker='o',color='0.3',mfc='white',ls='',label='published 10-min window does not contain the prediction'),
   mpl.patches.Patch(color='0.9',label='within 1 minute of the prediction')]
ax.legend(handles=h,frameon=False,fontsize=6,loc='upper left',bbox_to_anchor=(-0.38,-0.14),ncol=2)
ax.set_title('Only some of the published crash signals arrive when sound from the crash site can arrive', loc='left')
foot(fig,"For each aircraft crash that Kadri (2024) shows, we calculated when sound from the crash site should reach the hydrophone by the deep sound channel. Then we compared that time with the signal that his figure highlights. The F-35A and Lion Air signals agree to within one minute. The Air France 447 signal is 6.4 minutes late, and the published window starts after the expected arrival, so that panel cannot show the impact. Two Yemenia panels and one Transair panel are also 4 to 9 minutes late, and Sriwijaya is 12 minutes early. Times of some crashes are given only to the nearest minute. This is a check of published figures, not a new detection.",
     "EXPLORATORY (not pre-registered), prepare/kadri_crash_timing.py. Predicted arrival = impact time + WGS84 geodesic range / 1.482 km/s (module SOFAR prior, sd 0.006 km/s -> 6-13 s). Impact times: Kadri 2024 Supplementary S1 ('around', minute precision) except AF447 (BEA 02:14:28 UTC) and F-35A (S1 10:26:30). Positions: S1, except F-35A (module working point from Metz et al. 2023) and Yemenia 626 (ASN site; S1 position is on land). Receivers: IMS triad centroids (FDSN; H10S from the ocean transport path README). Observed: Kadri's highlighted box (digitised from the PMC rasters, +/- 2.4 s) or window start + 5 min (Kadri p. 11) where not digitised. Early arrivals from shallow-water sources (Sriwijaya, Java Sea) may be land-coupled paths; late arrivals cannot be explained by a faster path. AF447: predicted 02:39:19 +/- 6 s; window 02:41-02:51; box 02:44:58-02:46:27. Consequence: the AF447 coupling upper bound (stage 1b) is not applicable. Digitised data; PREDICTIVE, NOT CALIBRATED; caveats C1, C2.")
fig.savefig(OUT+'/hydroacoustics-kadri-crash-panels-timing.png', dpi=300); fig.savefig(OUT+'/hydroacoustics-kadri-crash-panels-timing.pdf'); check(fig)
EOF
echo ok