files=sorted(os.listdir('jobB'))
jobB = c.submit_job(
    intent='HEAVY, queued: debris-drift L-point likelihood (26 nodes, 3e5-1e6 particles, both ocean models, ~2-3 h at 88 threads) + origin-connectivity extension snapshots; waits for the drift arc-latitude chain to finish, then holds the deskstar heavy lock',
    command='bash ./kadriB.sh',
    inputs=[f'jobB/{f}' for f in files],
    outputs=['out/*-nodes.csv','out/*-summary.toml','out/*.log','snapE-*.bin','SHA256SUMS'],
    transfer_limits={'max_file_mb': 200, 'max_total_mb': 800},
    run_timeout_s=36*3600)
print(jobB.id)