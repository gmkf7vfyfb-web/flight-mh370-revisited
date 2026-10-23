
src3=inspect.getsource(chart3)
src3=src3.replace("LOC_OFF","LOC_OFF3")
LOC_OFF3={'A':(70,-6),'B':(70,-36),'E':(-95,-42),'F':(-85,34),'D':(-200,22),'G':(40,30)}
src3=src3.replace("xytext=(-125,40),textcoords='offset points',fontsize=6,color=C_T1","xytext=(30,-95),textcoords='offset points',fontsize=6,color=C_T1")
src3=src3.replace("""ax.text(0.02,0.02,f"{n35*100:.1f} % north of 35°S; {mG*100:.1f} % within 150 km of G",transform=ax.transAxes,fontsize=6.5)""",
 """ax.text(0.02,0.98,f"{n35*100:.1f} % north of 35°S; {mG*100:.1f} % within 150 km of G\\nHPD level at G {hpd_at(M,G['lat'],G['lon']):.2f}; at D {hpd_at(M,LOCI['D']['lat'],LOCI['D']['lon']):.2f}",transform=ax.transAxes,fontsize=6.5,va='top')""")
src3=src3.replace('"The pair locus G is at the northern edge of the 99 % region without drift and inside the 90 % region with drift; it is not a strong candidate"',
 '"The pair locus G lies on the edge of the 90 % region without drift and inside it with drift; the five highest-ranked pairs all point further south, near 37°S"')
src3=src3.replace("bbox_to_anchor=(0.06,0.335)","bbox_to_anchor=(0.06,0.30)").replace("figsize=(11,7.6)","figsize=(11,7.9)")
src3=src3.replace("each normalised to 1; HPD on cell mass","each normalised to 1; HPD level at a point = mass of cells at least as dense as the point's cell (smoothed); HPD on cell mass")
exec(src3); fig=chart3(); save(fig,'chart3-hpd-maps-pair-g')
