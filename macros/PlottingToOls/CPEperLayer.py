import matplotlib.pyplot as plt 
import math
import numpy as np 
import glob
import os.path
import yaml
import argparse

def Plot_SiStripCPEvalues(path=None, plotperlayer_TIB_TOB =False, plotperClusterWidth_TIB_TOB=False, plotResolution_TIB_TOB_TID_TEC=False, plotperRing_TID_TEC=False):
    
    colors=['cyan', 'blue', 'purple', 'aquamarine', 'crimson', 'turquoise', 'forestgreen', 'pink', 'magenta', 'indigo', 'limegreen', 'blueviolet', 'plum', 'purple', 'hotpink', 'mediumseagreen', 'springgreen', 'aquamarine', 'turquoise', 'aqua', 'mediumslateblue', 'orchid', 'deeppink', 'darkturquoise', 'teal', 'mediumslateblue']
    markers = [ 'o', '^', 's' , '*', 'H', '+', '4']
    
    analysisCfgs =os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "analysis.yml")
    with open(analysisCfgs,"r") as file:
        ymlConfiguration = yaml.load(file, Loader=yaml.FullLoader)
    
    for smp, cfg in ymlConfiguration["samples"].items():
        
        fig= plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        
        for unit in ["Centimetres", "PitchUnits"]:
            
            hitreso_values = os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "outputs", smp, "HitResolutionValues", "HitResolutionValues_{}_ALCARECO.txt".format(unit))
            
            if not os.path.exists(hitreso_values):
                continue
            
            era = cfg['era']
            isMc = True if cfg['type']=='mc' else False
            
            plots_dir = os.path.join(path, "plots")
            if not os.path.exists(plots_dir):
                os.makedirs(plots_dir)
    
            with open(hitreso_values) as f:
                pos = 0. 
                for line_nbr, line in enumerate(f):
                        
                    if 'Layer' in line:
                        continue

                    factor = 10000 if unit=="Centimetres" else (1.)
                    vals= line.split()
                    idx = int(vals[0].split("_L")[-1]) if "_L" in vals[0] else (None)
                    idx_ = int(vals[0].split("_R")[-1]) if "_R" in vals[0] else (None)
                    
                    res  = float(vals[1])*factor
                    cpe_parametrisation = float(vals[-1])*factor
                    err = float(vals[5])*factor

                    ###########################################
                    if plotperlayer_TIB_TOB:
                        suffix = "TIB-TOB_L1-4"
                        for i in range(1, 5):
                            if "TIB_L%s"%i in vals[0]: 
                                plt.scatter( 1., res, color=colors[i], marker=markers[i-1], label='cluster width = %s'%i)
                                #plt.errorbar(1., res, yerr=err)
                            elif "TOB_L%s"%i in vals[0]:
                                plt.scatter( 2., res, color=colors[i], marker=markers[i-1])
                                #plt.errorbar(2., res, yerr=err)
                        ax.set_xticks([1., 2.])
                        ax.set_xticklabels(["TIB 1-4", "TOB 1-4"], rotation=20., fontsize=8)
                    
                    ###########################################
                    if plotperClusterWidth_TIB_TOB:
                        suffix = "perClusterWidth_TIB-TOB"
                        if "TIB_L" in line:
                            plt.scatter( float(idx), res, color='limegreen', marker='s', label="TIB Layer1-4" if idx ==1 else "")
                        elif "TOB_L" in line:
                            plt.scatter( float(idx), res, color='magenta', marker='o', label="TOB Layer1-6" if idx ==1 else "")
                    
                    ###########################################
                    if plotResolution_TIB_TOB_TID_TEC:
                        suffix = "for-TIB-TOB-TID-TEC"
                        if "_All" in line:
                            plt.scatter( float(pos+1.), res, color='blue', marker='s', label="Pair Method" if "TIB" in line else "")
                            plt.scatter( float(pos+1.), cpe_parametrisation, color='red', marker='s', label="ULegacy Parametrization" if "TIB" in line else "")
                            pos += 1
                        ax.set_xticks([1., 2., 3., 4.])
                        ax.set_xticklabels(["TIB", "TOB", "TID", "TEC"], rotation=20., fontsize=8)
                                            
                    ###########################################
                    if plotperRing_TID_TEC:
                        suffix = "TID-TEC_R1-7"
                        if "TID_R" in line:
                            plt.scatter( float(idx_), res, color='purple', marker='s', label="TID Ring1-3" if idx_ ==1 else "")
                        elif "TEC_R" in line:
                            plt.scatter( float(idx_), res, color='aquamarine', marker='s', label="TEC Ring1-7" if idx_ ==1 else "")
           
            ylabel = r'SiStrip Hit Resolution. $(\mu m)$' if unit == "Centimetres" else ( r'SiStrip Hit Resolution. (pitch units)')
            plt.ylabel(ylabel, fontsize=12.)
            plt.legend(loc="upper left")
            plt.title('CMS Preliminary', fontsize=12., loc='left')
            titleName = r'$31.93 fb^{-1}$ (%s, 13TeV)'%(smp.split('_')[-1]) if not isMc else( r'(%s, 14TeV)'%smp.split('_14')[0])
            plt.title('%s'%(titleName), fontsize=10., loc='right')
            plt.ylim(0., 80.)
            pName = '{}/hit_resolution_{}_{}_{}.png'.format(plots_dir, smp, suffix, unit)
            fig.savefig(pName)
            plt.gcf().clear()
            print(" plots can be found in : {}".format(pName))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--path', required=True, help='slurm output dir ')
    options = parser.parse_args()
    Plot_SiStripCPEvalues(path=options.path, plotperlayer_TIB_TOB =True, plotperClusterWidth_TIB_TOB=False, plotResolution_TIB_TOB_TID_TEC=False, plotperRing_TID_TEC=False)
    Plot_SiStripCPEvalues(path=options.path, plotperlayer_TIB_TOB =False, plotperClusterWidth_TIB_TOB=True, plotResolution_TIB_TOB_TID_TEC=False, plotperRing_TID_TEC=False)
    Plot_SiStripCPEvalues(path=options.path, plotperlayer_TIB_TOB =False, plotperClusterWidth_TIB_TOB=False, plotResolution_TIB_TOB_TID_TEC=True, plotperRing_TID_TEC=False)
    Plot_SiStripCPEvalues(path=options.path, plotperlayer_TIB_TOB =False, plotperClusterWidth_TIB_TOB=False, plotResolution_TIB_TOB_TID_TEC=False, plotperRing_TID_TEC=True)
