"""
Slurm tools (based on previous condorhelpers and cp3-llbb/CommonTools condorSubmitter and slurmSubmitter)
"""
__all__ = ("CommandListJob", "jobsFromTasks", "makeTasksMonitor", "findOutputsForCommands")

from itertools import chain, count
import logging
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
logger = logging.getLogger("slurm tools")
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)
import os, os.path
import subprocess

from batch import CommandListJob as CommandListJobBase
from batch import TasksMonitor
from pprint import pprint
try:
    from CP3SlurmUtils.Configuration import Configuration as CP3SlurmConfiguration
    from CP3SlurmUtils.ConfigurationUtils import validConfigParams as CP3SlurmConfigValidParams
    from CP3SlurmUtils.SubmitWorker import SubmitWorker as slurmSubmitWorker
except ImportError as ex:
    logger.info("Could not import Configuration and slurmSubmitWorker from CP3SlurmUtils.SubmitUtils. Please run 'module load slurm/slurm_utils'")

SlurmJobStatus = ["PENDING", "RUNNING", "COMPLETED", "FAILED", "COMPLETING", "CONFIGURING", "CANCELLED", "BOOT_FAIL", "NODE_FAIL", "PREEMPTED", "RESIZING", "SUSPENDED", "TIMEOUT", "OUT_OF_MEMORY", "REQUEUED", "unknown"]
SlurmJobStatus_active = ["CONFIGURING", "COMPLETING", "PENDING", "RUNNING", "RESIZING", "SUSPENDED", "REQUEUED"]
SlurmJobStatus_failed = ["FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY"]
SlurmJobStatus_completed = "COMPLETED"

