import re
# verification: all v4 section headers survive, v4 sound text intact
v4_heads = re.findall(r"^## .*$", v4, re.M)
v5_heads = re.findall(r"^## .*$", v5, re.M)
print("v4 sections:", len(v4_heads), "| v5 sections:", len(v5_heads))
missing = [h for h in v4_heads if h not in v5_heads]
print("v4 headers absent from v5:", missing)
print("new in v5:", [h for h in v5_heads if h not in v4_heads])

# sound sections must be byte-identical where untouched
for probe in ["**`no-exhaustion-prior` is the seed.**",
              "The log-on is **one observation, used once**",
              "**Axis 1 — `[[terminal.options]]`",
              "Some operational descent figures in circulation come from mirrored copies",
              "**Phugoid period.** Lanchester's closed form",
              "**Still-air glide distance.**",
              "**Both deferred items above are to be put back in front of Pete"]:
    assert v5.count(probe)==1 and v4.count(probe)==1, probe
print("sound-section probes: all present exactly once in both versions")
print(f"\nv4 {len(v4):,} chars -> v5 {len(v5):,} chars (+{len(v5)-len(v4):,})")
print("edits applied:", len(EDITS))
open("end-of-flight.md","w").write(v5)
