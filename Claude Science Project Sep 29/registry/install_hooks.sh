#!/bin/sh
# Install the project pre-push check in this clone. Run once in each clone: sh install_hooks.sh
# It copies hooks/pre-push to the git hooks folder of the clone. If a different pre-push hook is there, it keeps it as pre-push.before-registry.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
rel=$(git rev-parse --git-path hooks)
mkdir -p "$rel"
dest=$(cd "$rel" && pwd)
if [ -f "$dest/pre-push" ] && ! cmp -s "$here/hooks/pre-push" "$dest/pre-push"; then
  mv "$dest/pre-push" "$dest/pre-push.before-registry"; echo "kept the old hook as $dest/pre-push.before-registry"
fi
cp "$here/hooks/pre-push" "$dest/pre-push" && chmod +x "$dest/pre-push"
echo "installed: $dest/pre-push"
