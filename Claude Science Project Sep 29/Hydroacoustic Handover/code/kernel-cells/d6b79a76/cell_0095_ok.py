def g1(df,k,rg,col): return df[(df.key==k)&(df.region==rg)][col].iloc[0]
for d in range(6):
    k=HK[d]; print(d, [f"{rg}:{g1(q1m,k,rg,'share'):.5f}/{g1(q1m,k,rg,'ess'):.0f}" for rg in ['strip','X50','X200','H50','H200']], 'P(strip|A1,A2,B)',[round(g1(q1m,k,'strip',f'P_region_given_{n}'),5) for n in ('A1','A2','B')])
print(q2m[q2m.key.str.contains('total')][['key','variant','ln_B_rate_A1','ln_B_rate_A2','ln_B_rate_B']].round(2).to_string())
print(CHW[CHW.variant.isin(['T1.0','C1.0'])][['key','variant','share_inside_arc','share_in_strip','impact speed m/s','turns begun','heading change deg','fuel at 00:11 kg']].map(fmt).to_string())
print(T.shape, M.shape)