t=open('handoff/amsa.txt').read()
for w in ['French','France','Thai','satellite','Japan','122','300 ']:
    for m in re.finditer(w,t):
        s=t[max(0,m.start()-250):m.end()+250].replace('\n',' ')
        # page number
        pg=re.findall(r'Page (\d+) of 34',t[:m.start()])
        print(w,'p',pg[-1] if pg else '?','|',s[:500]);print('--')