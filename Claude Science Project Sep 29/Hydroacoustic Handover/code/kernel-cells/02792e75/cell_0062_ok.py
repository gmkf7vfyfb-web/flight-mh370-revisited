p="out/sources-sightings-dossier.md"; s=open(p).read()
s=s.replace("by the crew of a **PLA Air Force Il-76**\n   with an Australian pilot aboard","by the crew of a **PLA Air Force search aircraft** (type not stated in the 5 Apr reports)\n   with an Australian pilot aboard")
s=s.replace("| Observer | PLA Air Force aircraft (Il-76 per Xinhua 24–29 Mar reporting pattern; 5 Apr report says \"Chinese Air Force aircraft\"); Australian pilot aboard reported to JACC |",
            "| Observer | One PLA Air Force aircraft; type not stated in the 5 Apr reports (the PLAAF aircraft flying from Perth in March were Il-76s); Australian pilot aboard reported to JACC |")
s=s.replace("Il-76's task area","aircraft's task area").replace("Il-76 task area","Aircraft task area")
s=s.replace("icao2015wp30 (§2.21–2.26)","icao2015wp30 (§2.22–2.26)")
open(p,"w").write(s); print(s.count("Il-76"))