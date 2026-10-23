s=host.get_local_compute_stats(); print(s['machine'], s['kernels'])
import subprocess
print(subprocess.run("ls -la /tmp/.mh370-heavy.lock; lsof /tmp/.mh370-heavy.lock 2>&1 | head; uptime", shell=True, capture_output=True, text=True).stdout)