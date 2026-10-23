f=host.frames(frame_id="1f938cf5-20bc-4aee-ba61-9768284cbcb2", offset=195)
msgs=f.get('messages') if isinstance(f,dict) else None
s=str(f); print(s[-2500:])