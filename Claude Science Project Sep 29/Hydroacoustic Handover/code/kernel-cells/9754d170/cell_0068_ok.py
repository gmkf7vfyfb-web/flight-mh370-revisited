
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
z=np.load('audit/work/sus/sus_spectra.npz'); f=z['f']
keys=sorted({k.rsplit('|',1)[0] for k in z.files if k!='f'})
print(len(keys), keys[:8])
evs=['A6sus2','A6sus3','A7sus2','A7sus3','A8sus2','A9sus3','A10sus3','A11sus']
fig,axs=plt.subplots(len(evs),3,figsize=(10,2*len(evs)),sharex=True)
for i,e in enumerate(evs):
    for j,st in enumerate(['H01W','H08S','H08N']):
        ax=axs[i,j]
        for c in ['red','blue']:
            k=f'{e}|{st}|{c}'
            if k in z.files: ax.plot(f,z[k],color=c,lw=0.7)
        ax.set_title(f'{e} {st}',fontsize=7); ax.tick_params(labelsize=6)
fig.tight_layout(); fig.savefig('audit/work/sus/qc_traces.png',dpi=80)
