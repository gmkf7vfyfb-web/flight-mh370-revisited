globals().update(GL)
import copy
CANDS_bak=copy.deepcopy(CANDS['A'])
CANDS['A'].update(lat=float(fla[i_b]),lon=float(flo[i_b]),t0=float(t0b-nT0),title='Kadri 00:49:58 (bearing 260.41 deg) + Portland 3274 01:15:51')
exec(src2d); fnA=chart2('A'); plt.close('all'); print(fnA, round(CANDS['A']['lat'],3),round(CANDS['A']['lon'],3),fmt(CANDS['A']['t0']))
host.view_image(fnA)