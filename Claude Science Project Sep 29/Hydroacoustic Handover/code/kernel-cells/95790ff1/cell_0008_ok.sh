cd repo; python3 - <<'EOF'
import base64,zipfile,io,binascii,zlib,struct
s=''.join(open("Sept 27 2026 backup PL ChatGPT instance/Blackman_2004_extracted_data_2026-09-27.zip.b64").read().split())
N=len(s)+1  # 16584
L=N//4*3-2
pre=base64.b64decode(s[:len(s)//4*4])          # aligned from start
suf_s='A'+s                                      # right-aligned
suf=base64.b64decode(suf_s)                      # bytes after missing char correct
assert len(suf)==L
# parse central directory from suffix
eocd=suf.rfind(b'PK\x05\x06'); n,cdsize,cdoff=struct.unpack('<HII',suf[eocd+10:eocd+20])
p=cdoff; ents=[]
for _ in range(n):
    sig,=struct.unpack('<I',suf[p:p+4]); assert sig==0x02014b50
    crc,csz,usz,fnl,exl,cml=struct.unpack('<IIIHHH',suf[p+16:p+34]); off,=struct.unpack('<I',suf[p+42:p+46])
    name=suf[p+46:p+46+fnl].decode(); ents.append((off,crc,csz,name)); p+=46+fnl+exl+cml
def chk(buf,off,crc,csz):
    fnl,exl=struct.unpack('<HH',buf[off+26:off+30]); d=buf[off+30+fnl+exl:off+30+fnl+exl+csz]
    try: return zlib.crc32(zlib.decompress(d,-15))==crc
    except Exception: return False
for off,crc,csz,name in ents:
    print(name, off, csz, 'pre',chk(pre,off,crc,csz) if off+csz<len(pre) else None, 'suf',chk(suf,off,crc,csz))
EOF