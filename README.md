# CPEanalyzer
- Cluster Parameter Estimator: algorithm used to determine the position and errors of the CMS Pixel and Strip clusters 
## Recipe for your favorite CMSSW version:
```bash
 cmsrel CMSSW_11_2_2_patch1
 cd CMSSW_11_2_2_patch1/src
 cmsenv
```
## Creation of Private Skim :
In order to allow parallelisation and fast iterations, a private skim of files is created from the AlCaReco files. The event content is minimised to the needs for the CPEEstimator, a tighter preselection is also applied, and the files are split in size for optimising between number of files and number of events inside. Skimming is done using the configuration in SiStripCPE/CPEanalyzer/test/skimProducer_cfg.py. There, the used track selection is defined in `SiStripCPE/CPEanalyzer/python/CPETrackSelector_cff.py`, and the trigger selection in `SiStripCPE/CPEanalyzer/python/TriggerSelection_cff.py` (the trigger selection is disabled by default). The event content is defined in `SiStripCPE/CPEanalyzer/python/PrivateSkim_EventContent_cff.py`.

 Which dataset to process is steered via a configurable parameter using the VarParsing, which also allows a local test run. After having run those two scripts for each dataset that one wants to process, the skim is ready for the automated workflow of the Cluster Parameter Estimation. 
### Run a Skim Test :
`configs\alcareco_2018D_localtest.yml` will be used by default as an input:
```python
python RunSkimmer.py --isTest --output
```
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

## My Talks:
## References:
- ["Measurement of Associated Z-Boson and b-Jet Production in Proton-Proton Collisions with the CMS Experiment"](http://cdsweb.cern.ch/record/1476930)
- [ SiStrip cluster MC truth tools ](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideStripClusterMCtruth)
- [ Analysis Tutorial](http://www.t2.ucsd.edu/twiki2/bin/view/UCSDTier2/AnalysisTutorial?sortcol=table;table=up#Efficiency_Plots)
