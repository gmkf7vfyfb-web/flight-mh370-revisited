cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-digitisation/sources/; cat PMC11065988.oa.xml; echo; ls -la PMC11065988 | head -120; python -c "
from PIL import Image;import glob
for f in sorted(glob.glob('PMC11065988/*.jpg'))[:40]:
    im=Image.open(f);print(f,im.size)
"