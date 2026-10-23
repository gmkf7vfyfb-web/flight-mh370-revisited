
def utcsec(df, ref):
    return (pd.to_datetime(df.utc, format='ISO8601')-pd.Timestamp(ref)).dt.total_seconds().values
plt.close('all')
exec(open('/dev/stdin').read()) if False else None
