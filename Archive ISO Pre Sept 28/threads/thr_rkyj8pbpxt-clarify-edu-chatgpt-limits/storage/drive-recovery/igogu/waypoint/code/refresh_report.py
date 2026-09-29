"""ARCHIVAL one-off migration: do not run on the final report.py."""
raise SystemExit("Use report.py directly; migration is archival")
from pathlib import Path
p=Path(__file__).with_name('report.py');s=p.read_text();s=s[:s.index("font='/usr/share/")]
s=s.replace("polys=[]", "polys=[];historic=[];arc7=[]")
s=s.replace("  for c in pm.findall('.//{*}Polygon//{*}coordinates'):polys.append(np.array([list(map(float,z.split(',')[:2])) for z in c.text.split()]))", "  for c in pm.findall('.//{*}coordinates'):polys.append(np.array([list(map(float,z.split(',')[:2])) for z in c.text.split()]))\n elif name is not None and name.text in ['Ocean Infinity 2018 search','Australia/China/Malaysia 2014-2017 search']:\n  for c in pm.findall('.//{*}coordinates'):historic.append(np.array([list(map(float,z.split(',')[:2])) for z in c.text.split()]))\n elif name is not None and name.text=='Arc 7 at 20000ft':\n  for c in pm.findall('.//{*}coordinates'):arc7.append(np.array([list(map(float,z.split(',')[:2])) for z in c.text.split()]))")
s=s.replace(" for i,p in enumerate(polys):ax.add_patch(Polygon(p,fill=False,edgecolor=orange,ls='--',lw=1.1))", " for p in historic:ax.plot(p[:,0],p[:,1],color='#92a2a8',lw=.7,alpha=.8)\n for p in arc7:ax.plot(p[:,0],p[:,1],color='#384653',lw=.8,ls=':')\n for p in polys:ax.plot(p[:,0],p[:,1],color=orange,ls='--',lw=1.4)")
s=s.replace("colors=purple,linewidths=[1,1.5]", "colors=purple,linewidths=[1.3,2]")
s=s.replace("'2024 proposal sketches')]", "'2024 proposal sketches'),Line2D([0],[0],color='#92a2a8',label='Historic search outlines (sketches)')]")
s=s.replace("stats['main_fuel']=dict(status='Density unresolved');", "ww=z['weights'];dd=interp(z['end'][:,2],z['end'][:,1]);stats['main_fuel']={'status':'Density unresolved','Pleiades50_mass':float(ww@(dd>=thresholds[.5])),'Pleiades90_mass':float(ww@(dd>=thresholds[.9]))};")
s=s.replace("s=6+130*z['weights']/z['weights'].max(),alpha=.25", "s=3+160*z['weights']/z['weights'].max(),alpha=.22")
s=s.replace("ax.legend(handles=legend,fontsize=8,loc='lower left')", "ax.legend(handles=[Line2D([0],[0],marker='o',ls='',color=blue,label='Weighted fuel locations')]+legend[1:],fontsize=9,loc='lower left')")
s=s.replace("figsize=(13,5.7)", "figsize=(10,5.8)")
s=s.replace("ax.set_title(sub,fontsize=11)", "ax.set_title(sub.replace(' + ',' +\\n'),fontsize=11)")
s=s.replace("fig.suptitle(label+' - conditional impact propagation',fontsize=16)", "fig.suptitle(label+' — trial impact mixture',fontsize=14)\n if source.startswith('main'):fig.text(.5,.88,'Parent importance ESS 4.8: contours are exploratory',ha='center',fontsize=10,color='#984d28')")
s=s.replace("ncol=3,fontsize=9", "ncol=2,fontsize=9")
s=s.replace("bottom=.17,top=.84,wspace=.18", "bottom=.18,top=.81,wspace=.30")
s=s.replace("fig,axs=plt.subplots(1,2,figsize=(12,4.8))", "fig,axs=plt.subplots(1,2,figsize=(10,4.7))")
s=s.replace("axs[1].barh(top.label.iloc[::-1]", "short=top.label.replace({'Vostok Skiway':'Vostok','Amundsen–Scott South Pole Station Airport':'South Pole','Union Glacier Blue-Ice Runway':'Union Glacier','Patriot Hills Airport':'Patriot Hills'})\naxs[1].barh(short.iloc[::-1]")
s=s.replace("ax.annotate(name,(q.longitude,q.latitude),xytext=(7,3),textcoords='offset points',fontsize=8)", "offset={'MEKAR':(28,18),'NILAM':(-55,14),'IGOGU':(-65,27),'BULVA':(15,-7),'ISBIX':(15,-6),'RUNUT':(-55,0)}[name];ax.annotate(name,(q.longitude,q.latitude),xytext=offset,textcoords='offset points',fontsize=9,arrowprops=dict(arrowstyle='-',lw=.5,color=grey))")
s += '''\n# Separate destination panels use the same catalog and rotation control.\nmdest=pd.read_csv(O/'main_destination_alignment.csv');mtop=mdest[mdest.angle_tolerance_deg==1].head(4)\nfig,axs=plt.subplots(1,2,figsize=(10,4.4))\nfor ax,tab,title in [(axs[0],top.head(4),'Earlier IGOGU ensemble'),(axs[1],mtop,'Main route — exploratory')]:\n labels=tab.label.replace({'Vostok Skiway':'Vostok','Amundsen–Scott South Pole Station Airport':'South Pole','Union Glacier Blue-Ice Runway':'Union Glacier','Patriot Hills Airport':'Patriot Hills','Navaid':'South Pole navaid'})\n ax.barh(labels.iloc[::-1],tab.weighted_alignment_fraction.iloc[::-1],color=blue);ax.set(xlim=(0,.6),xlabel='Fraction within 1°',title=title);ax.tick_params(axis='y',labelsize=9)\nfig.tight_layout();save(fig,'destination_comparison')\n'''
p.write_text(s+Path(__file__).with_name('report_pages.txt').read_text())
