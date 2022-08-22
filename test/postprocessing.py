import sys
import os, os.path
sys.dont_write_bytecode=True
import ROOT
import subprocess
import batch_slurm
import argparse
import glob 
import yaml
import numpy as np

from pprint import pprint
from collections import defaultdict
from functools import partial

import logging
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
logger = logging.getLogger("CPEFINALIZE")
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)
try:
    import colorlog
    from colorlog import ColoredFormatter
    formatter = ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                        'DEBUG':    'cyan',
                        'INFO':     'green',
                        'WARNING':  'blue',
                        'ERROR':    'red',
                        'CRITICAL': 'red',
                        'CRITICAL': 'red',
                        },
                secondary_log_colors={},
                style='%'
                )
    stream.setFormatter(formatter)
except ImportError:
    print(" You can add colours to the output of Python logging module via : https://pypi.org/project/colorlog/")
    pass

class SampleTask:
    def __init__(self, name, inputFiles=None, outputFile=None, config=None):
        self.name = name
        self.inputFiles = inputFiles
        self.outputFile = outputFile
        self.config = config

def getTasks(analysisCfgs=None):
    tasks = []
    print( analysisCfgs )
    with open(analysisCfgs,"r") as file:
        ymlConfiguration = yaml.load(file, Loader=yaml.FullLoader)
    for sName, sConfig in ymlConfiguration["samples"].items():
        tasks.append(SampleTask(sName, outputFile="{}.root".format(sName), config=sConfig))
    return tasks

def finalize_jobs(workdir='', finalize=False):
    resultsdir = os.path.join(workdir, "outputs")
    cwd = os.getcwd()
    analysisCfgs = os.path.join(cwd, workdir, "analysis.yml")
    tsk_path = os.path.join(cwd, workdir,"outputs")
    if finalize:
        tasks = getTasks(analysisCfgs=analysisCfgs)
        tasks_notfinalized = [ tsk for tsk in tasks if not os.path.exists(os.path.join(resultsdir, tsk.outputFile)) ]
        if not tasks_notfinalized:
            logger.info("All output files were found, so no finalization was redone !")
        else:
            def cmdMatch(ln, smpNm):
                return " --sample={}".format(smpNm) in ln or ln.endswith(" --sample={}".format(smpNm))
            batchDir = workdir #os.path.join(workdir, "batch")
            outputs, id_noOut = batch_slurm.findOutputsForCommands(batchDir,
                    { tsk.name: partial(cmdMatch, smpNm="{}/{}".format(tsk_path, tsk.name)) for tsk in tasks_notfinalized })
            if id_noOut:
                logger.error("Missing outputs for subjobs {0}, so no postprocessing will be run".format(", ".join(str(sjId) for sjId in id_noOut)))
                if hasattr(batch_slurm, "getResubmitCommand"):
                    resubCommand = " ".join(batch_slurm.getResubmitCommand(batchDir, id_noOut))
                    logger.info("Resubmit with '{}' ".format(resubCommand))
                return
            
            aProblem = False
            for tsk in tasks_notfinalized:
                nExpected, tskOut = outputs[tsk.name]
                if not tskOut:
                    logger.error("No output files for sample {}".format(tsk.name))
                    aProblem = True
                tskOut_by_name = defaultdict(list)
                for fn in tskOut:
                    tskOut_by_name[tsk.name].append(fn)
                for outFileName, outFiles in tskOut_by_name.items():
                    if nExpected != len(outFiles):
                        logger.error("Not all jobs for {} produced an output ({:d}/{:d} found), task cannot finalize".format(tsk.name, len(outFiles), nExpected))
                        aProblem = True
                    else:
                        haddCmd = ["hadd", "-f", os.path.join(resultsdir, "{}.root".format(tsk.name))]+outFiles 
                        try:
                            logger.debug("Merging outputs for sample {0} with {1}".format(tsk.name, " ".join(haddCmd)))
                            subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL) 
                        except subprocess.CalledProcessError:
                            logger.error("Failed to run {0}".format(" ".join(haddCmd)))
                            aProblem = True
            if aProblem:
                logger.error("Something went wrong with some of your Jobs, not all tasks are finalized ! ")
                return
            else:
                logger.info("All tasks finalized")

    
units     = {'cm' :1 , 'pitch':0 } #, pitch =0 / cm =1
compaigns = {'pre':0 , 'ul'   :1 } 

