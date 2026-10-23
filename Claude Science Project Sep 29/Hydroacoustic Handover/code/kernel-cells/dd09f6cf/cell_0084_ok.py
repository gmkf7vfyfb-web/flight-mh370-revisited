for t in list(axs[0].texts):
    if t.get_text().startswith('above 0'): t.remove()
axs[0].text(-0.3,2.15,'above 0 = favours the locality',ha='left',fontsize=7)
axs[1].set_title('Surface search: argues against the crossing',loc='left')
for t in list(fig.texts):
    if t.get_text().startswith(('Plain','Technical')): t.remove()
fig.text(0.05,0.155,'\n'.join(textwrap.wrap(f1,185)),fontsize=7,va='top'); fig.text(0.05,0.08,'\n'.join(textwrap.wrap(f2,195)),fontsize=6.5,va='top',color='#444')
fig.set_size_inches(10.5,5.9); fig.subplots_adjust(bottom=0.42)
fig.legends[0].set_bbox_to_anchor((0.52,0.255))
fig.savefig('fig3-search-likelihood-terms.png',dpi=200); fig.savefig('fig3-search-likelihood-terms.pdf'); print('ok')