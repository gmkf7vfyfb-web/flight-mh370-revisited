for kw in ['29 March','New Zealand','RNZAF','Orion']:
    for m in re.finditer(kw,a):
        print(kw,'p',pgp(m.start()),'||',re.sub(r'\s+',' ',a[max(0,m.start()-200):m.end()+250])[:450]); 
    print('--')
import pandas as pd
df=pd.read_csv(host.artifact_path('ca0ffc27-7931-47a6-8799-aca36744dc20'))
print(df.columns.tolist()); print(df.head(3).to_string()[:1500]); print(df.shape)