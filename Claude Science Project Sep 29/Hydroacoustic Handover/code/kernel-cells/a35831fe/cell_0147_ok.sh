cd "hyd/Claude Science Project Sep 29"; ls engine/hypotheses/hydroacoustics/ | head -30
grep -rnE "3\.3 ?(deg|°)|DEMONSTRATED" --include=*.md . | cut -c1-400 | head -12
echo =====; grep -rnE "0\.006 ?km|1\.482" --include=*.md . | cut -c1-350 | head -10
echo =====; grep -rnE "pick.{0,30}10 ?s|10 ?s.{0,20}pick" --include=*.md . | cut -c1-350 | head -10