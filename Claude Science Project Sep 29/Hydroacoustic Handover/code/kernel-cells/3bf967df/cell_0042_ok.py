import json, numpy as np, pandas as pd
R=json.load(open('handoff_kadri_results.json'))
by={r['name']:r for r in R.values()}
# Terms at D0 (00:19 data held out), bearing sd 1.0 deg for flight; values copied from structured outputs (verified below by string search)
terms={
 'Arrival time and bearing at Cape Leeuwin vs chance transient (rate background)':(-5.59,-5.58,'Flight','UNCONVERGED, cond. ESS 166 (T) / 14 (C)'),
 'Debris drift: recovered items only':(0.83,0.81,'Drift','±0.35; not specific to the bearing'),
 'Debris drift: populated Australian coast non-recovery (current setting)':(2.86-0.83,2.82-0.81,'Drift','post hoc; alertness open: total +1.28/+1.88/+2.28 at 1x/3x/5x'),
 'Seabed search (OI 2018 inferred, rho 0.05)':(0.74,0.87,'Search coverage','OI grade C; impact point, not seabed'),
 '2014 aircraft/ship surface search':(-0.66,-0.56,'Search coverage','own drift, CSIRO POD'),
 'Perth Canyon amplitude given Cape Leeuwin level':(np.log(0.012),np.log(0.10),'Hydro signals','PROVISIONAL: borrowed TL, digitised amplitude, test added after pre-registration'),
 'H08S non-detection given Cape Leeuwin level':(np.log(0.54),np.log(0.63),'Hydro signals','caveats C1, C2'),
}
src=json.dumps(R)
for k,(t,c,leg,_) in terms.items(): pass
for s in ['-5.59','-5.58','+0.83','+0.81','+2.86','+2.82','+0.74','+0.87','-0.66','-0.56','0.012','0.10','0.53-0.55','0.62-0.64']:
    assert s in src, s
df=pd.DataFrame([(k,leg,t,c,cav) for k,(t,c,leg,cav) in terms.items()],columns=['term','leg','ln_T','ln_C','caveat'])
groups={'A  acoustic timing + bearing only':[0],
        'B  A + drift (finds) + searches':[0,1,3,4],
        'C  B + Australian non-recovery':[0,1,2,3,4],
        'D  C + hydro amplitude and H08S (provisional)':[0,1,2,3,4,5,6]}
rows=[(g,df.ln_T.iloc[i].sum(),df.ln_C.iloc[i].sum()) for g,i in groups.items()]
comb=pd.DataFrame(rows,columns=['combination','ln_B_T','ln_B_C'])
comb['ln_B_T_one_arrival_bg']=comb.ln_B_T+2.89; comb['ln_B_C_one_arrival_bg']=comb.ln_B_C+2.89
pd.set_option('display.width',200); print(df.round(2).to_string(index=False)); print(comb.round(2).to_string(index=False))
df.to_csv('kadri-composed-terms.csv',index=False); comb.to_csv('kadri-composed-combinations.csv',index=False)