cd gfx && python - <<'E'
s=open('charts_traces.py').read()
s=s.replace("96.2 dB; this '\n            f'recording is louder). Pulse: \"","96.2 dB; this \"\n            f\"recording is louder). Pulse: \"")
open('charts_traces.py','w').write(s)
E
python -c "import ast;ast.parse(open('gfx/charts_traces.py').read());print('ok')"