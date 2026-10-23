
src5=inspect.getsource(chart5)
src5=src5.replace("""        ax.text(l+0.15,ymax*y,""","""        ax.text(l+(0.15 if k!='00:39:02' else -0.15),ymax*y,""").replace("color=c,fontsize=6.5,va='top')\n    for k,l in","color=c,fontsize=6.5,va='top',ha='left' if k!='00:39:02' else 'right')\n    for k,l in")
src5=src5.replace("""    for k,l in [('A',LOCI['A']['lat']),('B',LOCI['B']['lat']),('E',LOCI['E']['lat']),('F',LOCI['F']['lat'])]:
        ax.text(l,-ymax*0.035,k,""","""    for (k,l),dy in zip([('A',LOCI['A']['lat']),('B',LOCI['B']['lat']),('E',LOCI['E']['lat']),('F',LOCI['F']['lat'])],[0.012,0.012,0.012,0.05]):
        ax.text(l+(0.12 if k in('A','F') else -0.12),-ymax*dy,k,""").replace("fontsize=6.5,ha='center',va='top')","fontsize=6.5,ha='left' if k in('A','F') else 'right',va='top')")
src5=src5.replace("""    lines=['Arc crossing        lat °S  density  mass ±0.5°']
    for k,lab,l,d,m in rows: lines.append(f"{k:<9}{'':<11}{-l:5.2f}   {d:5.3f}   {m:5.3f}")""",
"""    lines=[f"{'crossing':<10}{'lat °S':>7}{'density':>9}{'±0.5°':>8}"]
    for k,lab,l,d,m in rows: lines.append(f"{k:<10}{-l:7.2f}{d:9.3f}{m:8.3f}")""")
src5=src5.replace("The pair locus sits on the northern shoulder of the impact density; Kadri\\'s 306.18° crossing sits in its tail",
                  "The pair locus lies in the thin northern tail of the impact density (about 5 % of the peak); Kadri\\'s 306.18° crossing lies further out")
src5=src5.replace("The pair point (33.6°S) is where the curve is about half its peak height.","At the pair point (33.6°S) the curve is about 5 % of its peak height, and 3 % of the simulated impacts are within 0.5° of it.")
src5=src5.replace('density per degree")','density per degree; ±0.5°: mass within 0.5°")')
exec(src5); fig,rows5=chart5(); save(fig,'chart5-latitudes-pair-g'); print(pdf.max(), xc[np.argmax(pdf)])
