wc -c pete_msgs.txt; python - <<'E'
import re
t=open('pete_msgs.txt').read()
# drop recall/skill blocks
t=re.sub(r'\[Memory\] <memory_recall.*?</memory_recall>.*?\n(?=\S)', '[recall removed]\n', t, flags=re.S)
t=re.sub(r'\[System\] <skill_discovery.*?</skill_discovery>', '[skills removed]', t, flags=re.S)
open('pete_msgs_clean.txt','w').write(t); print(len(t))
E