
q=im[im['quantile'].astype(str).str.startswith('arc033.5S')]
print(q['quantile'].unique()[:5], q.src_depth_m.unique(), q.fc_hz.unique())
print(q[(q.src_depth_m==10)&(q['quantile']=='arc033.5S_+0')][['logger','fc_hz','status','tl_db','ram_grid_covered','min_corridor_depth_m']].to_string())
print(tl[(tl.source_id=='arc033.5S_+0')&(tl.src_depth_m==10)].groupby('receiver').status.agg(lambda s: ','.join(sorted(set(s)))))
