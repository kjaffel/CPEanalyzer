# CPEanalyzer
- Cluster Parameter Estimator: algorithm used to determine the position and errors of the CMS Pixel and Strip clusters 
## Recipe for your favorite CMSSW version:
```bash
 cmsrel CMSSW_11_2_2_patch1
 cd CMSSW_11_2_2_patch1/src
 cmsenv
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
