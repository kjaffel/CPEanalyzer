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
logger = logging.getLogger("CPEAnalyser->TreeProducer")

current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
parser = argparse.ArgumentParser(description='Alignment Position Error (APE) Estimator ')
parser.add_argument('-o', '--outputdir', action='store', dest='outputdir', type=str, default=os.makedirs("." + current_time), help='** HistFactory output path')
parser.add_argument('-y', '--yml', action='store', dest='yml', type=str, default=None, help='** Yml file that include your AlcaReco samples')
    
global options 
options = parser.parse_args()
config = Configuration()

if os.path.exists(options.outputdir):
    logger.warning("Output directory {} exists, previous results may be overwritten".format( options.outputdir))

print ('slurm Output dir :', options.outputdir)
print ('yaml input files :', options.yml)

config.sbatch_partition = 'cp3'
config.sbatch_qos = 'cp3'
#config.cmsswDir = '/home/ucl/cp3/kjaffel/scratch/CPEanalyzer/CMSSW_10_2_6/src'
config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
config.sbatch_chdir = os.path.join(config.cmsswDir, options.outputdir ) 
config.sbatch_time = '0-02:00'
sbatch_memPerCPU = '2000'
#config.environmentType = 'cms'
config.inputSandboxContent = ["CPE4slurm.py"]
config.stageoutFiles = ['*.root']
config.stageoutDir = config.sbatch_chdir
config.inputParamsNames = ["inputfile","outputfile"]
#yaml_path = os.path.join(config.cmsswDir, '/SiStripCPE/CPEanalyzer/test/alcareco_2018analysis.yml')
print(config.cmsswDir)
yaml_path = os.path.join(config.cmsswDir, options.yml)
with open(yaml_path,"r") as file:
    ymlConfiguration = yaml.load(file)#,Loader=yaml.FullLoader)
    print ( ymlConfiguration ) 
for smp, cfg in ymlConfiguration["samples"].items():
    print (smp, ':', cfg["db"])
    try: 
        #files = glob.glob(os.path.join(cfg["db"], '*/', '*/', '*/', '*/', '*.root'))
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
cmsRun CPE4slurm.py inputFiles=${inputfile} outputFile=${outputfile}

"""
print("Submitting job...")
submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
submitWorker()

#if self.status == Jobs_still_Running



print("Done")
