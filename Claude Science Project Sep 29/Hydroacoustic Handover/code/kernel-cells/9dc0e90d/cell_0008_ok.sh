cd repo/r/"Claude Science Project Sep 29"
grep -rIn -i -E "flap (was|were)? ?(in the )?(retracted|stowed)|retracted position|trailing.edge damage|ditching.*(debris|flap)|fracture|interior (panel|debris)|cabin debris" --include=*.md . | cut -c1-240 | head -12
echo ===; grep -rIn -i -E "Indonesian radar|radar non-detection|not detected by" --include=*.md . | cut -c1-200 | head; echo ===; grep -rIn -i "Sri Lanka" --include=*.md . | cut -c1-200|head -3
echo ===; sed -n 20,40p results/hydroacoustics-prior-work-critique.md | cut -c1-200