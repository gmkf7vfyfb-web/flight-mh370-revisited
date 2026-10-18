
import struct, sys, os
# reduce snapshot binary (88-byte records, 9 times) to: u8 rel, env, class, fate + f32 lon/lat at time idx 4..7
src, dst, ntimes = sys.argv[1], sys.argv[2], 9
R = 16 + 8*ntimes
with open(src,'rb') as f, open(dst,'wb') as g:
    while True:
        b = f.read(R*65536)
        if not b: break
        out = bytearray()
        for i in range(0, len(b), R):
            r = b[i:i+R]
            out += r[0:4] + r[16+8*4:16+8*8]
        g.write(out)
print('reduced', os.path.getsize(src)//R, 'records')
