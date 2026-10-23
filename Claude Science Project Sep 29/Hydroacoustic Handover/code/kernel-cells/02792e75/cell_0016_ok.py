t=texts["atsb2017_text.txt"][0]
idx=[m.start() for m in re.finditer("Haixun",t)]
print(idx)
# see page marker style near first
print(repr(t[idx[0]-300:idx[0]+100]))