class CommandListJob(CommandListJobBase):
    """
    Helper class to create a slurm job array from a list of commands (each becoming a task in the array)
    
    Default work directory will be $(pwd)/slurm_work, default output pattern is "*.root"
    """
    default_cfg_opts = {
          "batchScriptsFilename" : "slurmSubmission.sh"
        , "stageoutFiles"        : ["*.root"]
        , "inputParamsNames"     : ["taskcmd"]
        , "useJobArray"          : True
        , "payload"              : ("${taskcmd}")
        }

    def __init__(self, commandList, workDir=None, configOpts=None):
        super(CommandListJob, self).__init__(commandList, workDir=workDir, workdir_default_pattern="slurm_work")
        ##
        self.cfg = CP3SlurmConfiguration()

        self.cfg.sbatch_chdir = self.workDir
        self.cfg.inputSandboxDir = self.workDirs["in"]
        self.cfg.batchScriptsDir = self.workDir
        self.cfg.stageoutDir = os.path.join(self.workDirs["out"], "${SLURM_ARRAY_TASK_ID}")
        self.cfg.stageoutLogsDir = self.workDirs["log"]
        self.cfg.inputParams = list([cmd] for cmd in self.commandList)
        ## apply user-specified
        cfg_opts = dict(CommandListJob.default_cfg_opts)
        if configOpts:
            cfg_opts.update(configOpts)
        for k, v in cfg_opts.items():
            if k not in CP3SlurmConfigValidParams:
                raise RuntimeError("Parameter {} is not a valid parameter for the slurm configuration".format(k))
            try:
                if type(v) == str and CP3SlurmConfigValidParams[k]["type"] == int:
                    setattr(self.cfg, k, int(v))
                elif type(v) == str and CP3SlurmConfigValidParams[k]["type"] == bool:
                    if v.lower() in ['0', 'false', 'no']:
                        setattr(self.cfg, k, False)
                    elif v.lower() in ['1', 'true', 'yes']:
                        setattr(self.cfg, k, True)
                    else:
                        raise ValueError()
                else:
                    setattr(self.cfg, k, v)
            except ValueError:
                raise RuntimeError("Could not convert '{}' to expected type for parameter {}: {}".format(v, k, CP3SlurmConfigValidParams[k]))

        self.slurmScript = os.path.join(self.cfg.batchScriptsDir, self.cfg.batchScriptsFilename)
        self.clusterId = None ## will be set by submit
        self._finishedTasks = dict()
        self._statuses = ["PENDING" for cmd in self.commandList]

        ## output
        try:
            slurm_submit = slurmSubmitWorker(self.cfg, submit=False, debug=False, quiet=False)
        except Exception as ex:
            logger.error("Problem constructing slurm submit worker: {}".format(str(ex)))
            raise ex
        else:
            from contextlib import redirect_stdout
            from io import StringIO
            workerout = StringIO()
            submitLoggerFun = logger.debug
            try:
                with redirect_stdout(workerout):
                    slurm_submit()
            except Exception as ex:
                submitLoggerFun = logger.info
                raise RuntimeError("Problem in slurm_submit: {}".format(str()))
            finally:
                submitLoggerFun("==========     BEGIN slurm_submit output     ==========")
                for ln in workerout.getvalue().split("\n"):
                    submitLoggerFun(ln)
                submitLoggerFun("==========     END   slurm_submit output     ==========")

    def _arrayIndex(self, command):
        return self.commandList.index(command)+1

    def _commandOutDir(self, command):
        """ Output directory for a given command """
        return os.path.join(self.workDirs["out"], str(self._arrayIndex(command)))

    def commandOutFiles(self, command):
        """ Output files for a given command """
        import fnmatch
        cmdOutDir = self._commandOutDir(command)
        if not os.path.isdir(cmdOutDir):
            os.mkdir(cmdOutDir)
        return list( os.path.join(cmdOutDir, fn) for fn in os.listdir(cmdOutDir)
                if any( fnmatch.fnmatch(fn, pat) for pat in self.cfg.stageoutFiles) )

    def submit(self):
        """ Submit the job to slurm """
        logger.info("Submitting an array of {0:d} jobs to slurm".format(len(self.commandList)))
        logger.debug("sbatch {0}".format(self.slurmScript))
        result = subprocess.check_output(["sbatch", self.slurmScript]).decode()

        self.clusterId = next(tok for tok in reversed(result.split()) if tok.isdigit())
        
        ## save to file in case
        with open(os.path.join(self.workDirs["in"], "cluster_id"), "w") as f:
            f.write(self.clusterId)

        logger.info("Submitted, job ID is {}".format(self.clusterId))

    def cancel(self):
        """ Cancel all the jobs using scancel """
        subprocess.check_call(["scancel", self.clusterId])

    def statuses(self, update=True):
        """ list of subjob statuses (numeric, using indices in SlurmJobStatus) """
        if update:
            try:
                self.updateStatuses()
            except Exception as ex:
                logger.error("Exception while updating statuses (will reuse previous): {0!s}".format(ex))
        return [ SlurmJobStatus.index(sjst) for sjst in self._statuses ]

    @property
    def status(self):
        if all(st == self._statuses[0] for st in self._statuses):
            return self._statuses[0]
        elif any(st == "RUNNING" for st in self._statuses):
            return "RUNNING"
        elif any(st == "CANCELLED" for st in self._statuses):
            return "CANCELLED"
        else:
            return "unknown"

    def subjobStatus(self, i):
        return self._statuses[i-1]

    def updateStatuses(self):
        for i in range(len(self.commandList)):
            subjobId = "{0}_{1:d}".format(self.clusterId, i+1)
            status = "unknown"
            if subjobId in self._finishedTasks:
                status = self._finishedTasks[subjobId]
            else:
                try:
                    sacctCmdArgs = ["sacct", "-X", "-n", "--format", "State%20", "-j", subjobId]
                    ret = subprocess.check_output(sacctCmdArgs).decode().strip()
                    if "\n" in ret:
                        raise AssertionError("More than one line in sacct... there's something wrong")
                    if len(ret) != 0:
                        ret = ret.split(" ")[0]
                        if "CANCELLED+" in ret:
                            # Can happen if scancel command did not have time to propagate
                            status = "CANCELLED"
                        else:
                            status = ret
                    else:
                        squeueCmdArgs = ["squeue", "-h", "-O", "state", "-j", subjobId]
                        status = subprocess.check_output(squeueCmdArgs).decode().strip()
                    if status not in SlurmJobStatus_active:
                        self._finishedTasks[subjobId] = status
                except subprocess.CalledProcessError as ex:
                    logger.warning("Could not update status of job ")#{}: {}".format(subjobId, ex!s))
                    # fall back to previous status (probably PENDING or RUNNING) and try again later
                    status = self._statuses[i]
            self._statuses[i] = status

    def getID(self, command):
        return self._arrayIndex(command)
    def commandStatus(self, command):
        return self.subjobStatus(self._arrayIndex(command))
    def getLogFile(self, command):
        return os.path.join(self.workDirs["log"], "slurm-{}_{}.out".format(self.clusterId, self._arrayIndex(command)))

    def getResubmitCommand(self, failedCommands):
        return getResubmitCommand(self.slurmScript, [ self._arrayIndex(cmd) for cmd in failedCommands ])

    def getRuntime(self, command):
        sacctCmdArgs = ["sacct", "-n", "--format", "Elapsed", "-j", "{0}_{1:d}".format(self.clusterId, self._arrayIndex(command))]
        elapsed = subprocess.check_output(sacctCmdArgs).decode().split("\n")[0].strip()
        dys, ms = 0, 0
        if "-" not in elapsed:
            elapsed = "0-{0}".format(elapsed)
            dys, elapsed = (tk.strip() for tk in elapsed.split("-"))
            dys = int(dys)
        if "." in elapsed:
            elapsed, ms = (tk.strip() for tk in elapsed.split("."))
            ms = int(ms)
        import datetime
        return (datetime.datetime.strptime(elapsed, "%H:%M:%S")-datetime.datetime(1900, 1, 1)) + datetime.timedelta(days=dys, milliseconds=ms)

