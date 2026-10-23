
import run_j_windows as Wm
rxall=Wm.receivers(); print(list(rxall))
DARC={}
for rx in rxall:
    rl_,ro_=rxall[rx]; _,_,dd=G.inv(flo,fla,np.full_like(flo,ro_),np.full_like(fla,rl_)) if 'flo' in dir() else (0,0,0)
