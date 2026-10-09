"""Fetch one logger-day of IMOS raw .DAT files from the public bucket (item 3 background, pre-registered
in imos_injection.py). Writes <root>/<logger>/<day>/*.DAT and appends 'sha256  path  size  key' lines
to <root>/<logger>/SHA256SUMS.txt. Idempotent (skips files already present with the listed size).
Usage: python fetch_imos_background.py <root> <site> <logger> <yyyymmdd>"""
import hashlib, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BUCKET = "https://imos-data.s3-ap-southeast-2.amazonaws.com/"


def keys(prefix):
    out, start = [], None
    while True:
        u = BUCKET + "?list-type=2&prefix=" + urllib.parse.quote(prefix) + (f"&start-after={urllib.parse.quote(start)}" if start else "")
        x = urllib.request.urlopen(u, timeout=60).read().decode()
        k = re.findall(r"<Key>([^<]+)</Key><LastModified>[^<]+</LastModified><ETag>[^<]+</ETag><Size>(\d+)</Size>", x)
        out += [(a, int(b)) for a, b in k]
        if "<IsTruncated>true" not in x:
            return out
        start = k[-1][0]


def get(args):
    key, size, dest = args
    if dest.exists() and dest.stat().st_size == size:
        data = dest.read_bytes()
    else:
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(BUCKET + urllib.parse.quote(key), timeout=120).read()
                if len(data) == size:
                    break
            except Exception:
                if attempt == 3:
                    raise
        tmp = dest.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(dest)
    return f"{hashlib.sha256(data).hexdigest()}  {dest.name}  {size}  {key}"


def main(root, site, logger, day):
    d = Path(root) / logger / day
    d.mkdir(parents=True, exist_ok=True)
    ks = [(k, s) for k, s in keys(f"IMOS/ANMN/Acoustic/{site}/{logger}/{day}/raw/") if k.upper().endswith(".DAT")]
    with ThreadPoolExecutor(4) as ex:
        lines = list(ex.map(get, [(k, s, d / k.split("/")[-1]) for k, s in ks]))
    with open(Path(root) / logger / "SHA256SUMS.txt", "a") as f:
        f.write("\n".join(f"{line.split('  ')[0]}  {day}/{line.split('  ', 1)[1]}" for line in lines) + "\n")
    print(logger, day, len(lines), "files")


if __name__ == "__main__":
    main(*sys.argv[1:5])
