
LOG.clear()
MZ="track metz-f35a on 22 Oct 2026 (`results/hydroacoustics-metz-f35a-anchor.md`)"
A='coordination/architecture.md'
sub(A,"  - The crash position and waveform are only in Metz et al. 2023, which is closed and not held.",
      "  - The crash position and waveform are only in Metz et al. 2023 (held: Pete bought it on 9 Oct 2026, artifact 7e4d336f; corrected 22 Oct 2026).")
sub(A,"- **H4: Metz et al. 2023 is still unobtainable.** The article-fulltext tool tried Unpaywall, Semantic\n  Scholar, PMC, Crossref TDM and the DOI landing page; all failed. F-35A stays blocked. If Pete holds the\n  PDF, an upload would unblock it. Contacting the authors is his decision, as ruled.",
      "- **H4: Metz et al. 2023.** The article-fulltext tool tried Unpaywall, Semantic\n  Scholar, PMC, Crossref TDM and the DOI landing page and returned nothing; that tool cannot reach a purchased copy.\n  Pete bought the paper on 9 Oct (artifact 7e4d336f). Contacting the authors for the waveforms is his decision, as ruled. [corrected 22 Oct 2026]")
sub(A,"**Correction to my ~05:00 entry.** \"Metz et al. 2023 is still unobtainable\" understated what is\navailable,",
      "**Correction to my ~05:00 entry.** The ~05:00 statement on Metz et al. 2023 understated what is\navailable,")
sub(A,"- **Metz et al.:** the paper is identified. The full text is paywalled, and Pete is purchasing it.","- **Metz et al.:** the paper is identified. Pete is purchasing it.")
sub(A,"The [Taylor1921] equation location is still open: the paper and LaCasce (2008) are closed access, so this is a library request for Pete.",
      "The [Taylor1921] equation location is still open: there is no copy of the paper or of LaCasce (2008) in the project store yet, so this is a library request for Pete.")
sub(A,"- Chapman (1988), JASA 84:697, is behind a paywall.","- Chapman (1988), JASA 84:697: no copy in the project store yet.")
sub(A,"Source spectrum would need Metz et al. 2023 (closed) — GAP.",f"Source spectrum would come from Metz et al. 2023 (held, artifact 7e4d336f; digitised by {MZ}).")
sub(A,"citing Metz et al. 2023, closed access). TL recalibration track: the F-35A spectrum is a GAP until Metz is obtained.",
      f"citing Metz et al. 2023, which Pete holds). TL recalibration track: the F-35A spectrum was an open item; Metz et al. 2023 is held (artifact 7e4d336f) and was digitised by {MZ}.")
sub(A,"- Gaps open: Metz 2023 (F-35A), Kadri 2019 JASA (closed), AF447 hydroacoustic source absent from the bibliography.",
      "- Open items: Metz 2023 (F-35A; held and digitised on 22 Oct), Dall'Osto 2019 JASA (ARA San Juan; was mislabelled 'Kadri 2019'; no copy in the store yet; Kadri 2019 is Sci. Rep. 9:912 and is held), AF447 hydroacoustic source absent from the bibliography.")
sub(A,"Metz et al. 2023 fetch: closed, no figures -> F-35A spectral route recorded as G4.",
      "Metz et al. 2023 (held, artifact 7e4d336f; the automated fetch returned nothing) -> F-35A spectral route recorded as G4; run on the held copy later on 22 Oct by track metz-f35a.")
sub(A,"G-K5 Metz 2023 / Kadri 2019 closed access)","G-K5 Metz 2023 held and digitised on 22 Oct / Dall'Osto 2019 no copy in store)")
sub(A,"Metz et al. 2023 and Kadri 2019 (closed\naccess). Disk:","Metz et al. 2023 (held; digitised by track metz-f35a) and Dall'Osto 2019 (JASA; no copy in the store yet). Disk:")
sub('coordination/HYDROACOUSTICS.md',"Metz et al. 2023 and Kadri 2019 (closed\naccess). Disk:","Metz et al. 2023 (held; digitised by track metz-f35a) and Dall'Osto 2019 (JASA; no copy in the store yet). Disk:")
R='results/hydroacoustics-references.md'
sub(R,"**Copyright:** nothing cited here is an unauthorised copy. Closed works are cited only through what open\nsources report about them, and are marked \"not held\".",
      "**Copyright:** nothing cited here is an unauthorised copy. Pete confirmed on 22 Oct 2026 that the project has the right to use every source stored in the repo, the Drive and the project source folders; a publisher's access status is not a reason to avoid a source. Each source's copy status (held, with its location, or no copy in the project store yet) is in `results/source-access-ledger-2026-10-22.csv`.")
