# CPEanalyzer
Cluster Parameter Estimator: algorithm used to determine the position and errors of the CMS Pixel and Strip clusters .
Method used from CMSSW - StripCPEfromTrackAngle; Takes the track angle estimate into account when applying the Lorentz angle and back plane correction, and uses a resolution parameterization as a function of the expected cluster width
## Recipe for your favorite CMSSW version:[current cmssw working version : 11_2_2_patch1]
```bash
 cmsrel CMSSW_11_2_2_patch1
 cd CMSSW_11_2_2_patch1/src
 cmsenv
 scram b
 # https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideScram
```
## Creation of Private Skim [Slurm]:
In order to allow parallelisation and fast iterations, a private skim of files is created from the AlCaReco files. The event content is minimised to the needs for the CPEEstimator, a tighter preselection is also applied, and the files are split in size for optimising between number of files and number of events inside. Skimming is done using the configuration in SiStripCPE/CPEanalyzer/test/skimProducer_cfg.py. There, the used track selection is defined in `SiStripCPE/CPEanalyzer/python/CPETrackSelector_cff.py`, and the trigger selection in `SiStripCPE/CPEanalyzer/python/TriggerSelection_cff.py` (the trigger selection is disabled by default). The event content is defined in `SiStripCPE/CPEanalyzer/python/PrivateSkim_EventContent_cff.py`.

 Which dataset to process is steered via a configurable parameter using the VarParsing, which also allows a local test run. After having run those two scripts for each dataset that one wants to process, the skim is ready for the automated workflow of the Cluster Parameter Estimation. 
### Run a Skim Test :
`configs\alcareco_2018DExpress_localtest.yml` will be used by default as an input:
```python
python CPE4slurm.py --isTest --task skimmer -o mytestDIR
```
- ``-o``/ ``--output``:  Output directory 
- ``-y``/``--yml``    :  Yml file that include your AlcaReco samples should be saved in: configs/
- ``--task``   :  skim/hitresolution 
- ``--isTest`` :  will pass one root file on slurm as cross-check
## Event, Track and Hit Selections:
The strip hit resolution is computed by using hits in overlapping modules of the same layer (["Pair Method"](https://indico.cern.ch/event/305395/contributions/701396/attachments/580300/798934/nmccoll_3_13_RecHitRes.pdf)).

Tracks are selected with the following cuts:
- Good identified and isolated muons 
- Flagged as `high purity` in order to minimise incorrect cluster assignments
- `min pT ~ 0.5 GeV`
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

## Plotting:
```
$  root ../data/tracking_ntuple.root 
root [0] 
Attaching file ../data/tracking_ntuple.root as _file0...
root [1] .x macros/overlay.C 
Info in <TCanvas::MakeDefCanvas>:  created default TCanvas with name c1
```

```
$  root ../data/tracking_ntuple.root 
root [0] 
Attaching file ../data/tracking_ntuple.root as _file0...
root [1] .x macros/eff.C 
Info in <TCanvas::MakeDefCanvas>:  created default TCanvas with name c1
```

## My Talks in Strip Calibration and Local Reconstruction meeting:
- []()
- [11.11 CPE reparameterization update](https://indico.cern.ch/event/934813/#60-cpe-reparameterization)
## References:
- [ CMS SiStrip Simulation, LocalReconstruction and Calibration page](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SiStripCalibration)
- [Project CMSSW displayed by LXR](https://cmssdt.cern.ch/lxr/source/DataFormats/SiStripCluster/interface/SiStripClusterTools.h)
- ["Measurement of Associated Z-Boson and b-Jet Production in Proton-Proton Collisions with the CMS Experiment"](http://cdsweb.cern.ch/record/1476930)
- [PHD-thesis Chapter4:Associated top-quark-pair and b-jetproduction in the dilepton channelat√s = 8  TeV as test of QCDand background to tt+Higgsproduction](https://bib-pubdb1.desy.de/record/222384/files/thesis.pdf)
- [ SiStrip cluster MC truth tools ](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideStripClusterMCtruth)
- [ Analysis Tutorial](http://www.t2.ucsd.edu/twiki2/bin/view/UCSDTier2/AnalysisTutorial?sortcol=table;table=up#Efficiency_Plots)
- [Strip hit resolution of CMS Tracker analysis: DOI:10.13140/RG.2.2.11136.84480](https://www.researchgate.net/publication/317633066_Strip_hit_resolution_of_CMS_Tracker_analysis)
