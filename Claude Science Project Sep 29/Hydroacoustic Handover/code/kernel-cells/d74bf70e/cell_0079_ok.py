import shutil, os, hashlib
D = "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/blackman"
os.makedirs(D, exist_ok=True)
files = {"blackman_shot_lines.csv":"dcc5ad17-e551-438b-bf67-8f15af75e96d","blackman_2003_events.csv":"eeea638b-4f8f-4cf5-8fd2-c10eed7c5a65",
 "blackman_2001_nonairgun_events.csv":"84984c13-9a7c-433e-a1cd-f07c9f164901","blackman_source_classes.csv":"2038faca-56e8-40bc-9bd1-7d7407729a5a",
 "blackman_transmission_loss.csv":"5d5a7707-dae5-4dfa-a9ec-130aabafd5b8","blackman_receiver_observations.csv":"762f97ad-1809-40bb-8c53-228f631e7c35",
 "receiver_observations_diff_vs_drive.csv":"394044c8-eab0-430e-b22a-93d52e39a45c","appendixB_timing_consistency.csv":"f5abe995-e189-4e99-a6cd-242750b353cc",
 "jd144_check.txt":"99bc4733-cad9-4ea7-acf7-882f87113f57","extraction_method.txt":"01fe3f65-9169-4fb0-948b-0fbf6b39dea8"}
for fn,v in files.items():
    p = host.artifact_path(v); shutil.copy(p, f"{D}/{fn}")
    print(fn, os.path.getsize(f"{D}/{fn}"))
# sanity: the shot lines and the negative control row
import pandas as pd
sl = pd.read_csv(f"{D}/blackman_shot_lines.csv", comment="#"); print(sl.shape, list(sl.columns)[:12])
ro = pd.read_csv(f"{D}/blackman_receiver_observations.csv", comment="#"); print(ro.shape)
print(ro[ro.apply(lambda r: "air8" in " ".join(map(str,r.values)), axis=1)].iloc[:, :8].to_string()[:1500])