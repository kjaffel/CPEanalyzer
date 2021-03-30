from __future__ import print_function
import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import sys
import os, os.path 

##
## Process definition
##
process = cms.Process("CpeSkim")
process.load("Configuration.StandardSequences.Services_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("RecoVertex.BeamSpotProducer.BeamSpot_cff")

##
## Setup command line options
##
options = VarParsing.VarParsing ('analysis')
options.parseArguments()
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True))

##
## Message Logger
##
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.categories.append('CPETrackSelector')
#process.MessageLogger.categories.append('')
process.MessageLogger.cerr.INFO.limit = 0
process.MessageLogger.cerr.default.limit = -1
process.MessageLogger.cerr.CPETrackSelector = cms.untracked.PSet(limit = cms.untracked.int32(-1))
process.MessageLogger.cerr.FwkReport.reportEvery = 1000 ## really show only every 1000th

maxEvents = -1
outputFileSize = 350000
trackSelection = None
globalTag = None
sample = "ALCARECOSiStripCalMinBias"

##
## Start of Configuration
##
if sample == 'data_UL2018A':
    process.load("SiStripCPE.CPEanalyzer.samples.Data_SiStripCalMinBias_Run2018A_UL2018_cff")
    outputName = 'SiStripCalMinBias_Run2018A_UL2018.root'
    trackSelection = "MinBias"

elif sample == 'data_express_Run2018B':
    process.load("SiStripCPE.CPEanalyzer.samples.Data_SiStripCalMinBias_Run2018B_express_cff")
    outputName = 'SiStripCalMinBias_Run2018B_express.root'
    globalTag = 'auto:run2_data'
    trackSelection = "MinBias" #FIXME not right, but give results since the latest give empty skim 
    #trackSelection = "SiStripCalMinBias"
    #globalTag = 'auto:run3_data_express'
    #globalTag = 'auto:run2_data_GRun'
    #globalTag = '101X_dataRun2_Express_v7'
elif sample == "ALCARECOSiStripCalMinBias":
    globalTag = 'auto:run2_data'
    trackSelection = 'SiStripCalMinBias'
    fileNames=cms.untracked.vstring(options.inputFiles)
    process.source = cms.Source("PoolSource", fileNames=fileNames)
else:
    print('ERROR --- incorrect data sammple: ', sample)
    exit(8888)

##
## Choice of GlobalTag
##
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag.globaltag = '101X_dataRun2_Express_v7'
if globalTag == None:
    print("No global tag specified, is this intended?")
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, globalTag, '')
    print("Using global tag \n"+process.GlobalTag.globaltag._value)

print("Using global tag "+process.GlobalTag.globaltag._value)


##
## Number of Events (should be after input file)
##
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(maxEvents) )

##
## Skim tracks
##
import SiStripCPE.CPEanalyzer.CPETrackSelector_cff as CPETrackSelector
# Determination of which CPETrackSelector to use
if trackSelection == "SingleMu":
    trackSelector = CPETrackSelector.MuSkimSelector
elif trackSelection == "DoubleMu":
    trackSelector = CPETrackSelector.DoubleMuSkimSelector
elif trackSelection == "MinBias":
    trackSelector = CPETrackSelector.MinBiasSkimSelector
elif trackSelection == "Cosmics":
    trackSelector = CPETrackSelector.CosmicsSkimSelector
elif trackSelection =="SiStripCalMinBias":
    trackSelector = CPETrackSelector.SiStripCalMinBiasSelector

else: # Extend list here with custom track selectors
    print("Unknown trackSelection %s, exiting"%(trackSelection))
    exit(1)


# https://github.com/cms-sw/cmssw/blob/CMSSW_11_2_X/Alignment/CommonAlignment/python/tools/trackselectionRefitting.py
print (trackSelector.src.getModuleLabel() )
if trackSelector.src.getModuleLabel() == "ALCARECOSiStripCalMinBias":
    import RecoTracker.TrackProducer.TrackRefitter_cfi
    import CommonTools.RecoAlgos.recoTrackRefSelector_cfi
    process.mytkselector = CommonTools.RecoAlgos.recoTrackRefSelector_cfi.recoTrackRefSelector.clone()
    process.mytkselector.src = 'ALCARECOSiStripCalMinBias'
    process.mytkselector.quality = ['highPurity']
    process.mytkselector.min3DLayer = 2
    process.mytkselector.ptMin = 0.5
    process.mytkselector.tip = 1.0
    # https://cmssdt.cern.ch/lxr/source/RecoTracker/TrackProducer/python/TrackRefitter_cfi.py
    process.seqTrackselRefit = RecoTracker.TrackProducer.TrackRefitter_cfi.TrackRefitter.clone()
    process.seqTrackselRefit.src= 'mytkselector'
    process.seqTrackselRefit.NavigationSchool = ''
    process.seqTrackselRefit.Fitter = 'FlexibleKFFittingSmoother'
    
    process.path = cms.Path(
        process.offlineBeamSpot*
        process.mytkselector+process.seqTrackselRefit
    )

else:
    process.mytkselector = trackSelector
    process.seqTrackselRefit = trackselRefit.getSequence(process, trackSelector.src.getModuleLabel())

    process.path = cms.Path(
        process.offlineBeamSpot*
        process.seqTrackselRefit*
        process.mytkselector
    )

##
## Define event selection from path
##
EventSelection = cms.PSet(
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('path')
    )
)

##
## configure output module
##
process.out = cms.OutputModule("PoolOutputModule",
    ## Parameters directly for PoolOutputModule
    fileName = cms.untracked.string(options.outputFile),
    # Maximum size per file before a new one is created
    maxSize = cms.untracked.int32(outputFileSize),
    dropMetaData = cms.untracked.string("DROPPED"),
    ## Parameters for inherited OutputModule
    SelectEvents = EventSelection.SelectEvents,
    outputCommands = cms.untracked.vstring(
        'drop *',
    ),
)
process.load("SiStripCPE.CPEanalyzer.PrivateSkim_EventContent_cff")
process.out.outputCommands.extend(process.CpeSkimEventContent.outputCommands)

##
## Outpath
##
process.outpath = cms.EndPath(process.out)
