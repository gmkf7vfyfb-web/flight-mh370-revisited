s=open('figs.py').read()
s=s.replace("fig.legend(handles=hh,loc='upper left',ncol=2,frameon=False,bbox_to_anchor=(0.08,0.12),fontsize=6)\n    fig.suptitle(title,x=0.08,ha='left',fontsize=8,y=0.95)\n    fig.text(0.08,-0.06,\"\\n\".join(textwrap.wrap(n1b,170)),fontsize=6,va='top'); fig.text(0.08,-0.15,",
            "fig.legend(handles=hh,loc='upper left',ncol=2,frameon=False,bbox_to_anchor=(0.08,0.05),fontsize=6)\n    fig.suptitle(title,x=0.08,ha='left',fontsize=8,y=0.95)\n    fig.text(0.08,-0.13,\"\\n\".join(textwrap.wrap(n1b,170)),fontsize=6,va='top'); fig.text(0.08,-0.235,")
s=s.replace("fig.text(0.08,-0.135,\"\\n\".join(textwrap.wrap(n2,170))","fig.text(0.08,-0.145,\"\\n\".join(textwrap.wrap(n2,170))")
open('figs.py','w').write(s); exec(s)
fig_backward(OD, lons, lats, 'Objects 70-110 km from the Haixun 01 contact on 5 April started away from the bearing-arc crossing on 8 March (provisional grid)', n1b, n2b)
fig_forward(exec_title)
