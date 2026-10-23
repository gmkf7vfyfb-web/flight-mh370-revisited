wd='/home/pete/.claude-science-scratch/.claude-science/jobs/0d37c2df-178b-41c2-ae15-2bb5437a8d9b'
for m in ('globcurrent','glorys12'):
    r=c.download(f'{wd}/snapL-{m}.bin', f'hpc/0d37c2df-178b-41c2-ae15-2bb5437a8d9b/snapL-{m}.bin')
    print(r)