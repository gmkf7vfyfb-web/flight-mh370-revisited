s = host.get_local_compute_stats(time_range=1800, sample_frequency=300)
m = s['machine']; print({k: m.get(k) for k in ('load1','load5','host_cores','cpu_busy_cores','cpu_free_cores','available_gb','disk_available_gb')})
print(s.get('kernels'))
for row in (s.get('series') or [])[-6:]: print(row)