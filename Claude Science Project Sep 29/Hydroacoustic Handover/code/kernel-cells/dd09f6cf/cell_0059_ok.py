z=Z['run-j-waypoints'][0]
t=z['rows|t'][z['rows|mask|strip']]; fl=z['rows|flame'][z['rows|mask|strip']]
print('impact min after 00:00 UTC: median %.1f  q05 %.1f q95 %.1f | flameout median %.1f'%(np.median(t)/60,np.percentile(t,5)/60,np.percentile(t,95)/60,np.nanmedian(fl)/60))