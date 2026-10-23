
r = host.mcp("google-drive", "read_file_content", fileId="1Rt_YubXmhk94Gd8M_C11B-s8I5x71fs9")
print(r if isinstance(r,str) else json.dumps(r)[:1500])
m = host.mcp("google-drive", "get_file_metadata", fileId="1Dfbfp4hdT97qyw4SHcI6_MPFCkCkVp2e")
print(json.dumps(m)[:400])
