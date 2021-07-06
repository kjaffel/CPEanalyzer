#!/usr/bin/python
import os, os.path
import sys
import glob
import yaml
import datetime
import argparse
import collections
import shutil
import subprocess
from pprint import pprint
from os import path, listdir
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
    print(" Add colours to the output of Python logging module via : https://pypi.org/project/colorlog/")
    pass

# WIP : not sure anymore if I want to use plotIt for CPE
def update_plotItFiles(data= None, era= None, rootf= None):
    data.update( {"{}:".format(rootf): {
            "type": "data",
            "legend": "data",
            "group": "data",
            "era": era,
            } })
    return data

def list_dir(thisDir):
    subdir =[]
    ls_cmd = ["xrdfs", "root://eoscms.cern.ch", "ls", thisDir]
    try :
        subprocess.check_call(ls_cmd, stdout=subprocess.PIPE)
        subdir = subprocess.check_output(ls_cmd).split('\n')
        subdir = filter(None, subdir)
    except subprocess.CalledProcessError:
        logger.error("Failed to run {0}".format(" ".join(ls_cmd)))
    return subdir

def mapDir(prefix, directory):
    thisDir = path.join(prefix, directory)
    childMap = {}
    contents = []
    for child in list_dir(thisDir):
        if path.join(thisDir, child).endswith('.root'): # path.isfile
            contents.append(child)
        else:
            contents.append(mapDir(thisDir, child)) # path.isdir
    childMap[directory] = contents
    return childMap

def makeFileList(prefix, dirMap):
    fileList = []
    for key in dirMap.keys():
        for child in dirMap[key]:
            if type(child) is str:
                fileList.append(path.join(prefix, path.join(key, child)))
            elif type(child) is dict:
                for subdirFile in makeFileList(path.join(prefix, key), child):
                    fileList.append(subdirFile)
    return fileList

def getFileList(dirName):
    pprint (mapDir(dirName, dirName))
    return makeFileList(dirName, mapDir(dirName, dirName))


def getTasks(task = None, analysisCfgs=None, cmsswDir=None, stageoutDir=None, isTest=False):
    
    files_ = []
    inputParams = []
    filesParams_persmp = []
    data = collections.defaultdict(dict)
    
    with open(analysisCfgs,"r") as file:
        ymlConfiguration = yaml.load(file)

    for smp, cfg in ymlConfiguration["samples"].items():
        if not smp.startswith("SiStripCalZeroBias_") and not smp.startswith("SiStripCalCosmics_") and not smp.startswith("SiStripCalMinBias_"):
            logger.error("The sample names in Yaml file : {} should start by one of these suffix : [SiStripCalZeroBias_ , SiStripCalCosmics_, SiStripCalMinBias_ ] , since it is used later as anInputTagName in process.TrackRefitterP5.clone(src=cms.InputTag(InputTagName)) ".format(analysisCfgs))
            continue
        
        update_plotItFiles(data = data, era=cfg["era"], rootf="{}.root".format(smp))
        
        if isTest:
            outputdir_Persmp = os.path.join(stageoutDir, "outputs", "%s"%smp)
            if not os.path.exists(outputdir_Persmp):
                os.makedirs(outputdir_Persmp)
            filesParams_persmp.append([cfg["db"], os.path.join(outputdir_Persmp, "output_0.root"), task, "--sample=%s"%outputdir_Persmp])
        else:
            try: # to find files on T2 
                files = glob.glob(os.path.join('/storage/data/cms/'+cfg["db"], '*/', '*/', '*/', '*/', '*.root'))
                files_ =[file.replace('/storage/data/cms/','') for file in files]
            except Exception as ex:
                logger.exception("{} root files not found locally ** ".format( files))
                if not os.path.exists("../configs/dascache/{}.dat".format(smp)):
                    logger.exception("searching files using root://eoscms.cern.ch ** ".format( files))
                    #/eos/cms/store/express/Run2018A/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/*/*/*/*/*.root
                    ls_cmd = ["xrdfs", "root://eoscms.cern.ch", "ls", cfg["db"]]
                    try:
                        subprocess.check_call(ls_cmd, stdout=subprocess.PIPE) 
                        print( "dirName to get file list:", subprocess.check_output(ls_cmd).split('\n'))
                        files_ = getFileList(subprocess.check_output(ls_cmd).replace('\n', ''))
                        pprint( 'Files List : ', files_)
                    except subprocess.CalledProcessError:
                        logger.error("Failed to run {0}".format(" ".join(ls_cmd)))
                    
                    with open('../configs/dascache/{}.dat', 'w') as outfile:
                            outfile.writelines("%s\n" % f for f in files_)
                else:
                    # open file and read the content in a list
                    logger.debug(" dascache is found for sample {} , so the files in dascache/{}.dat will be used , if you want to catch changes you made in the configs/yaml . please remove the dascache ! " .format(smp, smp ))
                    with open('../configs/dascache/{}.dat'.format(smp), 'r') as filehandle:
                        files_ = [f.rstrip() for f in filehandle.readlines()]
            
            filesPerJob = cfg["split"]
            sliced = [files_[i:i+filesPerJob] for i in range(0,len(files_),filesPerJob)]
            outputdir_Persmp = os.path.join(stageoutDir, "outputs", "%s"%smp)
            if not os.path.exists(outputdir_Persmp):
                os.makedirs(outputdir_Persmp)
            filesParams_persmp = [ [ ",".join(input), os.path.join(outputdir_Persmp, "output_%s.root"%idx), task, "--sample=%s"%outputdir_Persmp] for idx,input in enumerate(sliced) ]
    
    inputParams = filesParams_persmp
    
    yamlfile = open(os.path.join(stageoutDir, "plotit_files.yml"), "w")
    yaml.dump(data, yamlfile)
    yamlfile.close()
    
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
    parser.add_argument('-o', '--outputdir', action='store', dest='outputdir', type=str, default=None, help='** HistFactory output path')
    parser.add_argument('-y', '--yml', action='store', dest='yml', type=str, default=None, help='** Yml file that include your AlcaReco samples')
    parser.add_argument('--isTest', action='store_true', help='')
    parser.add_argument('--task', action='store', choices= ["skim", "hitresolution"], help='')
    options = parser.parse_args()
    
    if os.path.exists(options.outputdir):
        logger.warning("Output directory {} exists, previous results may be overwritten".format( options.outputdir))
    
    if options.isTest:
        # 1 data & 1 mc sample 
        YmlFile ='../configs/alcareco_localtest.yml'
    else:
        YmlFile = options.yml
    
    print ('slurm Output dir :', options.outputdir)
    print ('yaml input files :', YmlFile)
    
    ClusterParameterEstimator_4SLURM(yml=YmlFile, outputdir= options.outputdir, task=options.task.lower(), isTest = options.isTest) 
