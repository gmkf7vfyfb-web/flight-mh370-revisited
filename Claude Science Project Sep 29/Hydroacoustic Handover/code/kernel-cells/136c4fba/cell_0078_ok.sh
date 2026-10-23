cd "repo/Claude Science Project Sep 29/engine" && export XDG_CONFIG_HOME=/tmp/xdg PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH"
echo "=== scope ==="; make scope H=hydroacoustics 2>&1 | tail -15
echo "=== smoke ==="; timeout 600 make smoke H=hydroacoustics 2>&1 | tail -12