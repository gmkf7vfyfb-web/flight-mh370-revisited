df -k /System/Volumes/Data | tail -1 | awk '{printf "free %.1f GiB\n",$4/1048576}'; uptime
cd repo; export GIT_CONFIG_GLOBAL=/dev/null
git sparse-checkout add "Claude Science Project Sep 29/engine/Makefile" "Claude Science Project Sep 29/engine/scripts" 2>&1 | grep -v 'config/git' || true
cd "Claude Science Project Sep 29/engine"; ls Makefile scripts 2>/dev/null | head; grep -n -A12 '^scope' Makefile | head -30