s=open('figs.py').read()
s=s.replace("ax.set_title('Debris evidence favours the bearing locality over the run J posterior',loc='left')","ax.set_title('Near the bearing, debris evidence is above the run J average',loc='left')")
s=s.replace("ax.set_title('The ratio is stable across the 00:19 options',loc='left')","ax.set_title('Stable across 00:19 options',loc='left')")
s=s.replace("""            if o=='populated':
                for xi,(yi,ei) in zip(x,zip(r.LLR,r.ESS)): ax.text(xi,yi+2*r.sd_total.max()+0.12,f'{ei:.0f}',ha='center',fontsize=5.5,color='#444444')""",
"""            if o=='none':
                for xi,ei in zip(x,r.ESS): ax.text(xi,-0.45,f'{ei:.0f}',ha='center',fontsize=5.5,color='#444444')""")
s=s.replace("ax.text(0.98,0.02,'numbers: effective sample size (finds + populated)',transform=ax.transAxes,ha='right',fontsize=5.5,color='#444444')",
            "ax.text(0.02,0.075,'effective sample size (diamond, square):',transform=ax.transAxes,ha='left',fontsize=5.5,color='#444444'); ax.set_ylim(-0.6,None)")
s=s.replace("fig.text(0.06,-0.31,\"\\n\".join(textwrap.wrap(N3b,175))","fig.text(0.06,-0.33,\"\\n\".join(textwrap.wrap(N3b,175))")
s=s.replace("ax.margins(y=0.12)","ax.set_ylim(-0.6,4.4)")
open('figs.py','w').write(s); exec(s)
N3b=N3b.replace("Rows outside","Lines in (a): run J median impact longitude per 0.5 deg latitude (arc-latitude first look). Rows outside")
fig_llr(RC,prof,aus,ex)
