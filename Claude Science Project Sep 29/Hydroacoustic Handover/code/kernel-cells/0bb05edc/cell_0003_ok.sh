f="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/tool-results/0bb05edc-67da-48f0-9322-bf94577b110d/tool-results/toolu_01BXxeaxwD3JJS1CvkKRCTmz.txt"
grep -n "pdf count" "$f"
grep -iE "kadri|airplane|remote|s41598|srep|nature|detection" "$f" | grep -viE "^.*(fig-|hydroacoustics-air9|\.png)" | head -40
echo ---; grep -iE "\.pdf" "$f" | grep -viE "fig|hist|gather|validation|comparison|hydroacoustics-|map|chart|timeline|panel|curve|plot" | head -60