import matplotlib.pyplot as plt 
import math
import numpy as np 

colors=['purple', 'crimson', 'forestgreen', 'pink', 'crimson', 'magenta', 'indigo', 'limegreen', 'blueviolet', 'plum', 'purple', 'hotpink', 'mediumseagreen', 'springgreen', 'aquamarine', 'turquoise', 'aqua', 'mediumslateblue', 'orchid', 'deeppink', 'darkturquoise', 'teal', 'mediumslateblue']
markers = [ 'o', '^', 's' ]

fig= plt.figure(figsize=(8,6))
ax = fig.add_subplot(111)
Resolutions= {}
measuredHits = {}
predictedTracks = {}
with open("HitResolutionValues_Centimetres_ALCARECO.txt") as f:
    for line in f:
        for idx in range(1, 4):
            vals= line.split()
            if 'Layer' in line:
                continue
            res  = float(vals[1])*10000
            if "TIB_L%s"%idx in vals[0]: 
                plt.scatter( 1., res, color=colors[idx], marker=markers[idx-1], label='cluster width = %s'%idx)
            elif "TOB_L%s"%idx in vals[0]:
                plt.scatter( 2., res, color=colors[idx], marker=markers[idx-1])
ax.set_xticks(np.arange(2))
ax.set_xticklabels(["TIB 1-3", "TOB 1-3 "], rotation=20., fontsize=8)
plt.ylabel(r'SiStrip Hit Resolution. $(\mu m)$', fontsize=12.)
plt.legend()
plt.title('CMS Preliminary', fontsize=12., loc='left')
plt.title(r'$31.93 fb^{-1}$ (2018D, 13TeV)', fontsize=12., loc='right')
plt.ylim(0., 70.)
fig.savefig('position_and_error_paramteristation_overModules.png')
plt.gcf().clear()
