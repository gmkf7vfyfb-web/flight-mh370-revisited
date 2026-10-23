OUTD='kh/results'; os.makedirs(OUTD,exist_ok=True)
q1=pd.concat([q1m,q1j]); q1.to_csv(f'{OUTD}/q1-locality-mass.csv',index=False)
q2=pd.concat([q2m,q2j]); q2.to_csv(f'{OUTD}/q2-acoustic-bayes-factors.csv',index=False)
CHW.to_csv(f'{OUTD}/q3-conditional-characterisation-weighted.csv',index=False); TOP.to_csv(f'{OUTD}/q3-top1pct-rows-summary.csv',index=False)
feas.to_csv(f'{OUTD}/q3-feasibility-near-crossing.csv',index=False); tq.to_csv(f'{OUTD}/q1-q4-timing-quantiles.csv',index=False)
cc.to_csv(f'{OUTD}/q3-c2-cause-cells.csv',index=False); qs.to_csv(f'{OUTD}/q1-by-route-stratum.csv',index=False)
ch[ch.key.str.contains('joined')].to_csv(f'{OUTD}/q3-joined-v2-characterisation.csv',index=False)
NM={0:'D0 held out',1:'D1 R600 BTO',2:'D2 R600 BTO+BFO',3:'D3 both BFOs raw (Holland H2 data)',4:'D4 both BFOs start-up offset (Holland H1 data)',5:'D5 R600 BFO + R1200 BFO offset'}
def q1md(df,keys,regs):
    L_=['| 00:19 option | region | mass share | Kish ESS | eff. parents | A1/A2/B in region | C1 share | seed SE of share |','|---|---|---|---|---|---|---|---|']
    for k in keys:
        for rg in regs:
            r_=df[(df.key==k)&(df.region==rg)].iloc[0]
            L_.append(f"| {NM.get(int(k[1]),k) if 'joined' not in k else k} | {rg} | {r_.share:.5f} | {r_.ess:.0f} | {r_.eff_parents:.0f} | {r_.A1_share_in_region:.2f}/{r_.A2_share_in_region:.2f}/{r_.B_share_in_region:.2f} | {r_.get('C1_share_in_region',np.nan):.3f} | {r_.seed_share_se:.5f} |")
    return '\n'.join(L_)
MD_Q1=q1md(q1m,HK,['strip','X50','X100','X200','X400'])
MD_Q1H=q1md(q1m,HK,['H50','H100','H200','H400'])
MD_Q1J=q1md(q1j,[f'D{d} joined V2' for d in range(5)],['strip','X50','X200'])
def q2md(df,keys):
    L_=['| 00:19 option | branch, s_b | ln B (rate background) | ln B (one arrival) | conditional ESS | eff. parents | share in strip / X200 | A1/A2/B | C1 share | per-seed ln B min/median/max |','|---|---|---|---|---|---|---|---|---|---|']
    for k in keys:
        for vn in W.VNAME:
            r_=df[(df.key==k)&(df.variant==vn)].iloc[0]
            L_.append(f"| {NM.get(int(k[1])) if 'joined' not in k else k} | {vn[0]}, {vn[1:]} deg | {r_.ln_B_rate:.2f} | {r_.ln_B_single:.2f} | {r_.ess_conditional:.0f} | {r_.eff_parents_conditional:.0f} | {r_.cond_share_strip:.2f} / {r_.cond_share_X200:.2f} | {r_.cond_A1_share:.2f}/{r_.cond_A2_share:.2f}/{r_.cond_B_share:.2f} | {r_.get('cond_C1_share',np.nan):.3f} | {r_.seed_lnB_min:.1f} / {r_.seed_lnB_median:.1f} / {r_.seed_lnB_max:.1f} |")
    return '\n'.join(L_)
MD_Q2=q2md(q2m,HK); MD_Q2J=q2md(q2j,[f'D{d} joined V2' for d in range(5)])
print(MD_Q2[:1500])