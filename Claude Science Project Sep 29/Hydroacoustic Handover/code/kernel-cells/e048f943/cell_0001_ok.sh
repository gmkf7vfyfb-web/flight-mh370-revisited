export GIT_CONFIG_GLOBAL=/dev/null
cd hydro && git -c credential.helper= status | head -3; git sparse-checkout list; ls "Claude Science Project Sep 29" 2>/dev/null; cd ..
echo ---
cd repo && git -c credential.helper= status | head -3; git sparse-checkout list; ls "Claude Science Project Sep 29" 2>/dev/null; cd ..
du -sh hydro repo