i_h=src2c.find("    h=["); print(src2c[i_h-200:i_h+80].replace('\n','⏎'))
i_leg=src2c.find("    ax.legend(handles=h"); i_foot=src2c.find("    foot=("); i_txt=src2c.find("    fig.text(0.01,0.0")
print(i_h,i_leg,i_foot,i_txt)
print(src2c[i_foot:i_txt])