import shutil, pathlib
t=open("work/hydroacoustics-pleiades-test-standin.md").read()
t=t.replace("Under H the impact is predicted earlier (shorter flight past the 7th arc toward the conditional region near 35.2 °S),\nso arrivals move 5-10 min earlier; the spreads still overlap by 0.69-0.83 everywhere.",
            "Under H the predicted arrivals are 5-10 min earlier at every station, because the impact times weighted by the Pléiades\nlikelihood are earlier (the cause has not been attributed here). The spreads still overlap by 0.69-0.83 everywhere.")
t=t.replace("Wall time: power check about 30 min for three\n    options; full-row pass 16 seeds in 30 min.","Wall time: power check about 40 min for three\n    options; full-row pass 16 seeds in about 30 min.")
t=t.replace("{WT}",WT).replace("{PT}",PT).replace("{RT}",RT).replace("{ST}",ST).replace("{ZT}",ZT)
repo_t=t.replace("{{FIG_WINDOWS}}","hydroacoustics-pleiades-test-standin-windows-r600-bto-only.png").replace("{{FIG_POWER}}","hydroacoustics-pleiades-test-standin-power-r600-bto-only.png").replace("{{FIG_RESULT}}","hydroacoustics-pleiades-test-standin-result.png")
R=pathlib.Path("repo/Claude Science Project Sep 29/results"); D=R/"hydroacoustics-pleiades-test-standin"
(R/"hydroacoustics-pleiades-test-standin.md").write_text(repo_t)
for o in ON:
    shutil.copy(f"work/fig_windows_{o}.png", R/f"hydroacoustics-pleiades-test-standin-windows-{o}.png")
    shutil.copy(f"work/fig_power_{o}.png", R/f"hydroacoustics-pleiades-test-standin-power-{o}.png")
    (D/"power"/o).mkdir(parents=True,exist_ok=True); shutil.copy(f"work/power/{o}/power_check.json", D/"power"/o/"power_check.json")
shutil.copy("work/fig_result_rhyd.png", R/"hydroacoustics-pleiades-test-standin-result.png")
(D/"result").mkdir(exist_ok=True)
for f in ("per_seed.json","rhyd_mixture.json"): shutil.copy(f"work/result/{f}", D/"result"/f)
for f in ("power_check.py","rhyd_result.py","rhyd_mix.py"): shutil.copy(f"work/standin-scripts/{f}", D/"standin-scripts"/f)
open("work/standin_note_template.md","w").write(t)
print(sorted(str(p.relative_to(R)) for p in D.rglob("*") if p.is_file()), len(repo_t))