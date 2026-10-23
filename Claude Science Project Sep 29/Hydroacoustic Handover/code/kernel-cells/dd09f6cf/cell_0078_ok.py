leg[-1]=Line2D([],[],ls='none',marker='o',mfc='none',mec='#a3351f',mew=1.4,label='Haixun 01 contact, 4-5 Apr 2014 (sensitivity only)')
leg[7]=Line2D([],[],c='#1f4e9c',label='bearing 306.18 deg from hydrophone H01W (Cape Leeuwin); dashed = +/-1 deg')
fig.legends.clear()
for t in list(fig.texts):
    if t.get_text().startswith(('Plain','Technical')): t.remove()
fig.set_size_inches(10.5,7.4)
fig.subplots_adjust(left=0.07,right=0.98,top=0.92,bottom=0.36,wspace=0.06)
fig.legend(handles=leg,loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(0.52,0.285),fontsize=7)
fig.text(0.06,0.115,'\n'.join(textwrap.wrap(foot1,180)),fontsize=7,va='top')
fig.text(0.06,0.06,'\n'.join(textwrap.wrap(foot2,190)),fontsize=6.5,va='top',color='#444')
fig.savefig('fig1-seabed-coverage-bearing.png',dpi=200); fig.savefig('fig1-seabed-coverage-bearing.pdf')
r=fig.canvas.get_renderer(); texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]; print(ov[:10])