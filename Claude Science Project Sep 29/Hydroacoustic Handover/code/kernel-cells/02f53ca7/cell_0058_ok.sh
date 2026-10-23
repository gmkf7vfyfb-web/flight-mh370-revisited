cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"
python - <<'EOF'
import pandas as pd, numpy as np, json
RES="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/02f53ca7-66d6-4371-9a5a-275163236205/repo/Claude Science Project Sep 29/results/hydroacoustics-audit/data/air9_residuals.csv"
A=pd.read_csv(RES); A=A[(A.model=='M1')&(A.src_depth_m==10)]
def ols(fc,r):
    x=np.log2(fc); c=np.polyfit(x,r,1); e=r-np.polyval(c,x); se=np.sqrt(e@e/max(len(r)-2,1)/((x-x.mean())**2).sum()); return c[0],se,np.sqrt(np.mean(e**2))
print("uncorrected (audit sign, TL_obs-TL_model) slopes, with and without 40 Hz:")
for st in ('H01W','H08S'):
    a=A[A.station==st].sort_values('fc_hz'); m=a.fc_hz!=40
    print(st, 'all', np.round(ols(a.fc_hz.values,a.residual_db.values),2), 'no40', np.round(ols(a.fc_hz.values[m],a.residual_db.values[m]),2))
pv=A.pivot(index='fc_hz',columns='station',values='residual_db').dropna(); d=pv.H01W-pv.H08S
print('station difference d_b (audit sign): median', round(d.median(),2), 'slope all', np.round(ols(d.index.values,d.values),2), 'no40', np.round(ols(d.index.values[d.index!=40],d.values[d.index!=40]),2))
G=pd.read_csv('route1_grades.csv'); b=G[(G.weights=="V^(1/3)")&(G.sign==1)&(G.ball=="both")&(G.SL_B==235)]
gr=b.groupby(['zs','xh','zh']).g_slope.apply(lambda s:(s!='FAIL').all()).reset_index()
print('grid both-slope-ok by zs:', gr.groupby('zs').g_slope.mean().to_dict(), 'by zh:', gr.groupby('zh').g_slope.mean().to_dict(), 'by xh:', gr.groupby('xh').g_slope.mean().to_dict())
print('H01W slope range over grid', b[b.station=='H01W'].slope.min().round(2), b[b.station=='H01W'].slope.max().round(2), '; H08S', b[b.station=='H08S'].slope.min().round(2), b[b.station=='H08S'].slope.max().round(2))
print('shape grid both ok fraction', b.groupby(['zs','xh','zh']).g_shape.apply(lambda s:(s!='FAIL').all()).mean())
R=pd.read_csv('air8_recal.csv'); print(R.round(2).to_string(index=False))
E=pd.read_csv('tl_runs_ext.csv'); C=pd.read_csv('air7_corridor.csv')
for d in (30,40,50):
    e=E[E.tag==f'air7off+{d}_H01W'].set_index('fc_hz').tl_db.reindex(C.fc_hz).values; ex=e-C.tl_air9_H01W_db.values-C.dtl_obs_db.values
    print('ext',d,'excess 31.5-63 median', np.nanmedian(ex[3:]).round(1), np.round(ex,1))
print(json.load(open('wall_tl.json')))
EOF