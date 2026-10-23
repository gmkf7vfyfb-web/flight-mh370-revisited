
k=40; ms=np.convolve(pf**2, np.ones(k)/k, mode='same')
med=np.median(ms)
for nm,i in (("T",iT),("C",iC)):
    w=ms[i-120:i+120]; print(nm, "max 1s ms", w.max().round(4), "panel median 1s ms", med.round(4), "excess", (w.max()-med).round(4), "SNR dB", (10*np.log10(w.max()/med)).round(2))
# distribution of 6-s window max of 1-s ms (for context)
mx1=np.array([ms[j:j+240].max() for j in range(0,len(ms)-240,240)]); print("median 6s-window max 1s ms", np.median(mx1).round(4), "SNR of that", (10*np.log10(np.median(mx1)/med)).round(2))
print("panel noise 1s SPL dB re 1uPa^2", (10*np.log10(med/1e-12)).round(1))
