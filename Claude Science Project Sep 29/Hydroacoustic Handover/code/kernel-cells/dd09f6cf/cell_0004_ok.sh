cd repo; P='Claude Science Project Sep 29'
git ls-tree -r --name-only HEAD -- "$P" | grep -iE 'seabed|search|surface|amsa|haixun|kadri|ocean-infinity|oi20|bathym' | grep -v '\.npy$' | head -150