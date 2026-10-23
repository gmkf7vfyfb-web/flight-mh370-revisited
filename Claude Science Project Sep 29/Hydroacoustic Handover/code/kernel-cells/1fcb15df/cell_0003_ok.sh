export GIT_CONFIG_GLOBAL=/dev/null
ls; cd hydro && git log --oneline -1 && git sparse-checkout list; cd ..; cd repo 2>/dev/null && git log --oneline -1 && git sparse-checkout list