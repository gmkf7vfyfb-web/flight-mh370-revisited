cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python -c "
import ast
print(ast.get_docstring(ast.parse(open('calibration_events.py').read()))[3000:12000])
"; wc -l calibration_events.py; grep -n "^def \|^    def \|argv\|__main__" calibration_events.py | head -40; cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/0f0b1c26-b241-4b3b-9f87-53c4386c8175; git -C hydro log --oneline -1 -- "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/calibration_events.py"