W=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces
for f in cc6b3f2b-242b-40fa-b647-2bd32190a5f8 d2bd9c3e-51c3-45a1-ab65-1dbe7928c6a8 02f53ca7-66d6-4371-9a5a-275163236205 7adf9568-dd7f-4e62-823c-24873052d5fa; do
  for d in hydro repo tools; do [ -d "$W/$f/$d" ] && rm -rf "$W/$f/$d"; done
  du -sh "$W/$f" | cut -f1 | tr '\n' ' '; echo "$f"
done
df -k /System/Volumes/Data | tail -1 | awk '{printf "free %.1f GiB\n",$4/1048576}'