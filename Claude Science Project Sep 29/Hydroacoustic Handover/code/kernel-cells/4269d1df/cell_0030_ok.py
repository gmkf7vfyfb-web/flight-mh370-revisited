os.replace('jobsnap/run.sh','jobsnap/snaprun.sh')
files=sorted(os.listdir('jobsnap'))
jobS = c.submit_job(
    intent='Debris drift engine snapshots (light, 16 threads, ~10 min, <4 GB): forward drift 8 Mar - 6 Apr 2014 from Kadri/Haixun points and a 0.25 deg origin grid, both ocean models; no heavy lock (smoke-scale, 28-day forcing only)',
    command='bash ./snaprun.sh',
    inputs=[f'jobsnap/{f}' for f in files],
    outputs=['snap*.bin','log-*.txt','SHA256SUMS','snap-*.toml'],
    transfer_limits={'max_file_mb': 200, 'max_total_mb': 600},
    run_timeout_s=5400)
print(jobS)