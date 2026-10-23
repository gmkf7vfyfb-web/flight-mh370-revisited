
sltxt = open("src/mot_slides.txt").read()
for ln in sltxt.split("\n"):
    if re.search(r"(descent|fpm|glide|impact|fuel exhaust|simulat|00:19|BFO)", ln, re.I):
        print(ln.strip()[:150])
