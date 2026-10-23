import numpy as np
print("t_shot span:", cy.t_shot.min(), "to", cy.t_next.max(),
      "=", f"{int(cy.t_shot.min()//3600):02d}:{int(cy.t_shot.min()%3600//60):02d}:{int(cy.t_shot.min()%60):02d}",
      "to", f"{int(cy.t_next.max()//3600):02d}:{int(cy.t_next.max()%3600//60):02d}:{int(cy.t_next.max()%60):02d}")
print("panels:", cy.panel.value_counts().to_dict())
for p, grp in cy.groupby("panel"):
    print(f"  panel {p}: {len(grp):3d} cycles  {int(grp.t_shot.min()//3600):02d}:{int(grp.t_shot.min()%3600//60):02d}:{int(grp.t_shot.min()%60):02d}"
          f" - {int(grp.t_next.max()//3600):02d}:{int(grp.t_next.max()%3600//60):02d}:{int(grp.t_next.max()%60):02d}")
print("\nshots after 01:12 :", int((cy.t_shot>=4320).sum()), " after 01:14:29 :", int((cy.t_shot>=4*3600/4+ 3600+14*60+29-3600).sum()))
print("predicted arrivals: 01:16:54 =", 1*3600+16*60+54, "s ; 01:19:21 =", 1*3600+19*60+21, "s")
print("max cycle end (s):", cy.t_next.max())
