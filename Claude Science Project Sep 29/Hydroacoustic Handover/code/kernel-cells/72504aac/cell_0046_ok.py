
exec(open('work/common.py').read())
apply_figure_style(sizes=(8,7,6))
for k,v in LOCI.items(): print(k, round(v['lat'],2), round(v['lon'],2), v['txt'])
print(G_AZ_H01W, G_D_H01W, G_AZ_H08S, G_D_H08S)
for b in [57.0, 306.18, 274.84, G_AZ_H01W]: print(b, ray_arc_cross('H01W', b))
