
src7=inspect.getsource(chart7)
src7=src7.replace("""    b1.text(x[-1],band['near']['trk'][-1,1]-5,'impact within\\n150 km of G',color=C_NEAR,fontsize=6.5,ha='right',va='top'); b1.text(x[-1],band['rest']['trk'][-1,1]+2,'all others',color='#666666',fontsize=6.5,ha='right',va='bottom')\n""",
"""    b2.legend(handles=[Line2D([],[],color=C_NEAR,lw=1.6,marker='o',ms=2.5,label='impact within 150 km of G'),Line2D([],[],color=C_REST,lw=1.2,marker='o',ms=2.5,label='all other paths')],loc='lower left',frameon=False,fontsize=6.5)\n""")
src7=src7.replace("b1.text(0.5,0.97,'22:41 handshake',transform=b1.get_xaxis_transform()","b1.text(1.0,0.02,' 22:41 handshake',transform=b1.get_xaxis_transform()").replace("fontsize=6.5,color='#555555',va='top',ha='left')","fontsize=6.5,color='#555555',va='bottom',ha='left')")
assert 'b2.legend' in src7
exec(src7); fig=chart7(); save(fig,'chart7-paths-track-speed-pair-g')
