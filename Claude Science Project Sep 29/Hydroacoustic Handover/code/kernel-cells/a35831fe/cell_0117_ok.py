import inspect, re as _re
src3=inspect.getsource(chart3).replace("ax.set_xlim(80,118)","ax.set_xlim(68,118)").replace("ax.legend(handles=h,fontsize=5.8,loc='lower left',framealpha=0.85)","ax.legend(handles=h,fontsize=5.8,loc='center right',bbox_to_anchor=(1.0,0.62),framealpha=0.9)")
exec(src3)
src2=inspect.getsource(chart2).replace("ax.text(Lo+dlon*0.55,L+dlat*0.85,","ax.text(Lo-dlon*0.95,L+dlat*0.9,")
exec(src2)
src4=inspect.getsource(chart4).replace("ax.text(len(RX4)-0.45,0.8,'noise median',fontsize=6,ha='right')","ax.text(-0.45,0.8,'noise median',fontsize=6,ha='left')")
exec(src4)
src1=inspect.getsource(chart1).replace("ax.text(0.5,0.5,'no data held at this time'+nxt","ax.set_yticks([]); ax.text(0.5,0.5,'no data held at this time'+nxt")
exec(src1)
files={}
for k in CANDS:
    files[k]=[chart1(k),chart2(k),chart3(k),chart4(k)]
print(files['A'])