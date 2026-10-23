t=docs['jacc/media_interviews_2014_april_tr011.aspx']
i=t.find('of all the hundreds of photos'); print(t[:200]); print(re.findall(r'\d{1,2} April 2014',t)[:3]); print(t[i-200:i+1800])