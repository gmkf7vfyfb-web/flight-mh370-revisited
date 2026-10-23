cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22" && python - <<'EOF'
import pathlib
p=pathlib.Path('CALIBRATION_STATUS.txt'); t=p.read_text()
old=t[t.index('GATE STATUS:'):t.index('Station conditions on 8 March 2014')]
new='''GATE STATUS (block 7, injection-recovery on run J; committed 22 Oct ~04:45 UTC, pre-registration e816313; note
results/hydroacoustics-injection-recovery-run-j.md): P_D against received level now EXISTS at six receivers. With the envelope
matched filter (alpha 0.01 per 60 s window, tau 3.3 s) P_D = 0.5 at +7.0 / +6.6 / +4.8 / +4.0 dB above the background median at
IMOS 3376 / 3315 / 3274 / 3275 on their own REAL backgrounds, and at +7.8 / +8.5 dB at H01W / H08S on a PROXY background
(IMOS 3376 shaped to the digitised Blackman 2003 medians; single hydrophone). STA/LTA needs 10-16 dB, band energy 16-28 dB.
Detectability: under D0' p = 0.5 the coupling efficiency at which P_D(any unblocked receiver) = 0.5 is about 6e-4 (about 3 x the
F-35A anchor); P_D(any) at the anchor about 0.36; marginal over the four-decade eta prior P_D(any) is of order 0.1.
Gate verdict (rule 2): YES at the four IMOS loggers (model-matched caveat), PROXY-ONLY at H01W and H08S, BLOCKED H08N,
NO-INFORMATION 3250. No likelihood column has been written; composition (block 11) decides after review, and a ruling is
pending on whether IMOS terms may enter with the IMS terms at zero. For THIS package the consequence is: the IMS half of the
gate is exactly what request (b) asks Dr Kadri for - P_D(level) with his detector on real H01W/H08S background - and until it
arrives every IMS number here stays PREDICTIVE.

'''
p.write_text(t.replace(old,new))
r=pathlib.Path('REQUESTS.md'); s=r.read_text()
s=s.replace("""**Why:** the module's detection-probability model for the IMS stations is borrowed from an IMOS logger with a +4.8 dB
triad gain; this is the gate that decides whether hydroacoustics can enter the likelihood at all (block 7).""",
"""**Why:** the module's injection-recovery (block 7, 22 Oct) gives P_D against received level on REAL background at the four
IMOS loggers (P_D = 0.5 at +4 to +7 dB above the background median with the envelope matched filter, α = 0.01 per 60 s) but
only on a PROXY background at H01W and H08S (+7.8 / +8.5 dB; IMOS noise shaped to the digitised 2003 Blackman medians, single
hydrophone, no triad). The IMS half of the gate that decides whether hydroacoustics enters the likelihood is therefore his to
supply; the gate verdict today reads "proxy-only" at H01W/H08S.""")
r.write_text(s)
c=pathlib.Path('COVER_NOTE_FOR_PETE.md'); u=c.read_text()
u=u.replace("- Block 7 (injection-recovery) had not run when this was built; `CALIBRATION_STATUS.txt` says so.",
"- Block 7 (injection-recovery) landed while this was being built (~04:45 UTC); `CALIBRATION_STATUS.txt` and request B now carry\n  its verdict (real-background P_D at the IMOS loggers; proxy-only at H01W/H08S). The pending ruling on composing IMOS terms is\n  not a package matter.")
u=u.replace("the gate (block 7) described as pending.","the gate (block 7) described with today's verdict: real at IMOS, proxy-only at the IMS stations.")
c.write_text(u)
print(open('CALIBRATION_STATUS.txt').read()[t.index('GATE STATUS:'):t.index('GATE STATUS:')+400])
EOF
grep -n "proxy-only\|PROXY-ONLY" CALIBRATION_STATUS.txt REQUESTS.md COVER_NOTE_FOR_PETE.md | head