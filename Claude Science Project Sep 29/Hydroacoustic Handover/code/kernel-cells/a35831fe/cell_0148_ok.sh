cd main; git log -1 --oneline; 
grep -rnE "3\.3 ?(deg|°)|DEMONSTRATED" --include=*.md . | cut -c1-500 | head -15
echo =====; grep -rnE "0\.006 ?km|± ?0\.006|\+/- ?0\.006" --include=*.md . | cut -c1-400 | head -10
echo =====; grep -rnE "pick.{0,40}10 ?s|10 ?s.{0,30}pick" --include=*.md . | cut -c1-400 | head -10