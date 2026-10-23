time.sleep(1500)
lines = [l for l in open(OUT / "run2.log").read().splitlines() if "ok ram" in l or "failed" in l]
print(proc.poll(), len(lines), lines[-2:])
print(subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip())
print(subprocess.run(["df", "-k", "/System/Volumes/Data"], capture_output=True, text=True).stdout.splitlines()[-1].split()[3])