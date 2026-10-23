cd leg; python -c "
import ast,sys
try: ast.parse(open('cond_pred.py').read())
except SyntaxError as e: print(e.lineno, repr(e.text))"; sed -n 59,62p cond_pred.py | cut -c1-60