t=open('handoff/opsearch.txt').read()
print(t[:600])
# find page markers style
print(re.findall(r'\n\s*(\d{1,3})\s*\n',t[:20000])[:40])