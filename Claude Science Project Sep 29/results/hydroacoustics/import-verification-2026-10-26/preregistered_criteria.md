# Pre-registered pass criteria - verification of hydroacoustics repository import 26 Oct 2026
Written before any recomputation (verifier session 8b907e71).
V1 k factor: AGREE if my RMS/p-p scale factor k per station within 2% of producer (5.176 H01W, 5.145 H08S) - i.e. |dB diff| <= 0.17 dB; MINOR if within 5%; else DISAGREE.
V1 levels: AGREE if my 5-40 Hz median 1-s RMS level within 0.3 dB of producer per panel/case; MINOR 0.3-1.0 dB; DISAGREE >1 dB. Second estimator same tolerance. 1-sigma judged adequate if it covers spread across estimator choice/k variation; else flagged.
V2 IMOS band levels: AGREE if 10-20 and 20-40 Hz levels within 0.05 dB of noise_estimate and gain application confirmed; MINOR <=0.5 dB; DISAGREE >0.5 dB.
V3 CMST overlay: AGREE if peak and p99 ratios within 0.2 dB of producer -0.69 / -0.42 dB; MINOR <=0.5 dB; else DISAGREE.
V4 Royer offset: AGREE if offset within 0.3 dB of +5.81 and transferred levels within 0.3 dB; sigma within 0.3 dB of 1.61; fragility judged by whether 6 dB line inside 1-sigma.
V5 stage-3 tables: AGREE if row count exact, source SHA-256 exact, column sum within 1e-9 relative.
V6 DB: AGREE if SHA-256 equals e0442ace...caf91 and (if inputs available) rebuild gives 182 checks/179 PASS/3 REVIEW; NOT VERIFIED for rebuild if inputs not available read-only.
