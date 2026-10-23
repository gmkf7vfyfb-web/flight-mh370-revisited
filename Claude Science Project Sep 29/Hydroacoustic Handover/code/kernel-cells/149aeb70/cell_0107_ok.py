print(host.findings.mark_addressed(
    ["e348e723-231a-44b2-90cb-6f5f0a1e32b3", "3dc51ac6-7e8c-4d93-99ab-4367a7c275b2"],
    note=("Both fixed in hydro-kadri-northern-conditional.md v3 (19dab9ef). (1) Proposed span lower bound "
          "corrected from 1,390 s to 1,346 s so it abuts the existing test's 1,347 s upper bound and the pair "
          "of searches is contiguous across 28.9 S; recomputed dt(-28.9)=1,346 s and dt(-22.0)=1,710 s, and the "
          "superseded 1,390 s value is noted in the artifact as leaving 28.9-28.0 S unsearched. (2) The locality "
          "percentages no longer mix runs: run I dive 0.36/1.21/2.31% and run I 0.37/1.19/2.28% are now quoted "
          "separately. Project memory row mem_fb3e17d86ad7 corrected to match.")))
