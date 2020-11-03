#!/bin/bash
# N.B : run this script from clean shell with cms_env !!
echo "Hello Rucio Users !"
source /cvmfs/cms.cern.ch/cmsset_default.sh
echo "setup your VOMS-PROXY !"
voms-proxy-init -voms cms -rfc -valid 192:00
source /cvmfs/cms.cern.ch/rucio/setup.sh
export RUCIO_ACCOUNT=kjaffel  # Or your CERN username if it differs
echo """
    - You can then issue the command  
        $ rucio --help  # to understand all your options. 
    - You can list your quota at all sites via the command 
        $ rucio list-account-limits $ RUCIO_ACCOUNT.
    - If you do not have quota in the right place (or enough), you should ask for a quota increase at the RSE(Rucio Storage Elements) you would like to use. To find out who to ask, you can query the RSE attributes to identify the accounts responsible for managing quota.
        $ rucio list-rse-attributes T2_UCL_BE
    - know more about Rucio here: https://twiki.cern.ch/twiki/bin/view/CMSPublic/Rucio
"""

requested_samples=(
'/ZeroBias/Run2018A-SiStripCalZeroBias-12Nov2019_UL2018-v2/ALCARECO'
'/ZeroBias/Run2018B-SiStripCalZeroBias-12Nov2019_UL2018-v2/ALCARECO'
'/ZeroBias/Run2018B-SiStripCalZeroBias-12Nov2019_UL2018_LowPU-v1/ALCARECO'
'/ZeroBias/Run2018C-SiStripCalZeroBias-12Nov2019_UL2018-v2/ALCARECO'
'/ZeroBias/Run2018C-SiStripCalZeroBias-12Nov2019_UL2018_rsb-v1/ALCARECO'
'/ZeroBias/Run2018D-SiStripCalZeroBias-12Nov2019_UL2018_rsb-v1/ALCARECO'
)

for smp in ${requested_samples[*]}; do 
    #rucio add-rule cms:$smp 1 T2_BE_UCL
    rucio add-rule --ask-approval cms:$smp 1 T2_BE_UCL
    
done
rucio list-rules --account=kjaffel | grep "REPLICATING"
