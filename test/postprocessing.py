import sys
sys.dont_write_bytecode=True

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
    print(" Add colours to the output of Python logging module via : https://pypi.org/project/colorlog/")
    pass

import os, os.path
import ROOT
import subprocess
import batch_slurm
import argparse
import glob 
import yaml
from pprint import pprint
from collections import defaultdict
from functools import partial

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

def FINALIZE_JOBS(workdir='', finalize=False):
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

def RUN_PLOTTER(workdir=None):
    ROOT.gROOT.ProcessLine(".L ../macros/Resolutions.cc")
    units = {'pitch':0 }#, 'cm':1} 
    compaigns = {'PreLegacy':0}#, 'ULegacy':1}
    for k1 in compaigns.keys():
        for idx, k2 in enumerate(units.keys()):
            dircreated = False 
            for rootfile in glob.glob(os.path.join(workdir, 'outputs','*.root')): 
                rootpath = rootfile.replace('.root', '')
                try:
                    logger.debug("Resolution from 1D gaussian fit for {} compaign in {} units :".format(k1, k2) )
                    logger.debug(" for file : {}".format( rootfile))
                    ROOT.Resolutions(units[k2], compaigns[k1], rootfile, rootpath, dircreated)
                    dircreated = True
                except subprocess.CalledProcessError:
                    logger.error("Failed to run .L ../macros/Resolutions.cc with : {0}".format(" ".join(rootfile)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RUN CPE FIANLIZE')
    parser.add_argument('--finalize', action='store_true', default=True, help='')
    parser.add_argument('--workdir', required=True, help='')
    
    options = parser.parse_args()
    
    FINALIZE_JOBS(workdir=options.workdir, finalize=options.finalize)
    
    RUN_PLOTTER(workdir=options.workdir)
