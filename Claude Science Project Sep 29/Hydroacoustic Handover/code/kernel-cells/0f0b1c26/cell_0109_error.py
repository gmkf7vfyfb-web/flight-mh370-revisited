
import os, json, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt, textwrap
os.chdir('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/0f0b1c26-b241-4b3b-9f87-53c4386c8175')
apply_figure_style(sizes=(8,7,6))
H='hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/'
WR=H+'results-data/digitised/waveform-rasters/'
OUT='figs'; os.makedirs(OUT,exist_ok=True)
def foot(fig, ste, tech, y0=0.01, width=175):
    t1="\n".join(textwrap.wrap("Simplified English: "+ste, width)); t2="\n".join(textwrap.wrap("Technical: "+tech, width))
    fig.text(0.01, y0, t1+"\n\n"+t2, fontsize=6, va='bottom', ha='left', color='0.25')
def env(df):
    u=df.upper.values; l=df.lower.values; return u,l
def utcsec(df, ref):
    return (pd.to_datetime(df.utc)-pd.Timestamp(ref)).dt.total_seconds().values

C_K='#1f4e9c'; C_V='#c8641e'; C_N='#4d8f3a'; C_M='#7a3d9c'
fig, axs = plt.subplots(2,2, figsize=(7.2,6.4)); fig.subplots_adjust(left=0.09,right=0.98,top=0.93,bottom=0.30,hspace=0.55,wspace=0.28)
# a: H10N charge
ref='2017-12-01T21:11:00Z'
ax=axs[0,0]
k=pd.read_csv(WR+'kadri2024_fig8_grenade_H10N_DIGITISED.csv'); v=pd.read_csv(WR+'vergoz2021_fig2_charge_H10N_DIGITISED.csv'); n=pd.read_csv(WR+'nielsen2021_fig3_charge_H10N_node2_DIGITISED.csv')
pk=10**(130/20)/1e6
ax.fill_between(utcsec(k,ref), k.lower, k.upper, color=C_K, lw=0, alpha=0.85, label='Kadri (2024) Fig. 8, pressure axis')
ax.fill_between(utcsec(v,ref), v.lower*pk+8, v.upper*pk+8, color=C_V, lw=0, alpha=0.85, label='Vergoz et al. (2021) Fig. 2, scaled to their printed peak')
ax.fill_between(utcsec(n,ref), n.lower*pk+16, n.upper*pk+16, color=C_N, lw=0, alpha=0.85, label='Nielsen et al. (2021) Fig. 3, scaled to the same peak')
ax.set_xlim(30,130); ax.set_yticks([-4,0,4]); ax.set_ylabel('Pressure (Pa); upper traces offset')
ax.set_xlabel('Seconds after 21:11:00 UTC, 1 Dec 2017')
ax.set_title('Charge at Ascension North: the three papers agree within 3 s', loc='left')
ax.axvline(64, color='0.5', lw=0.6, ls=':')
ax.legend(loc='upper left', frameon=False, fontsize=6, bbox_to_anchor=(0,-0.28), ncol=1)
panel_letter(ax,'a')
# b: H04S charge
ref2='2017-12-01T21:32:00Z'; ax=axs[0,1]
k=pd.read_csv(WR+'kadri2024_fig8_grenade_H04S_DIGITISED.csv'); v=pd.read_csv(WR+'vergoz2021_fig2_charge_H04S_DIGITISED.csv'); n=pd.read_csv(WR+'nielsen2021_fig3_charge_H04S_node2_DIGITISED.csv')
pk2=10**(122/20)/1e6
ax.fill_between(utcsec(k,ref2), k.lower, k.upper, color=C_K, lw=0, alpha=0.85)
ax.fill_between(utcsec(v,ref2), v.lower*pk2+3, v.upper*pk2+3, color=C_V, lw=0, alpha=0.85)
ax.fill_between(utcsec(n,ref2), n.lower*pk2+6, n.upper*pk2+6, color=C_N, lw=0, alpha=0.85)
ax.set_xlim(0,150); ax.set_yticks([-1,0,1]); ax.set_xlabel('Seconds after 21:32:00 UTC, 1 Dec 2017')
ax.set_title('Charge at Crozet: weak, dispersed, same timing', loc='left'); panel_letter(ax,'b')
# c: CMST fig 1 vs IMOS 3315
ax=axs[1,0]
c=pd.read_csv(WR+'cmst2014_fig1_perth_canyon_DIGITISED.csv'); m=pd.read_csv(WR+'cmst_fig1_overlay/imos3315_531A728A_1-120Hz_column_envelope.csv')
ax.fill_between(c.t_s, c.lower, c.upper, color='0.55', lw=0, label='CMST report 2014-30 Fig. 1 (digitised)')
ax.plot(m.t_s, m.upper_pa, color=C_M, lw=0.6, label='Our read of the same recording (1-120 Hz)'); ax.plot(m.t_s, m.lower_pa, color=C_M, lw=0.6)
ax.set_xlim(100,275); ax.set_ylim(-2,2); ax.set_ylabel('Pressure (Pa)'); ax.set_xlabel('Seconds after 01:30:00 UTC, 8 Mar 2014')
ax.set_title('Perth Canyon logger: our calibration matches the report', loc='left')
ax.legend(loc='upper left', frameon=False, fontsize=6, bbox_to_anchor=(0,-0.28)); panel_letter(ax,'c')
ov=json.load(open(WR+'cmst_fig1_overlay/cmst_fig1_vs_imos3315.json'))
ax.text(0.98,0.04,f"peak {ov['1-120Hz']['peak_ratio_db_measured_minus_cmst']:+.1f} dB, {ov['1-120Hz']['dt_peak_s_measured_minus_cmst']:+.1f} s", transform=ax.transAxes, ha='right', fontsize=6)
# d: CMST fig 2 band level
ax=axs[1,1]
cols=['#1f4e9c','#c8641e','#4d8f3a']
for i in (1,2,3):
    d=pd.read_csv(WR+f'cmst2014_fig2_ha01_h{i}_band_DIGITISED.csv'); s=pd.Series(d.band_5_40Hz_db_re_panel_max).rolling(5,center=True).mean()
    ax.plot(d.t_s, s, color=cols[i-1], lw=0.8, label=f'hydrophone {i}')
