import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("HitEff")
process.load("Configuration/StandardSequences/MagneticField_cff")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')  

options = VarParsing.VarParsing('analysis')
options.parseArguments()
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

### initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.categories.append('HitEff')
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
                limit = cms.untracked.int32(-1)
                        )
###########################################################
outputFile=options.outputFile
InputTagName = "ALCARECO"+outputFile.split('_')[0]
fileNames=cms.untracked.vstring(options.inputFiles)
###########################################################
process.source = cms.Source("PoolSource", fileNames=fileNames)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1))

process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")
#process.load("RecoLocalTracker.SiStripRecHitConverter.StripCPEfromTrackAngle_cfi")
process.load("RecoTracker.TrackProducer.TrackRefitters_cff")

process.refitTracks = process.TrackRefitterP5.clone(src=cms.InputTag(InputTagName))

process.load("SiStripCPE.CPEanalyzer.SiStripHitResol_cff")
process.anResol.combinatorialTracks = cms.InputTag("refitTracks")
process.anResol.trajectories = cms.InputTag("refitTracks")

process.TFileService = cms.Service("TFileService",
        fileName = cms.string(outputFile)  
)
process.allPath = cms.Path(process.MeasurementTrackerEvent*process.offlineBeamSpot*process.refitTracks*process.hitresol)
