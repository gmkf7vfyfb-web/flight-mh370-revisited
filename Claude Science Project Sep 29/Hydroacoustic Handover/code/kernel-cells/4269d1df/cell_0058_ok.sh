X=/Users/pete/Downloads/mh370-exchange; ls $X/end-of-flight/; ls $X/end-of-flight/run-j; ls $X/end-of-flight/run-j/summary | head -30; ls $X/end-of-flight/run-j-joined-v2 $X/end-of-flight/run-j-joined-v2/* | head -20; ls $X/core/run-j/; python3 -c "
import json;d=json.load(open('$X/end-of-flight/run-j/summary/table-0019-mixture.json'));print(list(d)[:20]); 
for k in list(d)[:6]: print(k, str(d[k])[:600])
"; python3 -c "import pyproj;print(pyproj.__version__)"