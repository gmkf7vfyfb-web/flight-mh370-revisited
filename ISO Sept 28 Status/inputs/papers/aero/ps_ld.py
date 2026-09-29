import math
# PS-model B772 row (pycontrails ps-aircraft-params-20250328.csv)
S=427.8; AR=8.678038569; delta_2=0.020708613; cs=0.851726902; psi0=6.461822217
Xo=0.987569999; wc=0.767369197; j2=0.873764241; j1=0.078399473; j3=70.0
kappa=1.4; Rd=287.05287; g=9.80665
def isa(h):  # h in m, troposphere/strat
    if h<=11000:
        T=288.15-0.0065*h; p=101325*(T/288.15)**5.25588
    else:
        T=216.65; p=22632.06*math.exp(-g*(h-11000)/(Rd*T))
    return T,p
def mu(T): return 1.458e-6*T**1.5/(110.4+T)
def LD(m, M, h):
    T,p=isa(h)
    Re=S**0.5*M*(p/mu(T))*(kappa/(Rd*T))**0.5
    cf=0.0269/Re**0.14; cd0=cf*psi0
    k1=0.8*(1-0.53*cs)*cd0
    e=1.0/(1+0.03+delta_2+k1*math.pi*AR)
    CL=m*g/(kappa/2*p*M*M*S)
    mcc=wc-0.10*CL/cs**2; x=M*cs/mcc
    cdw=cs**3*j1*max(x-j2,0)**2 + j3*max(x-Xo,0)**4
    CD=cd0+CL*CL/(math.pi*AR*e)+cdw
    return CL/CD, CL, cd0, e, cdw
for h_ft in (35000, 25000, 15000, 5000):
    h=h_ft*0.3048
    best=max(((LD(174000,M/1000,h)[0],M/1000) for M in range(300,900,5)))
    print(f"FL{h_ft//100}: max L/D={best[0]:.2f} at M={best[1]:.3f}", end='; ')
    for M in (0.6,0.7,0.8,0.84,0.87,0.9,0.95):
        ld,CL,cd0,e,cdw=LD(174000,M,h)
        print(f"M{M}:L/D {ld:.1f}(CL {CL:.2f},CDw {cdw:.4f})", end=' ')
    print()
