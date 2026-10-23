cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/43360090-fdd3-4918-a664-de9fef7e80f6/articles/ && python3 - <<'EOF'
t=open('10.1038_s41598-017-14177-3.pdf.txt').read()
i=t.find('Analysis of CTBTO data'); print(t[i:i+5200]); print('======')
t2=open('10.1038_s41598-018-37626-z.pdf.txt').read()
i=t2.find('Results'); print(t2[i:i+4500])
EOF