
APPROVED="not retrieved — ask Pete"
pat3=re.compile(r"\b(not held|NOT held|Not held)\b(?! out| behind| at a band| fixed| constant| back)")
SKIP_FILES=('results/source-access-ledger-2026-10-22.md','results/hydroacoustics-run-j-levels.md')
SKIP_LINE=('"not held"','"Not held (closed)"','(GAP)',"'closed and",'165 cells','STANDING RULE','closed access')
changed={}; before_after=[]
for p in files('.md'):
    r=rel(p)
    if r.startswith(GEN_SKIP) or r in SKIP_FILES: continue
    raw=open(p,encoding='utf-8',newline='').read()
    lines=raw.split('\n'); new=[]; n=0
    for line in lines:
        o=line
        if not any(s in line for s in SKIP_LINE):
            line=line.replace("not held; nothing downloaded; ask Pete", APPROVED+"; nothing downloaded")
            line=line.replace("3250 (blocked)","3250 (North West Shelf in the path)")
            line=pat3.sub(APPROVED,line)
            line=line.replace("** "+APPROVED+".**","**"+APPROVED+".**")
        if line!=o: n+=1; before_after.append((r,o,line))
        new.append(line)
    if n:
        open(p,'w',encoding='utf-8',newline='').write('\n'.join(new)); changed[r]=n
print(len(changed),'files,',sum(changed.values()),'lines changed')
for k,v in sorted(changed.items()): print(' ',v,k)
print()
for r,o,nw in before_after[:12]:
    i=nw.find(APPROVED); print(r.split('/')[-1],'|',nw[max(0,i-50):i+60].strip())
