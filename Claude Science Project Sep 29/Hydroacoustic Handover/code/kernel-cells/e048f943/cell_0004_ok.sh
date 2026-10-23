cd repo/"Claude Science Project Sep 29"
cat threads/work-orders/hydroacoustics-order-2026-10-21.md
echo ======REFRESH
sed -n 505,625p threads/master-prompts/hydroacoustics.md
echo ======INBOX
sed -n 1661,1690p coordination/HYDROACOUSTICS.md