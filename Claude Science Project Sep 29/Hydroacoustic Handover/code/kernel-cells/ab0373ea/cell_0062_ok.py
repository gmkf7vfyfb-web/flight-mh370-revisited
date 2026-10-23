def watch_until(hhmm):
    global stopped_reason
    tgt = dt.datetime.combine(dt.date.today(), dt.time(*map(int, hhmm.split(":"))))
    while dt.datetime.now() < tgt and proc.poll() is None:
        f = free_gib()
        if f < 9.0:
            proc.send_signal(signal.SIGINT); stopped_reason = f"disk {f:.1f} GiB < 9 at {dt.datetime.now():%H:%M}"; break
        time.sleep(30)
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT); stopped_reason = stopped_reason or f"soft deadline {hhmm} (SIGINT; pool terminated, finished jobs kept)"
        try: proc.wait(120)
        except Exception: proc.terminate()
    lines = [l for l in open(OUT / "run2.log").read().splitlines() if "ok ram" in l or "failed" in l]
    print(proc.poll(), len(lines), lines[-1:], f"free {free_gib():.1f} GiB", stopped_reason, dt.datetime.now().strftime("%H:%M"))
watch_until("03:35")