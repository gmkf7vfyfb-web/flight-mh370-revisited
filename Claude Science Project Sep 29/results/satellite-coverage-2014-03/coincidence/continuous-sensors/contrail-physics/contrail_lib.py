"""Contrail formation (Schmidt-Appleman criterion) and persistence physics.
References
 - Schumann U. (1996) Meteorol. Z. 5, 4-23: SAC, mixing-line slope G, T_LM approximation.
 - Sonntag D. (1994) Meteorol. Z. 3, 51-66: saturation vapour pressure over liquid / ice (as used in CoCiP / pycontrails).
 - Teoh R. et al. (2022) ACP 22, 10919, Eq. 1: ERA5 HRES RHi correction, North Atlantic (a=0.9779, b=1.635, cap 1.65).
 - Teoh R. et al. (2024) ACP 24, 6071, Eqs. 2-4: latitude-dependent global correction; coefficients as implemented by the
   same group in pycontrails ExponentialBoostLatitudeCorrectionHumidityScaling (pressure levels, q_method=None).
"""
import numpy as np
EPS = 0.6219     # R_d/R_v (pycontrails epsilon = 287.05/461.51)
CP = 1004.0      # J kg-1 K-1 (pycontrails c_pd)

def e_liq(T):   # Pa, Sonntag 1994
    return 100.0*np.exp(-6096.9385/T + 16.635794 - 0.02711193*T + 1.673952e-5*T**2 + 2.433502*np.log(T))
def e_liq_prime(T):
    return e_liq(T)*(6096.9385/T**2 - 0.02711193 + 2*1.673952e-5*T + 2.433502/T)
def e_ice(T):   # Pa, Sonntag 1994
    return 100.0*np.exp(-6024.5282/T + 24.7219 + 0.010613868*T - 1.3198825e-5*T**2 - 0.49382577*np.log(T))

def vapour_pressure(q, p):
    """q specific humidity kg/kg, p Pa -> e Pa"""
    return q*p/(EPS + (1-EPS)*q)

def G_slope(p, eta, ei_h2o=1.25, Q=43.2e6):
    """Mixing-line slope Pa/K (Schumann 1996 eq. 4)."""
    return ei_h2o*CP*p/(EPS*Q*(1-eta))

def T_LM(G, iters=6):
    """Threshold temperature for liquid saturation of the mixing line (K): Schumann (1996) approximation
    refined by Newton iteration on de_liq/dT = G (exact tangent point)."""
    lg = np.log(G - 0.053)
    T = -46.46 + 9.43*lg + 0.72*lg**2 + 273.15
    for _ in range(iters):
        f = e_liq_prime(T) - G
        # derivative of e_liq_prime numerically
        h = 1e-3
        fp = (e_liq_prime(T+h) - e_liq_prime(T-h))/(2*h)
        T = T - f/fp
    return T

def sac(T, e, p, eta):
    """True where the Schmidt-Appleman criterion is met: ambient T below T_LM and mixing line
    reaching liquid saturation, i.e. e + G (T_LM - T) >= e_liq(T_LM)."""
    G = G_slope(p, eta); tlm = T_LM(G)
    return (T < tlm) & (e + G*(tlm - T) >= e_liq(tlm)), tlm

def rhi_max(T):
    out = e_liq(T)/e_ice(T)
    low = T <= 235.0
    return np.where(low, 1.67 + (1.45-1.67)*(T-190.0)/(235.0-190.0), out)

def rhi_correct_teoh2022(rhi):
    a, b = 0.9779, 1.635
    r = rhi/a
    return np.where(r > 1, np.minimum(r**b, 1.65), r)

def rhi_correct_teoh2024(rhi, lat, T):
    a1, a2, a3, a4 = 0.062621, 0.95224, 0.45893, 39.254
    b1, b2, b3, b4 = 1.4706, 1.4325, 0.44312, 18.755
    la = np.abs(lat)
    a = a1/(1+np.exp(a3*(la-a4))) + a2
    b = b1/(1+np.exp(b3*(la-b4))) + b2
    r = rhi/a
    r = np.where(r >= 1, r**b, r)
    return np.minimum(r, rhi_max(T))

def fl_to_pressure(fl):
    """ISA pressure (Pa) for flight level (hundreds of ft)."""
    h = np.asarray(fl)*100*0.3048
    p_trop = 101325*(1-2.25577e-5*np.minimum(h, 11000.0))**5.25588
    return np.where(h <= 11000, p_trop, 22632.06*np.exp(-(h-11000)/6341.62))
