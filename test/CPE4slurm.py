#!/usr/bin/python
import os, os.path
import sys
import glob
import yaml
import datetime
import argparse
import shutil
from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

import logging
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
logger = logging.getLogger("CPEAnalyser: algorithm used to determine the position and errors of the CMS Strip clusters")
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
                        },
                secondary_log_colors={},
                style='%'
                )
    stream.setFormatter(formatter)
except ImportError:
    # https://pypi.org/project/colorlog/
    pass

def getTasks(task = None, analysisCfgs=None, cmsswDir=None, stageoutDir=None, isTest=False):
    with open(analysisCfgs,"r") as file:
        ymlConfiguration = yaml.load(file, Loader=yaml.FullLoader)

    for smp, cfg in ymlConfiguration["samples"].items():
        if smp not startswith.("SiStripCalZeroBias_") and not startswith.("SiStripCalCosmics_") and not startswith.("SiStripCalMinBias_"):
            logger.error("The sample names in Yaml file : {} should start by one of these suffix : [SiStripCalZeroBias_ , SiStripCalCosmics_, SiStripCalMinBias_ ] , since it is used later as anInputTagName in process.TrackRefitterP5.clone(src=cms.InputTag(InputTagName)) ".format(analysisCfgs))
            continue
        if isTest:
            outputdir_Persmp = os.path.join(stageoutDir, "outputs", "%s"%smp)
            if not os.path.exists(outputdir_Persmp):
                os.makedirs(outputdir_Persmp)
            inputParams = [[cfg["db"], os.path.join(outputdir_Persmp, "output_1.root"), task, "--sample=%s"%outputdir_Persmp]]
        else:
            try: 
                files = glob.glob(os.path.join('/storage/data/cms/'+cfg["db"], '*/', '*/', '*/', '*/', '*.root'))
            except Exception as ex:
                logger.exception("{} root files not found ** ".format( files))
            filesPerJob = cfg["split"]
            files_=[file.replace('/storage/data/cms/','') for file in files]
            sliced = [files_[i:i+filesPerJob] for i in range(0,len(files_),filesPerJob)]
            outputdir_Persmp = os.path.join(stageoutDir, "outputs", "%s"%smp)
            if not os.path.exists(outputdir_Persmp):
                os.makedirs(outputdir_Persmp)
            inputParams = [ [ ",".join(input), os.path.join(outputdir_Persmp, "output_%s.root"%idx), task, "--sample=%s"%smp] for idx,input in enumerate(sliced) ]
    return inputParams 

def ClusterParameterEstimator_4SLURM(yml=None, outputdir= None, task=None, isTest=False):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(config.cmsswDir, outputdir) 
    config.sbatch_time = '0-02:00'
    config.sbatch_memPerCPU = '2000'
    config.batchScriptsFilename ="slurmSubmission.sh" 
    #config.environmentType = 'cms'
    config.inputSandboxContent = ["skimProducer.py" if task=="skim" else("SiStripHitResol.py" if task=="hitresolution" else("CPEstimator.py"))]
    config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ["inputFiles","outputFile", "task","sample"]
    
    analysisCfgs = os.path.join(config.cmsswDir, yml)
    config.inputParams = getTasks (task=task, analysisCfgs=analysisCfgs, cmsswDir=config.cmsswDir, stageoutDir=config.stageoutDir, isTest=isTest) 
    shutil.copyfile(analysisCfgs, config.stageoutDir+"/analysis.yml")
    config.payload = \
    """
    echo ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
    if [[ "$task" == *"skim"* ]]; then
        cmsRun skimProducer.py inputFiles=${inputFiles} outputFile=${outputFile}
    elif [[ "$task" == "hitresolution" ]]; then
        cmsRun SiStripHitResol.py inputFiles=${inputFiles} outputFile=${outputFile}
    else
        cmsRun CPEstimator.py inputFiles=${inputFiles} outputFile=${outputFile}
    fi
    """
    
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()
    logger.warning('Work still in progress for better workflow ...\n'
                   'To hadd files and produce plots. Please run as follow when the jobs finish running\n'
                   'python postprocessing.py --workdir {}\n'
                   'squeue -u user_name  : allows you to check your submitted jobs status\n'.format(outputdir))

    
if __name__ == '__main__':
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    parser = argparse.ArgumentParser(description='RUN CPE ANALYSER')
    parser.add_argument('-o', '--outputdir', action='store', dest='outputdir', type=str, default=os.makedirs("." + current_time), help='** HistFactory output path')
    parser.add_argument('-y', '--yml', action='store', dest='yml', type=str, default=None, help='** Yml file that include your AlcaReco samples')
    parser.add_argument('--isTest', action='store_true', help='')
    parser.add_argument('--task', action='store', choices= ["skim", "hitresolution"], help='')
    options = parser.parse_args()
   
    if os.path.exists(options.outputdir):
        logger.warning("Output directory {} exists, previous results may be overwritten".format( options.outputdir))
    if options.isTest:
        YmlFile ='../configs/alcareco_2018DExpress_localtest.yml'
    else:
        YmlFile = options.yml
    print ('slurm Output dir :', options.outputdir)
    print ('yaml input files :', YmlFile)
    
    ClusterParameterEstimator_4SLURM(yml=YmlFile, outputdir= options.outputdir, task=options.task.lower(), isTest = options.isTest) 
