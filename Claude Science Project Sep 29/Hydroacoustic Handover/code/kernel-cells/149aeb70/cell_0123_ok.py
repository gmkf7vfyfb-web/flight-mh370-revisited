import matplotlib.pyplot as plt; plt.close("all")
exec(open("make_h08s_fig.py").read())
print("largest pair dt actually tested:", kp.dt_s.max(), "s -> 00:52:03 +", round(kp.dt_s.max()), "s =",
      f"{int((3123+kp.dt_s.max())//3600):02d}:{int((3123+kp.dt_s.max())%3600//60):02d}:{int((3123+kp.dt_s.max())%60):02d}")
