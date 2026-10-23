for i in [7,8]:
    tt=re.sub(r'\s+',' ',st[i]); k=tt.find('Step 1'); 
    print('PDF p',i+1, tt[max(0,k-100):k+2200] if k>=0 else tt[:1800]); print()