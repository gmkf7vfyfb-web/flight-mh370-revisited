trk5=track(-25.732,101.369,alpha=0.005)
for c_ in list(a1.collections):
    if isinstance(c_,mpl.collections.PathCollection): c_.remove()
la,lo=trk5['2014-04-13']; a1.scatter(lo,la,s=3,c='#ff9f1c',zorder=4,label='debris from the crossing, position on 13 Apr')
a1.legend(loc='upper left',frameon=True,framealpha=0.85,edgecolor='none',fontsize=7)
a1.set_title('An impact near the crossing leaves a low chance that no debris was seen',loc='left')
a2.set_title('The exposure fell on 28-30 Mar (fair) and 21-26 Apr (poor weather)',loc='left')
fig.savefig('fig2-surface-search-locality.png',dpi=200); fig.savefig('fig2-surface-search-locality.pdf')
for k in ['2014-03-28','2014-04-13','2014-04-22']:
    la,lo=trk5[k]; print(k,'median %.2f %.2f'%(np.median(la),np.median(lo)))
print('L_surf csiro 0.5%% at crossing cell %.3f, Haixun cell %.3f'%(Lgrid[(REF_A,'csiro')][int(np.floor((-25.732-GLAT0)/GST))*GNX+int(np.floor((101.369-GLON0)/GST))],Lgrid[(REF_A,'csiro')][hcell]))