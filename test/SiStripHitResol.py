import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("HitEff")
process.load("Configuration/StandardSequences/MagneticField_cff")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

options = VarParsing.VarParsing('analysis')
options.parseArguments()
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

### initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
#process.MessageLogger.categories.append('HitEff')
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
                limit = cms.untracked.int32(-1)
                        )
###########################################################
outputFile=options.outputFile
InputTagName = "ALCARECO"+outputFile.split('/')[-2].split('_')[0]
print("InputTagName:", InputTagName )
fileNames=cms.untracked.vstring(options.inputFiles)

from Configuration.AlCa.GlobalTag import GlobalTag
# not the best way to do it # FIXME 
# edmProvDump <filename> | grep -i globaltag
if "RelVal" in outputFile.split('/')[-2]: # mc samples
    process.GlobalTag = GlobalTag(process.GlobalTag, '112X_mcRun3_2021_realistic_v13', '')  
else: # data
    process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')  
###########################################################
process.source = cms.Source("PoolSource", fileNames=fileNames)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1))

process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")
# https://cmssdt.cern.ch/lxr/source/RecoLocalTracker/SiStripRecHitConverter/python/StripCPEfromTrackAngle_cfi.py?v=CMSSW_11_2_1&%21v=CMSSW_11_2_1
#  useLegacyError= False , maxChgOneMIP = 6000.
process.load("RecoLocalTracker.SiStripRecHitConverter.StripCPEfromTrackAngle_cfi")
process.load("RecoTracker.TrackProducer.TrackRefitters_cff")

process.refitTracks = process.TrackRefitterP5.clone(src=cms.InputTag(InputTagName))

process.load("SiStripCPE.CPEanalyzer.SiStripHitResol_cff")
process.anResol.combinatorialTracks = cms.InputTag("refitTracks")
process.anResol.trajectories = cms.InputTag("refitTracks")

process.TFileService = cms.Service("TFileService",
        fileName = cms.string(outputFile)  
)
process.allPath = cms.Path(process.MeasurementTrackerEvent*process.offlineBeamSpot*process.refitTracks*process.hitresol)
