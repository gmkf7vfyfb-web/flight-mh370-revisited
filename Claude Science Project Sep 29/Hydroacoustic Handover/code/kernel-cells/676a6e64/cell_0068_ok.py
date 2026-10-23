s = host.get_local_compute_stats(time_range=3600, sample_frequency=300)
m = s['machine']; print({k: m.get(k) for k in ('load1','load5','cpu_busy_cores','cpu_free_cores','disk_available_gb')}, s.get('kernels'))
for row in (s.get('series') or []): print(row)