cd repo; export HOME=$PWD/../h XDG_CONFIG_HOME=$PWD/../h/.config
git sparse-checkout add "/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/"
git add --sparse "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18"
git status --short | head
git -c user.name="Claude Science" -c user.email="noreply@example.com" commit -qm "Kadri-Haixun conditional: pre-registration and corrected bearing-arc geometry"
git pull -q --rebase origin claude-science-sep29 && git push origin claude-science-sep29 2>&1 | tail -1; git log -1 --format='%h %s'