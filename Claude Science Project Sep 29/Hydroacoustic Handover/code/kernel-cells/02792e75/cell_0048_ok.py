for k in ["mr006","mr008","mr009"]:
    tt=re.sub(r"\s+"," ",jacc[k][2]); i=tt.find("Media Release"); print(k,"|",tt[i:i+1100],"\n")