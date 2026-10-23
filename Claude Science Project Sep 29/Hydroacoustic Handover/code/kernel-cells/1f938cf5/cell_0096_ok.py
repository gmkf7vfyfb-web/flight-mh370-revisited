
rt=mabs.loc[[s for s in mabs.index if s.startswith('run-j/')]]
lr=np.log(rt.ratio_rec_to_impact); lf=np.log(rt.ratio_fus_to_impact)
rng_rec=f"{lr.min():+.2f} to {lr.max():+.2f}"; rng_fus=f"{lf.min():+.2f} to {lf.max():+.2f}"
print(rt[['ratio_rec_to_impact','ratio_fus_to_impact']].round(3), rng_rec, rng_fus)
old="route strata; ln ratio 0.0 to +0.1. Treated as 1."
assert old in md
md=md.replace(old,f"route strata; ln ratio {rng_rec} (detached), {rng_fus} (retained), i.e. within Monte Carlo noise of 0. Treated as 1.")
open('out/README.md','w').write(md)
dst='repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/settling'
shutil.copy('out/README.md',dst)
json.dump(dict(rng_rec=rng_rec,rng_fus=rng_fus),open('out/_lr.json','w'))
