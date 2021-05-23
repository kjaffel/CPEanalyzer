import matplotlib.pyplot as plt 
import math
import numpy as np 
import glob
import os.path
import yaml
import argparse

def Cluster_parameter_estimator_values(path=None):
    fig= plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    Resolutions= {}
    measuredHits = {}
    predictedTracks = {}
    colors=['purple', 'crimson', 'forestgreen', 'pink', 'crimson', 'magenta', 'indigo', 'limegreen', 'blueviolet', 'plum', 'purple', 'hotpink', 'mediumseagreen', 'springgreen', 'aquamarine', 'turquoise', 'aqua', 'mediumslateblue', 'orchid', 'deeppink', 'darkturquoise', 'teal', 'mediumslateblue']
    markers = [ 'o', '^', 's' ]
    
    analysisCfgs =os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "analysis.yml")
    with open(analysisCfgs,"r") as file:
        ymlConfiguration = yaml.load(file, Loader=yaml.FullLoader)
    
    for smp, cfg in ymlConfiguration["samples"].items():
        hitreso_values = os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "outputs", smp, "HitResolutionValues", "HitResolutionValues_Centimetres_ALCARECO.txt")
        era = cfg['era']
        plots_dir = os.path.join(path, "plot_run{}".format(era))
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)

        with open(hitreso_values) as f:
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
        plt.title(r'$31.93 fb^{-1}$ (%s, 13TeV)'%(smp.split('_')[-1]), fontsize=12., loc='right')
        plt.ylim(0., 70.)
        fig.savefig('{}/hit_resolution_{}.png'.format(plots_dir, smp))
        plt.gcf().clear()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--path', required=True, help='slurm output dir ')
    options = parser.parse_args()
    Cluster_parameter_estimator_values(path=options.path)
