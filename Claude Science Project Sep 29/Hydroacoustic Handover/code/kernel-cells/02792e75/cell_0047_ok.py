for k in sorted(jacc):
    ts,u,t=jacc[k]; tt=re.sub(r"\s+"," ",t)
    d=re.search(r"Media Release (\d+ April 2014[^ ]*)",tt)
    for m in re.finditer(r"[^.]*\b(object|debris|sighting|recovered|satellite)[^.]*\.",tt,re.I):
        s=m.group(0).strip()
        if len(s)<400: print(k,(d.group(1) if d else ts[:8]),"|",s[:300])