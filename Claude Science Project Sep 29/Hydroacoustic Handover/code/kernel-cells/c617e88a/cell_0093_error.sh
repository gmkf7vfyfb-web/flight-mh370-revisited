cd work; python - <<'E'
t=open("standin_note_template.md").read()
m=lambda a: "{"+"{artifact:art_"+a+"}"+"}"
t=t.replace("{{FIG_WINDOWS}}",m("a886fd99-ba47-430e-a15e-12de51c1c38a")).replace("{{FIG_POWER}}",m("e6b34c37-b6a0-410f-8384-5ce5241ab3e7")).replace("{{FIG_RESULT}}",m("c4eaf781-b658-4241-8d85-cb7da185a66f"))
t=t.replace("**Pre-registration:**","**Repository:** `claude-science-sep29` commit `7100e5391f59dd3333950875f0523cb2328d6d06`.\n**Pre-registration:**",1)
open("hydroacoustics-pleiades-test-standin.md","w").write(t)
E
grep -c "artifact:art_" hydroacoustics-pleiades-test-standin.md; grep -c "FIG_" hydroacoustics-pleiades-test-standin.md