categories= { 
            # 'cat1':  """(clusterW1 == clusterW2) && clusterW1 == {clw} && clusterW2 == {clw} \n 
            #       && expectedW1 > clusterW1 +2  && expectedW2 > clusterW2 +2""", 
             'cat1':  """(clusterW1 == clusterW2) && clusterW1 == {clw} && clusterW2 == {clw} """,
            # 'cat2':  """(clusterW1 == clusterW2) && clusterW1 == 1 && clusterW2 == 1 \n
            #       && expectedW1 <= {trkw} && expectedW2 <= {trkw}""",
            # 'cat3':  """expectedW1 >= clusterW1 && expectedW2 >= clusterW2 \n
            #       && expectedW1 == {trkw} && expectedW2 == {trkw}""",
            #'cat4':  """ ((- expectedW1 + clusterW1) == 1 || (- expectedW1 + clusterW1) == 2) \n
            #       && ((- expectedW2 + clusterW2) == 1 || (- expectedW2 + clusterW2) == 2) \n
            #       && expectedW1 == {trkw} && expectedW2 == {trkw}""",
            # 'cat5':  """clusterW1 <= 4 && clusterW2 <= 4 \n
            #       && expectedW1 == {trkw} && expectedW2 == {trkw}""", 
            # 'cat6':"""( ( abs(driftAlpha) <= {alpham} &&  abs(driftAlpha) >= {alphap} ) 
            #       ||   ( abs(driftAlpha_2) <= {alpham} && abs(driftAlpha_2) >= {alphap} ) ) \n"""
            # 'cat6':""" (abs(driftAlpha) == {alpha} || abs(driftAlpha_2) == {alpha}) \n""",
            #  'cat7':""" (clusterW1 == clusterW2) && (N1uProj == {afp} || N1uProj == {afp}) \n
            #        && (clusterW1 <= 4 && clusterW2 <= 4)""",
        }
    
fit_rngs = { 
            'cat1': { 'cluster_w': np.arange(1, 5), 'track_w': 'cat1' },
                #'HC': { 'cluster_w': np.arange(5, 10), 'track_w': 'cat1' },
                #'LC': { 'cluster_w': np.arange(1, 5), 'track_w': 'cat1' }
            'cat2': { 'cluster_w': 'cat2', 'track_w': np.arange(0.2, 1., 0.2) },
            'cat3': { 'cluster_w': 'cat3', 'track_w': np.arange(1.1, 5., 4.) },
            'cat4': { 'cluster_w': 'cat4', 'track_w': np.arange(0.2, 3., 0.2) },
            'cat5': { 'cluster_w': 'cat5', 'track_w': np.arange(0.2, 4., 0.2) },
            'cat6': { 'cluster_w': 'cat6', 'track_w': np.arange(0., 0.1, 0.01) },
            'cat7': { 'cluster_w': 'cat7', 'track_w': np.arange(0., 1.6, 0.25) },
        }
    
def runPlotter(workdir, run):
    ROOT.gROOT.ProcessLine(".L ../macros/Resolutions.cc")
    
    for cat, cut in categories.items():
        for idx, k2 in enumerate(units.keys()):
            
            dir_created = False 
            for rf in glob.glob(os.path.join(workdir, 'outputs','*.root')): 
                
                rp = rf.replace('.root', '')
                if 'readwithJSROOT' in rp: continue
                
                wFix = 'cluster_w' if cat != 'cat1' else 'track_w'
                wVar = 'cluster_w' if cat == 'cat1' else 'track_w'
                for w in fit_rngs[cat][wVar]:
                    if not cat in ['cat1', 'cat6', 'cat7']:
                        trkw = round(w, 2)
                        clw  = fit_rngs[cat]['cluster_w']
                        cluster_cut = cut.format(trkw=trkw)
                    elif cat == 'cat6':
                        alpha  = w
                        alpham = alpha - 0.01
                        alphap = alpha
                        trkw  = 'None_driftalpha{}'.format(alpha)
                        clw   = 'cat6'
                        #cluster_cut = cut.format(alpham=alpham, alphap=alphap)
                        cluster_cut = cut.format(alpha=alpha)
                    elif cat == 'cat7':
                        afp  = w
                        trkw = 'None_afp{}'.format(afp)
                        clw  = 'cat7'
                        cluster_cut = cut.format(afp=afp)
                    else:
                        trkw = fit_rngs[cat]['track_w']
                        clw  = w
                        cluster_cut = cut.format(clw=clw)

                    cltrk_w = '_clusterW{}_trackW{}'.format(clw, str(trkw).replace('.', 'p'))
                    try:
                        logger.debug("Resolution from 1D gaussian fit for {}Legacy compaign in {} units :".format(run, k2) )
                        logger.debug(" for file : {}".format( rf))
                        logger.debug(" cut = {}".format(cluster_cut))
                        ROOT.Resolutions(units[k2], compaigns[run], rf, rp, cltrk_w, cluster_cut, False)
                        dir_created = True
                    except subprocess.CalledProcessError:
                        logger.error("Failed to run .L ../macros/Resolutions.cc with : {0}".format(" ".join(rf)))

    for f in ['CutFlowReports', 'HitResolutionValues', 'GaussianFits']:
        dir_ = os.path.join(workdir,'results', f)
        if not os.path.isdir(dir_):
            os.makedirs(dir_)
        try:
            cmd = ['mv', './'+ f +'_*', dir_ ]
            subprocess.check_call(" ".join(cmd), shell=True)
        except:
            logger.error("Failed to run {0}".format(" ".join(cmd)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RUN CPE FIANLIZE')
    parser.add_argument('--finalize', action='store_true', default=True, help='Will hadd the finialized outputs first')
    parser.add_argument('--workdir', required=True, help='slurm output dir')
    parser.add_argument('--run', required=True, choices= ['ul', 'pre'], help='stand for the compaigns, ul is ULegacy and pre is PreULegacy')
    
    options = parser.parse_args()
    
    finalize_jobs(workdir=options.workdir, finalize=options.finalize)
    
    runPlotter(workdir=options.workdir, run=options.run)
