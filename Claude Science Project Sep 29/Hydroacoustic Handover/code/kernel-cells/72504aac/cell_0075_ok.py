
src2=inspect.getsource(chart2)
src2=src2.replace("xytext=(15,-40),textcoords='offset points',fontsize=6.5,color=C_G","xytext=(25,45),textcoords='offset points',fontsize=6.5,color=C_G")
src2=src2.replace("xytext=(10,-18),textcoords='offset points',fontsize=6.5,color=C_HW,arrowprops","xytext=(-12,-30),textcoords='offset points',fontsize=6.5,color=C_HW,ha='right',arrowprops")
src2=src2.replace("at {r.lat:.2f}°S {r.lon:.2f}°E","at {-r.lat:.2f}°S {r.lon:.2f}°E")
exec(src2); fig=chart2(); save(fig,'chart2-trajectory-pair-g')
