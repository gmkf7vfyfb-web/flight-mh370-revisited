a = host.artifacts(filename="ga_search_and_rescue_search_area_2014.geojson")
print([(x.get('filename'), x.get('version_id')) for x in (a if isinstance(a,list) else a.get('artifacts',[]))][:3])
import subprocess
print(subprocess.run("cd 'repo/r/Claude Science Project Sep 29' && ls engine/data | head -50; find . -iname '*arc*' \\( -name '*.csv' -o -name '*.geojson' \\) | grep -v node_modules | head -20", shell=True, capture_output=True, text=True).stdout)