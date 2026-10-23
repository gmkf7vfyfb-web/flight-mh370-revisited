python3 - <<'EOF'
from scipy import stats
import numpy as np
# Kadri chance calculation reconstructions
for N,w,sector in [(4,2,360),(8,5,360),(19,2,109),(19,0.5,109),(19,5,109)]:
    p=1-(1-2*w/sector)**N
    print(f"N={N} +/-{w} deg sector {sector}: P(any within) = {p:.3f}")
# Table 1 bearing stats
b=[261.24,268.24,256.77,303.28,309.96,253.66,311.98,343.16,291.13,234.67,260.41,320.40,329.51,324.26,274.84,257.58,315.46,306.18,314.15]
b=np.array(b); print('n',len(b),'range',b.min(),b.max(),'within +/-2 of 306.18 (excl self):',np.sum(np.abs(b-306.18)<=2)-1,' +/-5:',np.sum(np.abs(b-306.18)<=5)-1, ' +/-10:',np.sum(np.abs(b-306.18)<=10)-1)
# time span
print('span min', (55*60+7-(38*60+29))/60)
# Curtin Poisson: 2 events in 5 h
lo,hi=stats.chi2.ppf(0.025,4)/2, stats.chi2.ppf(0.975,6)/2
lam=2/(5*3600); T=280
for L in [lo/(5*3600),lam,hi/(5*3600)]:
    pB=L*T*np.exp(-L*T); print(f"lambda {L:.2e}/s -> P(B|notA) {pB:.4f}; prior for post 0.5: {pB/(1+pB):.4f}")
# 1/day rate
L=1/86400; pB=L*T*np.exp(-L*T); print('1/day:',round(pB,4))
# trials table
for W,B in [(3600,30),(7200,30),(3600,8),(900,30)]:
    n=2*W*B; z=stats.norm.isf(0.01/n); print(W,B,n,round(z,2))
for cut in [120,360]:
    n=2*3600*30/cut; print(cut, round(stats.norm.isf(0.01/n),2))
# Kadri 2017 ranging errors
for est,true in [(2500,2360),(5500,5600)]: print(est-true, round(100*(est-true)/true,1))
# Kadri E1 vs Curtin range
print('E1 discrepancy km', 4961.6-1900, 'in sigma', (4961.6-1900)/200)
# mode cutoffs
c=1500
for H in [3000,4000,5000]:
    fc=c/(4*H); print(H, round(fc,3), 'modes below 5 Hz', int((5/fc+1)//2), 'below 40 Hz', int((40/fc+1)//2))
EOF