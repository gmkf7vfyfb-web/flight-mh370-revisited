
import glob
rows=[]
for fpath in glob.glob('audit/work/sens/out/*/*/power_check.json'):
    opt,var=fpath.split('/')[-3:-1]; d=json.load(open(fpath))
    for sc,rec in d['synthetic'].items():
        for h in ['H','noH']:
            r=rec[h]['reweighted']; rows.append(dict(option=opt,variant=var,scenario=sc,truth=h,E_lnR=r['mean'],mc_se=r['mc_se_mean'],P_abs_ge1=r['p_abs_ge_1'],P_abs_ge0p5=r['p_abs_ge_0p5'],p_any_signal=r['mean_p_any_signal']))
    for s_ in ['H01W','3376','3274']:
        rows.append(dict(option=opt,variant=var,scenario='meanPD',truth=s_,E_lnR=d['windows'][s_]['reweighted']['mean_pd_flight']))
for opt in ['held-out','r600-bto-only','r600-bto-raw-bfo']:
    d=json.load(open(f"audit/repo/Claude Science Project Sep 29/results/hydroacoustics-pleiades-test-standin/power/{opt}/power_check.json"))
    for sc,rec in d['synthetic'].items():
        for h in ['H','noH']:
            r=rec[h]['reweighted']; rows.append(dict(option=opt,variant='standin_N2000',scenario=sc,truth=h,E_lnR=r['mean'],mc_se=r['mc_se_mean'],P_abs_ge1=r['p_abs_ge_1'],P_abs_ge0p5=r['p_abs_ge_0p5'],p_any_signal=r['mean_p_any_signal']))
    for s_ in ['H01W','3376','3274']:
        rows.append(dict(option=opt,variant='standin_N2000',scenario='meanPD',truth=s_,E_lnR=d['windows'][s_]['reweighted']['mean_pd_flight']))
PCdf=pd.DataFrame(rows); PCdf.to_csv(AUD+'data/sensitivity_power_check.csv',index=False)
t=PCdf[(PCdf.scenario.isin(['A','C']))].pivot_table(index=['option','variant'],columns=['scenario','truth'],values=['E_lnR','P_abs_ge1']).round(3)
print(t.to_string())
print(PCdf[PCdf.scenario=='meanPD'].pivot_table(index=['option','variant'],columns='truth',values='E_lnR').round(3).to_string())
