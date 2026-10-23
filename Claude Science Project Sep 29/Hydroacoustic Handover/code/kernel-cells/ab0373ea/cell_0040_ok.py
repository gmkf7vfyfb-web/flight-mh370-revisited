import signal, datetime as dt
def free_gib():
    return int(subprocess.run(["df", "-k", "/System/Volumes/Data"], capture_output=True, text=True).stdout.splitlines()[-1].split()[3]) / 1048576
stopped_reason = None
t_end = time.time() + 540
while time.time() < t_end and proc.poll() is None:
    f = free_gib()
    if f < 9.0:
        proc.send_signal(signal.SIGINT); stopped_reason = f"disk {f:.1f} GiB < 9 at {dt.datetime.now():%H:%M}"; break
    time.sleep(30)
lines = [l for l in open(OUT / "run2.log").read().splitlines() if "ok ram" in l or "failed" in l]
print(proc.poll(), len(lines), lines[-1:], f"free {free_gib():.1f} GiB", stopped_reason, dt.datetime.now().strftime("%H:%M"))