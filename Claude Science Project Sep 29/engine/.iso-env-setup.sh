#!/usr/bin/env bash
# iso runs this in every new worktree (cwd = the worktree). It links the git-ignored inputs a
# worktree needs from the main checkout: every ignored file in data/ (environment grids,
# extracted fuel tables, ...), the Python venv, the base run that `make hypothesis` and
# `make sensitivity` compare against, and the large or licensed inputs kept outside git
# (data/external). A missing source is reported, never fatal.
set -u
main="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"
inputs="${MH370_INPUTS:-/jackbox/home/MH370-inputs}"

link() { # link <source> <path in this worktree>
    if [ ! -e "$1" ]; then echo "skipped $2: $1 does not exist"; return; fi
    if [ -e "$2" ] || [ -L "$2" ]; then echo "kept $2"; return; fi
    mkdir -p "$(dirname "$2")" && ln -s "$1" "$2" && echo "linked $2 -> $1"
}

git -C "$main" ls-files --others --ignored --exclude-standard --directory data/ | while read -r path; do
    link "$main/${path%/}" "${path%/}"
done
link "$main/.venv" .venv
link "$main/runs/davey2016" runs/davey2016
link "$inputs" data/external
exit 0
