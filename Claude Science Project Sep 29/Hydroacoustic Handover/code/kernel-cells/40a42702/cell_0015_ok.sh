F=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/tool-results/676a6e64-2eac-490f-b67d-6c3f5c82f047/tool-results/toolu_01KGQQgtZgsRv2rxqYGNwyHP.txt
grep -n '^--- ' $F
L=$(grep -n '^--- tl grid' $F | cut -d: -f1); sed -n "$((L)),$((L+14))p" $F
L=$(grep -n '^--- imos_tl' $F | cut -d: -f1); sed -n "$((L)),\$p" $F | cut -c1-400