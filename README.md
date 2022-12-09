# CPEanalyzer
Cluster Parameter Estimator: algorithm used to determine the position and errors of the CMS Pixel and Strip clusters .
Method used from CMSSW - StripCPEfromTrackAngle; Takes the track angle estimate into account when applying the Lorentz angle and back plane correction, and uses a resolution parameterization as a function of the expected cluster width. 

This repositry is based on [Hit resolution repositry](https://gitlab.cern.ch/coldham/hitresolutionproject/-/tree/master) and large part of the code have been re-used for CPE studies purpose on the top of [CPEanalayser](https://github.com/delaere/cmssw/tree/CPE_from-CMSSW_10_6_2/UserCode/CPEanalyzer)!
## Recipe for your favorite CMSSW version:[current cmssw working version : 11_3_0]
```bash
 cmsrel CMSSW_11_3_0
 cd CMSSW_11_3_0/src
 # specific to ingrid, https://github.com/kjaffel/ZA_FullAnalysis#environment-setup-always- 
 cms_env 
 cmsenv
 mkdir SiStripCPE
 cd SiStripCPE
 git clone https://github.com/kjaffel/CPEanalyzer
 # https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideScram
 scram b 
```
## Creation of Private Skim [Slurm]:
In order to allow parallelisation and fast iterations, a private skim of files is created from the AlCaReco files. The event content is minimised to the needs for the CPEEstimator, a tighter preselection is also applied, and the files are split in size for optimising between number of files and number of events inside. Skimming is done using the configuration in SiStripCPE/CPEanalyzer/test/skimProducer_cfg.py. There, the used track selection is defined in `SiStripCPE/CPEanalyzer/python/CPETrackSelector_cff.py`, and the trigger selection in `SiStripCPE/CPEanalyzer/python/TriggerSelection_cff.py` (the trigger selection is disabled by default). The event content is defined in `SiStripCPE/CPEanalyzer/python/PrivateSkim_EventContent_cff.py`.

 Which dataset to process is steered via a configurable parameter using the VarParsing, which also allows a local test run. After having run those two scripts for each dataset that one wants to process, the skim is ready for the automated workflow of the Cluster Parameter Estimation. 
### Launch a Test :
`configs\alcareco_localtest.yml` will be used by default as an input:
```python
python CPE4slurm.py --isTest --task hitresolution -o mytestDIR
```
- ``-o``/ ``--output``:  Output directory 
- ``-y``/``--yml``    :  YAML file that include your AlcaReco samples should be saved in: configs/
- ``--task``   :  hitresolution or skim ( the later is deprecated sorry!).
- ``--isTest`` :  will pass one root file on slurm as cross-check.

Hadd root files and launch plotting script ``macros/Resolutions.cc``
```python
python postprocessing.py --workdir mytestDIR
```
## Event, Track and Hit Selections:
The strip hit resolution is computed by using hits in overlapping modules of the same layer (["Pair Method"](https://indico.cern.ch/event/305395/contributions/701396/attachments/580300/798934/nmccoll_3_13_RecHitRes.pdf)).

Tracks are selected with the following cuts:
- Good identified and isolated muons 
- Flagged as `high purity` in order to minimise incorrect cluster assignments
- `min pT 3 GeV`
- The impact parameter is required to be close to the beamspot : `|d0| < 20 cm |dz| < 60 cm`
- Goodness of the track fit : The track fit must yield a good `X2`
- With the selection of tracks of high transverse momentum, the angles are mainly small and so is the cluster width. 
An important criterion of a good measurement from a strip cluster is, whether its width Wcl matches to the projected track length. 

Hit pairs are selected by requiring:
- At most 4 strips cluster width;
- Clusters that are of the same width in both the modules;
- Clusters that are not at the edge of the modules;
- Predicted path (distance of propagation from one surface to the next) < 7 cm; i.e. only pairs within the same layer are allowed;
- Error on predicted distance in the bending coordinate between the two hits < 25 microns 

## Useful Plotting macros:
``macros/PlottingToOls/CPEplotter.py`` is the main script used for plotting the saved resolution values in ``workdir/outputs/sample_Name/HitResolutionValues/HitResolutionValues_*.txt`` after postprocessing.
```python
python CPEplotter.py --path to__mytestDIR --run <run>
```
- ``<run>`` : choices are ``ul`` or ``pre`` (ul for ULegacy or pre for pre-ULegacy)

## My Talks in Strip Calibration and Local Reconstruction meeting:
- [Weekly Tracker DPG Meetings 2.May.22](https://indico.cern.ch/event/1140520/#2-cpe-update)
- [Weekly Tracker DPG Meetings 9.Nov.20](https://indico.cern.ch/event/934813/#60-cpe-reparameterization)

## References:
- [Phase 1 Upgrade Detector DetId schema](https://github.com/cms-sw/cmssw/blob/master/Geometry/TrackerNumberingBuilder/README.md)
- [CMS SiStrip Simulation, LocalReconstruction and Calibration page](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SiStripCalibration)
- [Project CMSSW displayed by LXR](https://cmssdt.cern.ch/lxr/source/DataFormats/SiStripCluster/interface/SiStripClusterTools.h)
- ["Measurement of Associated Z-Boson and b-Jet Production in Proton-Proton Collisions with the CMS Experiment"](http://cdsweb.cern.ch/record/1476930)
- [PHD-thesis Chapter4:Associated top-quark-pair and b-jetproduction in the dilepton channelat√s = 8  TeV as test of QCDand background to tt+Higgsproduction](https://bib-pubdb1.desy.de/record/222384/files/thesis.pdf)
- [ SiStrip cluster MC truth tools ](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideStripClusterMCtruth)
- [ Analysis Tutorial](http://www.t2.ucsd.edu/twiki2/bin/view/UCSDTier2/AnalysisTutorial?sortcol=table;table=up#Efficiency_Plots)
- [Troubleshooting Guide](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookTroubleShooting)
- [Strip hit resolution of CMS Tracker analysis: DOI:10.13140/RG.2.2.11136.84480](https://www.researchgate.net/publication/317633066_Strip_hit_resolution_of_CMS_Tracker_analysis)
