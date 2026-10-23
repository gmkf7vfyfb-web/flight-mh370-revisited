import json
fr = host.frames()
print(type(fr), len(fr) if hasattr(fr,'__len__') else '')
# find shape
sample = fr[0] if isinstance(fr, list) else fr
print(str(sample)[:600])
