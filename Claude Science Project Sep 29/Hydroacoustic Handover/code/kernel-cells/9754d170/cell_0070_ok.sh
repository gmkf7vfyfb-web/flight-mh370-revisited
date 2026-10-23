ls -la audit/work/sus/; python3 -c "
import pandas as pd; d=pd.read_csv('audit/work/sus/sus_tl.csv'); print(d.groupby(['site','station']).size()); print(d.tail(3).to_string())" 2>&1 | tail -12