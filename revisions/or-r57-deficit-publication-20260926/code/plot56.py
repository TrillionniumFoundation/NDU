from pathlib import Path
import json
import matplotlib.pyplot as plt
from rational import F
R=Path(__file__).resolve().parents[1]
fig,ax=plt.subplots(figsize=(7.2,4.2))
for seed,style in ((5602,"-"),(5603,"--")):
    row=json.loads((R/f"results/runs/exact-k8-{seed}-t2--price.json").read_text())
    t=[z["seconds"] for z in row["trace"]]
    w=[float(F(z["upper"])-F(z["lower"])) for z in row["trace"]]
    ax.step(t,w,where="post",linestyle=style,label=f"Seed {seed}")
    ax.plot(t[-1],w[-1],marker="o")
ax.set_xlabel("Elapsed optimization time (seconds)")
ax.set_ylabel("Certified absolute value gap")
ax.set_title("Formal rerun: complete exact-target search trajectories")
ax.legend();ax.grid(True,alpha=0.25);fig.tight_layout()
fig.savefig(R/"generated/exact_trajectories.pdf",bbox_inches="tight")
fig.savefig(R/"generated/exact_trajectories.png",dpi=180,bbox_inches="tight")
plt.close(fig)
