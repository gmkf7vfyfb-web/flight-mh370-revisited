tt=re.sub(r'\s+',' ',st[8]); k=tt.find('sea state of the ocean'); print(tt[k:k+2200])
tt2=re.sub(r'\s+',' ',st[9]); print('PDF p10:',tt2[:900])