sub(R,"- **Not held** (closed). Cited for context only; no values are taken from it.","- **No copy in the project store yet** (the companion report UCRL-TR-207323 is held). Cited for context only; no values are taken from the JASA paper.")
sub(R,"- **Not held** beyond the abstract.","- **Abstract only in the project store** (the lay-language paper is held).")
sub(R,"- **Not held** (closed). The equation is used as given in Brown2026 Eq. 2.","- **No copy in the project store yet.** The equation is used as given in Brown2026 Eq. 2.")
sub(R,"- **Not held** (closed). Cited for the conventional","- **No copy in the project store yet.** Cited for the conventional")
sub(R,"- **Not held** (closed). Cited for the alternative evidence scale","- **No copy in the project store yet.** Cited for the alternative evidence scale")
sub(R,"Not committed: copyrighted,\n  not open access.","Not committed to the public repo\n  (copyrighted).")
D='results/hydroacoustics-digitised-sources.md'
sub(D,"**The F-35A source spectrum needed by the TL-recalibration track therefore has to\n  come from Metz et al., which is closed access and not held (GAP).**",
      f"**The F-35A source spectrum needed by the TL-recalibration track therefore has to\n  come from Metz et al. (2023), which Pete holds (artifact 7e4d336f); it was digitised by {MZ}.** [corrected 22 Oct 2026]")
sub(D,"- Kadri 2019 (ARA San Juan): the paper is Kadri, Wang et al., JASA 146 (2019), doi 10.1121/1.5125251, \"Source\n  triangulation utilizing three-dimensional arrivals\" — closed access; `fetch_article_fulltext` was not attempted\n  because Europe PMC lists it as not open access. **GAP.**",
      "- \"Kadri 2019 (ARA San Juan)\" was a misattribution [corrected 22 Oct 2026]: JASA 146(4):2104 (doi 10.1121/1.5125251, \"Source\n  triangulation utilizing three-dimensional arrivals\") is by Dall'Osto (2019). Kadri (2019) is Sci. Rep. 9:912 (doi\n  10.1038/s41598-018-37626-z, sea-bottom elasticity, gold open access); it is held (artifact 133c4968;\n  exchange `sources/open-access-fetched-2026-10-22/`) and was extracted by track metz-f35a. The Dall'Osto paper has no\n  copy in the project store yet (abstract only); nothing from it has been digitised.")
sub(D,"Metz et al. (2023) is the source to obtain.","Metz et al. (2023) is the source (held, artifact 7e4d336f).")
sub(D,"Kadri 2019 (closed); Nielsen 12 figures","Kadri 2019 (Sci. Rep.; held, extracted 22 Oct); Nielsen 12 figures")
sub(D,"every named source touched except Kadri 2019 and AF447.","every named source touched except Kadri 2019 (Sci. Rep.; held since 22 Oct), Dall'Osto 2019 (no copy in the store) and AF447.")
sub(D,"(G4) F-35A spectrum absent from Brown — open, needs Metz et al.\n  2023 (closed access); (G5) Kadri 2019 closed access — open;",
      "(G4) F-35A spectrum absent from Brown — open; Metz et al.\n  2023 is held (artifact 7e4d336f) and was digitised on 22 Oct by track metz-f35a; (G5) 'Kadri 2019' was Dall'Osto 2019 (JASA, no copy in the store); Kadri 2019 (Sci. Rep.) is held —")
sub(D,"obtain Metz et al. 2023 and Kadri 2019 through\nPete or the Kadri collaboration;","Metz et al. 2023 and Kadri 2019 are held (extracted 22 Oct); ask Pete for Dall'Osto 2019 (JASA) if wanted;")
sub(D,"blocker: none for this block; G4/G5 need closed-access papers that only Pete or a collaborator can supply.","blocker: none for this block; G4 is closed by the 22 Oct extraction (anchor ruling pending); G5 needs Dall'Osto 2019 only if the San Juan 3-D arrival is to be used.")
BV='results/hydroacoustics-blackman-validation.md'
sub(BV,"`9854c72`: \"the paper contains NO F-35A waveform or spectrum ... has to come from Metz et al., which is NOT held (GAP)\"),",
        "`9854c72`: \"the paper contains NO F-35A waveform or spectrum ...\"; that message also recorded Metz et al. as unavailable, which was wrong: Pete has held it since 9 Oct, artifact 7e4d336f),")
sub(BV,"Metz, Obana & Fukao (2023; closed access, waveform request pending)","Metz, Obana & Fukao (2023; held, artifact 7e4d336f; waveform request pending)")
sub(BV,"returned\n  no full text or figures (closed access). The F-35A spectral route is recorded as **G4** and the block rests on route 1.",
        "returned\n  no full text or figures (the fetch tool cannot reach a purchased copy; the paper itself has been held since 9 Oct, artifact 7e4d336f). The F-35A spectral route is recorded as **G4**; track metz-f35a ran it on the held copy later on 22 Oct. The block rests on route 1.")