def jobsFromTasks(taskList, workdir=None, batchConfig=None, configOpts=None):
    if batchConfig:
        if not configOpts:
            configOpts = dict()
        else:
            configOpts = dict(configOpts)
        bc_c = dict(batchConfig)
        for k,cov in configOpts.items():
            if k in bc_c:
                if isinstance(cov, list):
                    cov += bc_c[k].split(", ")
                    del bc_c[k]
                else: # ini file takes preference
                    configOpts[k] = bc_c[k]
                    del bc_c[k]
        configOpts.update(bc_c)
    slurmJob = CommandListJob(list(chain.from_iterable(task.commandList for task in taskList)), workDir=workdir, configOpts=configOpts)
    for task in taskList:
        task.jobCluster = slurmJob
    return [ slurmJob ]

def makeTasksMonitor(jobs=[], tasks=[], interval=120):
    """ make a TasksMonitor for slurm jobs """
    return TasksMonitor(jobs=jobs, tasks=tasks, interval=interval
            , allStatuses=SlurmJobStatus
            , activeStatuses=[SlurmJobStatus.index(stNm) for stNm in SlurmJobStatus_active]
            , failedStatuses=[SlurmJobStatus.index(stNm) for stNm in SlurmJobStatus_failed]
            , completedStatus=SlurmJobStatus.index(SlurmJobStatus_completed)
            )


def findOutputsForCommands(batchDir, commandMatchers):
    """
    Look for outputs of matching commands inside batch submission directory

    :param batchDir: batch submission directory (with a ``slurmSubmission.sh`` file)
    :param commandMatchers: a dictionary with matcher objects (return ``True`` when passed matching commands)

    :returns: tuple of a matches dictionary (same keys as commandMatchers, a list of output files from matching commands) and a list of IDs for subjobs without output
    """
    with open(os.path.join(batchDir, "slurmSubmission.sh")) as slurmFile:
        cmds = []
        finished, readingCmds = False, False
        ln = next(slurmFile)
        while not finished:
            if ln.strip().endswith("inputParams=("):
                readingCmds = True
            elif readingCmds:
                if ln.strip() == ")":
                    finished = True
                else:
                    cmds.append(ln.strip().strip('"'))
            ln = next(slurmFile)
    matches = dict()
    id_noOut = []
    for mName, matcher in commandMatchers.items():
        ids_matched = [ (i, cmd) for i, cmd in zip(count(), cmds) if matcher(cmd) ]
        files_found = []
        if not ids_matched:
            logger.warning("No jobs matched for {}".format(mName))
        else:
            outdir = os.path.join(batchDir, "outputs", mName)#, "output_%s"%str(sjId))
            for sjId, cmd in ids_matched:
                if not os.path.exists(os.path.join(outdir, "output_%s.root"%str(sjId))):
                    logger.debug("Output directory for {} not found: {} (command: {})".format(mName, outdir, cmd))
                    id_noOut.append(sjId)
                else:
                    sjOut = [ os.path.join(outdir, fn) for fn in os.listdir(outdir) ]
                    if not sjOut:
                        logger.debug("No output files for {} found in {} (command: {})".format(mName, outdir, cmd))
                        id_noOut.append(sjId)
                    files_found = sjOut
        matches[mName] = len(ids_matched), files_found
    return matches, sorted(id_noOut)

def getResubmitCommand(submissionScript, idsToResubmit):
    if os.path.isdir(submissionScript):
        submissionScript = os.path.join(submissionScript, "slurmSubmission.sh")
    if not os.path.isfile(submissionScript):
        raise FileNotFoundError(submissionScript)
    return ["sbatch", "--array={}".format(",".join(str(sjId) for sjId in idsToResubmit)), submissionScript ]
