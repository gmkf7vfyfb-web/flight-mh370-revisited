cd work; python - <<'E'
t=open("standin_note_template.md").read()
t=t.replace("{{FIG_WINDOWS}}","{{artifact:art_a886fd99-ba47-430e-a15e-12de51c1c38a}}").replace("{{FIG_POWER}}","{{artifact:art_e6b34c37-b6a0-410f-8384-5ce5241ab3e7}}").replace("{{FIG_RESULT}}","{{artifact:art_c4eaf781-b658-4241-8d85-cb7da185a66f}}")
t=t.replace("**Pre-registration:**","**Repository:** `claude-science-sep29` commit `7100e5391f59dd3333950875f0523cb2328d6d06`.\n**Pre-registration:**",1)
open("hydroacoustics-pleiades-test-standin.md","w").write(t)
E
cp ../repo/"Claude Science Project Sep 29"/results/hydroacoustics-pleiades-test-preregistration.md . ; grep -c "artifact:art_" hydroacoustics-pleiades-test-standin.md