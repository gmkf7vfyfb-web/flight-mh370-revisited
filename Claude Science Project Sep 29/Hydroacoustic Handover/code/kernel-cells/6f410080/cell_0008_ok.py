for k in ['sir','factual','marghany','guardian']:
    t=open(f'handoff/{k}.txt').read()
    print(k, re.findall(r'\[\*\*Page (\d+)\*\*\]',t)[:3])
    n=pagesnips(k,r'satellite imag|imagery|Pl[eé]iades|Gaofen|THEOS|WorldView|DigitalGlobe|Thai|Tomnod',w=500)
    print(n)
print(open('handoff/sir_psnip.txt').read()[:6000])