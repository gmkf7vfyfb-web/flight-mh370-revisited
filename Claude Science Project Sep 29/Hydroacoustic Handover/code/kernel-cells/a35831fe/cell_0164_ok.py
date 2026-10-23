for kw in ['def chart2','star','candidate impact point','set_xlim','legend(','savefig','foot','Kadri bearing','plain','Plain words']:
    for mt in re.finditer(re.escape(kw),src2c):
        s=mt.start(); print('---',kw,s, src2c[max(0,s-150):s+250].replace('\n','⏎')[:400]); break