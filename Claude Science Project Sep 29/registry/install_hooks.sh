#!/bin/sh
# Install the project pre-push check in this clone. Run once in each clone: sh install_hooks.sh
# It copies hooks/pre-push to the git hooks folder. If a different pre-push hook is there, it keeps it as pre-push.before-registry.
set -e
here=$(cd "$(dirname "$0")" && pwd)
dest=$(git -C "$here" rev-parse --git-path hooks)
case "$dest" in /*) ;; *) dest="$(git -C "$here" rev-parse --show-toplevel)/$dest" ;; esac
mkdir -p "$dest"
if [ -f "$dest/pre-push" ] && ! cmp -s "$here/hooks/pre-push" "$dest/pre-push"; then
  mv "$dest/pre-push" "$dest/pre-push.before-registry"; echo "kept the old hook as $dest/pre-push.before-registry"
fi
cp "$here/hooks/pre-push" "$dest/pre-push" && chmod +x "$dest/pre-push"
echo "installed: $dest/pre-push"
