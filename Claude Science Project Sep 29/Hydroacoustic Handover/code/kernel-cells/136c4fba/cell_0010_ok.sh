cd "repo/Claude Science Project Sep 29" && export XDG_CONFIG_HOME=/tmp/xdg
echo "=== inbox: section headings ==="; grep -n "^#" coordination/HYDROACOUSTICS.md | tail -40
echo; echo "=== inbox tail 120 lines ==="; tail -120 coordination/HYDROACOUSTICS.md
echo; echo "=== operating guide present? ==="; ls threads/ ; find . -name "thread-and-module-operating-guide.md" -o -name "*RUN-STATE*" | head