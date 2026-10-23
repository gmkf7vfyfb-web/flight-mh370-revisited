time.sleep(90)
lines = [l for l in open(OUT / "run2.log").read().splitlines() if "Warning" not in l]
print(proc.poll(), lines[:1], lines[-3:])
print(subprocess.run(["uptime"], capture_output=True, text=True).stdout)
print(subprocess.run(["df", "-k", "/System/Volumes/Data"], capture_output=True, text=True).stdout.splitlines()[-1])