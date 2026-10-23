import matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style(sizes=(8,7,6))
OUTD="out"
FOOT_ENV=("(i) Plain: We use average sea data for March. The sea floor is 4,577 m deep at the position where the ship heard the signal. "
          "No flight data is used.\n"
          "(ii) Technical: WOA23 1-deg decav, March monthly 0-1,500 m + Jan-Mar seasonal below, mean of 25.5/26.5 S cells at 101.5 E; "
          "Mackenzie (1981) sound speed; Francois-Garrison (1982) absorption at 37.5 kHz, pH 8.0; GEBCO 2020 depth at 25.975 S 101.461 E. "
          "Prior-free; no 00:19 option; physics provisional.")
prof=np.genfromtxt(f"{OUTD}/profile.csv",delimiter=",",names=True)
fig,axs=plt.subplots(1,3,figsize=(7.2,3.6),sharey=True,gridspec_kw={"wspace":0.08})
for ax,key,lab,col in zip(axs,["T_C","c_mps","alpha37p5_dBkm"],["Temperature (°C)","Sound speed (m/s)","Absorption at 37.5 kHz (dB/km)"],["0.2"]*3):
    ax.plot(prof[key],prof["depth_m"],color="k",lw=1.2)
    ax.axhline(Z_BED,color="0.4",ls="--",lw=0.8); ax.set_xlabel(lab); ax.margins(x=0.06)
axs[0].set_ylim(Z_BED+150,0); axs[0].set_ylabel("Depth (m)")
axs[0].text(axs[0].get_xlim()[0]+0.5,Z_BED-80,"sea floor 4,577 m",fontsize=7,color="0.3",va="bottom")
axs[1].annotate(f"minimum {cg.min():.0f} m/s\nat {zg[np.argmin(cg)]:.0f} m",xy=(cg.min(),zg[np.argmin(cg)]),xytext=(1505,2200),fontsize=7,arrowprops=dict(arrowstyle="-",color="0.4",lw=0.6))
axs[2].text(0.97,0.03,f"{Ax[0]:.0f} dB lost to absorption\non the vertical path",transform=axs[2].transAxes,ha="right",va="bottom",fontsize=7)
for a,l in zip(axs,"abc"): panel_letter(a,l)
fig.suptitle("Water column under the first contact: absorption, not refraction, limits the signal",x=0.06,ha="left",fontsize=8)
fig.text(0.01,-0.02,FOOT_ENV,fontsize=6,va="top",wrap=True)
fig.subplots_adjust(top=0.88,bottom=0.17,left=0.09,right=0.98)
fig.savefig(f"{OUTD}/haixun-water-column.png",dpi=300,bbox_inches="tight")
plt.close(fig)

FOOT_P=("(i) Plain: The lines show how likely the boat team was to hear a working flight-recorder beacon on the sea floor, for each horizontal distance "
        "from the beacon. The three lines use three different ways to set the receiver performance. The bands show the spread from the unknown values.\n"
        "(ii) Technical: Dukane DK100 source 160.5 dB re 1 uPa at 1 m new, 157.0 dB at 30 d, linear (day 27.3 = 157.3 dB) with unit spread -3/+2 dB; ray-traced direct path "
        "(WOA23 March, GEBCO 2020 4,577 m, receiver 2 m); ERA5 10-m wind 3.6 m/s; APL-UW wind noise; P = P(transmitting 0.7-0.9) x Phi(SE/sigma), sigma 2-5 dB; "
        "losses for pointing, beam pattern and shielding included; 200k Monte Carlo draws. Prior-free; physics provisional; no recordings exist.")
cols={"A":"k","B":"0.45","C":"0.7"}; ls={"A":"-","B":"--","C":":"}
P=np.genfromtxt(f"{OUTD}/pdet_vs_offset.csv",delimiter=",",names=True)
fig,axs=plt.subplots(1,2,figsize=(7.2,3.4),gridspec_kw={"wspace":0.3})
lab={"A":"first-principles sonar equation","B":"maker's practical range (2.0-3.6 km)","C":"ATSB favourable range (4.0-5.0 km)"}
for c in "ABC":
    axs[0].fill_between(P["offset_m"]/1000,P[f"{c}_SE05"],P[f"{c}_SE95"],color=cols[c],alpha=0.15,lw=0)
    axs[0].plot(P["offset_m"]/1000,P[f"{c}_SE50"],color=cols[c],ls=ls[c],lw=1.3,label=lab[c])
    axs[1].plot(P["offset_m"]/1000,P[f"{c}_Pmean"],color=cols[c],ls=ls[c],lw=1.3)
axs[0].axhline(0,color="0.3",lw=0.6); axs[0].text(9.9,0.8,"detection threshold",ha="right",fontsize=7,color="0.3")
axs[0].set_xlabel("Horizontal offset from beacon (km)"); axs[0].set_ylabel("Signal excess (dB), median and 5-95 %")
axs[0].legend(frameon=False,loc="lower left",fontsize=7)
axs[1].set_xlabel("Horizontal offset from beacon (km)"); axs[1].set_ylabel("Probability of detection (mean)")
axs[1].set_yscale("log"); axs[1].set_ylim(1e-6,1)
for x_,t_ in [(2,"second contact\n2 km"),(3,"3 km")]:
    axs[1].axvline(x_,color="0.6",lw=0.6,ls="-."); 
axs[1].text(2.05,2e-6,"second contact 2-3 km",fontsize=7,color="0.4")
axs[1].text(0.2,0.25,f"directly above:\nA {P['A_Pmean'][0]:.3f}, C {P['C_Pmean'][0]:.4f},\nB {P['B_Pmean'][0]:.1e}",fontsize=7,va="top")
for a,l in zip(axs,"ab"): panel_letter(a,l); a.set_xlim(0,10); a.margins(y=0.04)
fig.suptitle("A beacon 4.6 km below a hand-held receiver is at or below the detection threshold even directly overhead",x=0.06,ha="left",fontsize=8)
fig.text(0.01,-0.02,FOOT_P,fontsize=6,va="top",wrap=True)
fig.subplots_adjust(top=0.88,bottom=0.16,left=0.09,right=0.98)
fig.savefig(f"{OUTD}/haixun-detection-vs-offset.png",dpi=300,bbox_inches="tight")
plt.close(fig)
print(P["A_Pmean"][0],P["B_Pmean"][0],P["C_Pmean"][0], P["A_SE50"][0],P["A_SE95"][0])