R=pd.read_csv(O+"h01w_time_discriminant.csv")
print(R[["option","kadri_time_utc","statistic","observed","clipped_fraction_in_window","p_panelc","rank_panelc","n_null_panelc","floor_panelc","p_pooled"]].to_string(index=False))
