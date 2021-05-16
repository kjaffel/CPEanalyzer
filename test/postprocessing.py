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
    # https://pypi.org/project/colorlog/
    pass
import os
import os.path
import subprocess
import batch_slurm
from collections import defaultdict
import argparse
import glob 
import yaml
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
    print os.environ["CMSSW_BASE"] 
    analysisCfgs = os.path.join("/nfs/scratch/fynu/kjaffel/CPEanalyzer/CMSSW_11_2_2_patch1/src/SiStripCPE/CPEanalyzer/test", workdir, "analysis.yml")
    tsk_path = os.path.join("/nfs/scratch/fynu/kjaffel/CPEanalyzer/CMSSW_11_2_2_patch1/src/SiStripCPE/CPEanalyzer/test", workdir,"outputs")
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
            print ("outputs = ", outputs, "id_noOut = ", id_noOut)
            if id_noOut:
                logger.error("Missing outputs for subjobs {0}, so no postprocessing will be run".format(", ".join(str(sjId) for sjId in id_noOut)))
                if hasattr(batch_slurm, "getResubmitCommand"):
                    resubCommand = " ".join(batch_slurm.getResubmitCommand(batchDir, id_noOut))
                    logger.info("Resubmit with '{}' (and possibly additional options)".format(resubCommand))
                return
            
            aProblem = False
            for tsk in tasks_notfinalized:
                nExpected, tskOut = outputs[tsk.name]
                if not tskOut:
                    logger.error("No output files for sample {}".format(tsk.name))
                    aProblem = True
                tskOut_by_name = defaultdict(list)
                for fn in tskOut:
                    tskOut_by_name[os.path.basename(fn)].append(fn)
                print( tskOut_by_name ,"tskOut_by_name")
                for outFileName, outFiles in tskOut_by_name.items():
                    if nExpected != len(outFiles):
                        logger.error("Not all jobs for {} produced an output file {} ({:d}/{:d} found), cannot finalize".format(tsk.name, outFileName, len(outFiles), nExpected))
                        aProblem = True
                    else:
                        print( 'outFileName:', outFileName , "outFiles:", outFiles)
                        haddCmd = ["hadd", "-f", os.path.join(resultsdir, "{}.root".format(tsk.name))]+outFiles
                        try:
                            logger.debug("Merging outputs for sample {0} with {1}".format(tsk.name, " ".join(haddCmd)))
                            subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL) 
                        except subprocess.CalledProcessError:
                            logger.error("Failed to run {0}".format(" ".join(haddCmd)))
                            aProblem = True
            if aProblem:
                logger.error("Something went wrong with some of your Jobs ! ")
                return
            else:
                logger.info("All tasks finalized")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RUN CPE FIANLIZE')
    parser.add_argument('--finalize', action='store_true', default=True, help='')
    parser.add_argument('--workdir', required=True, help='')
    options = parser.parse_args()
    FINALIZE_JOBS(workdir=options.workdir, finalize=options.finalize)
