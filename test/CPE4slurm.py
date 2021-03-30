#!/usr/bin/python
import os, os.path
import sys
import glob
import yaml
import datetime
import argparse

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

import logging
logger = logging.getLogger("CPEAnalyser: algorithm used to determine the position and errors of the CMS Strip clusters")

def ClusterParameterEstimator_4SLURM(yml=None, outputDIR= None, task=None, isTest=False):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(config.cmsswDir, options.outputdir ) 
    config.sbatch_time = '0-02:00'
    sbatch_memPerCPU = '2000'
    #config.environmentType = 'cms'
    config.inputSandboxContent = ["skimProducer.py" if task=="skim" else("SiStripHitResol.py" if task=="HitResol" else("CPEstimator.py"))]
    config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ["inputfile","outputfile"]
    
    yaml_path = os.path.join(config.cmsswDir, options.yml)
    with open(yaml_path,"r") as file:
        ymlConfiguration = yaml.load(file)#,Loader=yaml.FullLoader)
    
    for smp, cfg in ymlConfiguration["samples"].items():
        print (smp, cfg["db"])
        if isTest:
            outputdir_Persmp = os.path.join(config.stageoutDir, "output", "%s"%smp)
            if not os.path.exists(outputdir_Persmp):
                os.makedirs(outputdir_Persmp)
            config.inputParams = [[cfg["db"], os.path.join(outputdir_Persmp, "Output_isTest.root")]]
        else:
            try: 
                files = glob.glob(os.path.join('/storage/data/cms/'+cfg["db"], '*/', '*/', '*/', '*/', '*.root'))
            except Exception as ex:
                logger.exception("{} root files not found ** ".format( files))
            filesPerJob = cfg["split"]
            files_=[file.replace('/storage/data/cms/','') for file in files]
            sliced = [files_[i:i+filesPerJob] for i in range(0,len(files_),filesPerJob)]
            outputdir_Persmp = os.path.join(config.stageoutDir, "output", "%s"%smp)
            if not os.path.exists(outputdir_Persmp):
                os.makedirs(outputdir_Persmp)
            config.inputParams = [ [ ",".join(input), os.path.join(outputdir_Persmp, "Output_%s.root"%idx) ] for idx,input in enumerate(sliced) ]
    
    config.payload = \
    """
    echo ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
    if [ "$task" = "skim" ]; then
        cmsRun skimProducer.py inputFiles=${inputfile} outputFile=${outputfile}
    elif [ "$task" = "HitResol" ]; then
        cmsRun SiStripHitResol.py inputFiles=${inputfile} outputFile=${outputfile}
    else
        cmsRun CPEstimator.py inputFiles=${inputfile} outputFile=${outputfile}
    fi
    """
    
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()
    
if __name__ == '__main__':
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    parser = argparse.ArgumentParser(description='Run Skim Producer')
    parser.add_argument('-o', '--outputdir', action='store', dest='outputdir', type=str, default=os.makedirs("." + current_time), help='** HistFactory output path')
    parser.add_argument('-y', '--yml', action='store', dest='yml', type=str, default=None, help='** Yml file that include your AlcaReco samples')
    parser.add_argument('--isTest', action='store_true', help='')
    parser.add_argument('--task', action='store', choices= ["skim", "HitResol"], help='')
    options = parser.parse_args()
    
    if os.path.exists(options.outputdir):
        logger.warning("Output directory {} exists, previous results may be overwritten".format( options.outputdir))
    if isTest:
        YmlFile ='../configs/alcareco_2018D_localtest.yml'
    else:
        YmlFile = options.yml
    print ('slurm Output dir :', options.outputdir)
    print ('yaml input files :', YmlFile)
    
    ClusterParameterEstimator_4SLURM(yml=YmlFile, outputDIR= options.outputdir, task=options.task, isTest = options.isTest) 