ax.axvline(290, color='0.5', lw=0.6, ls=':'); ax.set_xlim(100,350)
ax.set_ylabel('5-40 Hz level (dB re panel maximum)'); ax.set_xlabel('Seconds after 01:30:00 UTC, 8 Mar 2014')
ax.set_title('Cape Leeuwin: peak at 01:34:50 on all three sensors', loc='left'); ax.legend(frameon=False, fontsize=6, loc='lower left'); panel_letter(ax,'d')
fig.suptitle('Published hydrophone records re-read from the figures: times and levels agree across sources', x=0.01, ha='left', fontsize=8)
foot(fig, "We read the traces from the published figures. In (a) and (b) the same explosion is shown by three papers; the times agree to 3 s and the peak in Kadri's figure agrees with the level that Vergoz printed to within 1 dB. In (c) we compare a published trace with our own processing of the same recording; the peak agrees to 0.7 dB and 2.4 s. These are digitised published data, not new measurements.",
     "(a,b) ARA San Juan calibration charge, 1 Dec 2017 (108 kg TNT, Vergoz et al. 2021 p. 2528). Kadri 2024 Fig. 8 (PMC raster 749 px, pressure axis; peak 3.44 Pa = 130.7 dB re 1 uPa at H10N, 1.06 Pa = 120.5 dB at H04S) vs Vergoz printed peaks 130 / 122 dB re 1 uPa; Vergoz Fig. 2 and Nielsen Fig. 3 have no pressure scale and are drawn normalised x printed peak, offset. Peak times H10N 21:12:06 / 21:12:04 / 21:12:03-06 UTC. (c) CMST 2014-30 Fig. 1 vs IMOS 3315 file 531A728A.DAT (role B), Curtin gain file + -197.8 dB sensitivity, logger clock -25.82 s (pre-registered clock test), 4th-order zero-phase Butterworth 1-120 Hz, column envelope on CMST's 0.69 s pixel grid; 5-40 Hz: -2.0 dB. (d) CMST Fig. 2 jet colour scale inverted to dB (-40..0 re panel max), 5-40 Hz mean, 5-column running mean; CMST text 01:34:50 +/- 3 s. Script prepare/digitise_waveform_rasters.py, cmst_fig1_imos_overlay.py (module 5230679). DIGITISED; nothing here is a likelihood.")
fig.savefig(OUT+'/hydroacoustics-published-waveforms-retraced.png', dpi=300); fig.savefig(OUT+'/hydroacoustics-published-waveforms-retraced.pdf')
r=fig.canvas.get_renderer(); texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov_=[(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print(ov_[:10])
