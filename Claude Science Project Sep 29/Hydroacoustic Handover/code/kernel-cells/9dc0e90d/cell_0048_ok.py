obs = pd.read_csv("repo/r/Claude Science Project Sep 29/engine/data/satcom-observations.csv")
print(obs.columns.tolist()); print(obs[obs.astype(str).apply(lambda r: '00:19' in ' '.join(r), axis=1)].to_string()[:800])
import subprocess
print(subprocess.run("grep -rn 'BTO_FIXED_OFFSET_US\\|GES_LAT\\|GES_LON\\|PERTH' 'repo/r/Claude Science Project Sep 29/engine/crates/satcom/src/'*.rs | head", shell=True, capture_output=True, text=True).stdout)