KP='results/hydroacoustics-kadri-package-v2.md'
sub(KP,"(G-K5, open) G4 Metz 2023 and G5 Kadri 2019 closed access — request D.","(G-K5, open) G4 Metz 2023 (held; digitised 22 Oct) and G5 Dall'Osto 2019 (no copy in store) — request D.")
sub(KP,"- blocker: Pete's approval (nothing is sent without it); G4/G5 closed-access papers.","- blocker: Pete's approval (nothing is sent without it).")
OS='results/hydroacoustics-overnight-2026-10-22-summary.md'
sub(OS,"spectrum (it cites Metz et al. 2023, closed access, G4); Kadri 2019 closed access (G5).","spectrum (it cites Metz et al. 2023, which Pete holds; G4); 'Kadri 2019' (G5) was Dall'Osto 2019 (JASA; no copy in the store), and Kadri 2019 is Sci. Rep. 9:912, held.")
sub(OS,"G4 (F-35A spectrum; needs Metz et al. 2023), G5 (Kadri 2019),","G4 (F-35A spectrum; Metz et al. 2023 is held, digitised 22 Oct), G5 (Dall'Osto 2019; was listed as 'Kadri 2019'),")
sub(OS,"(Metz et al. 2023 not held) rather than digitised; Kadri 2019 (closed access) and AF447","(Metz et al. 2023 is held; the track did not find it) rather than digitised; Dall'Osto 2019 (listed as 'Kadri 2019'; no copy in the store) and AF447")
sub(OS,"Metz et al. 2023 is closed (one fetch, nothing returned)","Metz et al. 2023 was not found by the track (one fetch, nothing returned; the paper is held, artifact 7e4d336f)")
sub(OS,"Metz et al. 2023 and Kadri 2019 via\n   Pete or a collaborator.","Metz et al. 2023 (held) was digitised on 22 Oct by track metz-f35a; Dall'Osto 2019 via Pete if wanted.")
sub('results/hydroacoustics-prior-work-critique.md',"| Not assessable: report not obtained |","| Report held (`royer-2016-LDO-201608.pdf`, artifact e6fa6f46; digitised in block 1); to be assessed in the next update of this critique |")
sub('results/hydroacoustics-literature-review.md',"Metz2023, Prario2023,","Prario2023,")
sub('results/hydroacoustics-literature-review.md',"and most of the theory papers in §4. **No load-bearing","and most of the theory papers in §4. Metz2023 was bought by Pete on 9 Oct 2026 and read in full after this review (artifact 7e4d336f). **No load-bearing")
sub('results/debris-drift-find-episodes.md',"Durgadoo's full text is not open access and was not re-read tonight.","Durgadoo's full text is open access (CC BY 4.0, NORA eprint 523313) and was not re-read tonight.")
RR='results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md'
sub(RR,"- Blackman et al. (2004, JASA) is paywalled. I used the abstract,","- Blackman et al. (2004, JASA): no copy in the project store. I used the abstract,")
sub(RR,"(most open access; JASA 2004 is paywalled)","(most open access; no copy of the JASA 2004 paper in the project store)")
sub(RR,"- **Blackman et al. 2004 JASA:** paywalled (publisher). The companion","- **Blackman et al. 2004 JASA:** no copy in the project store. The companion")
JP='paper/JON-MODEL-PAPERS.md'
sub(JP,"3 identified, **all closed access**. Metadata and publisher abstract only; listed in §3, excluded from the detailed table","3 identified; no copy in the project store (metadata and publisher abstract only); listed in §3, excluded from the detailed table until a copy is supplied")
sub(JP,"All\nthree are closed access; the Cambridge Core landing pages","No copy of the\nthree is in the project store; the Cambridge Core landing pages")
SR='results/satellite-coverage-2014-03/coincidence/literature/satellite-literature-register.csv'
sub(SR,"ATSB site does not answer from sandbox; not on Drive","Later revisions held (artifacts 7203665a and 5af6ca76; Drive 1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw); these two 2014 editions have no copy in the store")
sub(SR,"MH370 - First Principles Review,https://www.atsb.gov.au/,not retrieved,","MH370 - First Principles Review,https://www.atsb.gov.au/,artifact 5b08ea64 (atsb_first_principles_review_dec2016.pdf),")
sub(SR,"Not retrieved; O01 PDF p.4 says the Pleiades re-analysis complements the First Principles Review.","Held (artifact 5b08ea64) but not yet read for this register; O01 PDF p.4 says the Pleiades re-analysis complements the First Principles Review.")
sub(SR,"Not on Drive; ATSB site unreachable","Held as an artifact (5b08ea64); not on the Drive")
MP='threads/master-prompts/hydroacoustics.md'
sub(MP,"ask Metz's group for the F-35 paper and waveforms","ask Metz's group for the H11 waveforms (the paper is held, artifact 7e4d336f)")
sub(MP,"Vergoz 2021, Kadri 2019;","Vergoz 2021, Dall'Osto 2019;")
print(len(LOG),'substitutions applied')
