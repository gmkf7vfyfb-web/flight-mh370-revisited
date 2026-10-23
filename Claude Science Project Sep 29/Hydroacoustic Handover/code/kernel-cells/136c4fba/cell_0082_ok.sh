cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python3 -m py_compile "$P/prepare/kadri_northern_conditional.py" && echo compiles
python3 -c "
import pandas as pd
C=pd.read_csv('$P/results-data/kadri_northern/candidates.csv')
q=C[(C.station=='H08S')&(C.option=='caption')]
print(q[['statistic','computable','observed','n_shots_in_window']].to_string(index=False))
print('no computable row has a blank value:', bool(((q.computable==True)&(q.observed.isna())).sum()==0))"
git add "$P/prepare/kadri_northern_conditional.py"
git -c user.name="hydroacoustics" -c user.email="hydroacoustics@local" commit -q -m "Hydroacoustics run J Task 1: disclose the correction to pre-registration declaration 2 - only the two closed-cycle statistics are untestable in the caption window, the four shot-window statistics are computable on 2 shots; original wording left in place" && git push -q origin hypothesis/hydroacoustics && echo "pushed $(git rev-parse --short HEAD)"