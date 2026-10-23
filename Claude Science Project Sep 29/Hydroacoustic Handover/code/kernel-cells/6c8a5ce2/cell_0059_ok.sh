cd .tmp/standin; python - <<'EOF'
s=open("chart_tau.py").read()
s=s.replace('"B. Why τ matters: energy in the detection band"','"B. Share of source energy in 5–40 Hz\\n(module convention: normalised over 1–500 Hz)"')
s=s.replace('ax[2].legend(frameon=False, loc="lower right")','ax[2].legend(frameon=False, loc="lower right"); ax[2].set_ylim(0, 0.25); ax[2].set_xlim(-0.6, len(strata) - 0.4)')
s=s.replace("Panel B: a longer duration puts less energy into the band the hydrophones use. ","Panel B: a longer duration puts less energy into the band the hydrophones use, but only up to 1 s. The module sets its coupling from the F-35A at each duration, so most of this effect cancels. ")
s=s.replace("band fraction ESD flat to 1/τ then f^-2.\")","band fraction ESD flat to 1/τ then f^-2, normalised over 1–500 Hz (audit F7), so it is constant for τ > 1 s; η_cal(τ) is inverted from the F-35A at each τ, so S_b(τ) cancels except through the TL spectral shape difference between the F-35A path and each impact path.\")")
open("chart_tau.py","w").write(s)
EOF
python chart_tau.py smoke_tau/summary.json "smoke: free seed 1" && echo ok