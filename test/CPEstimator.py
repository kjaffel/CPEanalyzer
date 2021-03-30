import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("CPEana")

### Standard Configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')

### global tag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data_GRun', '')
# process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc_GRun', '')

### initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.categories.append('CPEana')
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
        limit = cms.untracked.int32(-1)
        )
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

# setup 'analysis' options
options = VarParsing.VarParsing ('analysis')
options.outputFile = 'CPE_defaultOutput.root'
options.inputFiles= ''#/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/230/00000/7281AF0F-36A0-E811-A56D-FA163E85FA06.root'
options.maxEvents = -1
options.parseArguments()

### Events and data source
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring (options.inputFiles) )

### Track refitter specific stuff
process.load("RecoVertex.BeamSpotProducer.BeamSpot_cff")
import RecoTracker.TrackProducer.TrackRefitter_cfi
import CommonTools.RecoAlgos.recoTrackRefSelector_cfi
process.mytkselector = CommonTools.RecoAlgos.recoTrackRefSelector_cfi.recoTrackRefSelector.clone()
process.mytkselector.src = 'ALCARECOSiStripCalMinBias'
process.mytkselector.quality = ['highPurity']
process.mytkselector.min3DLayer = 2
process.mytkselector.ptMin = 0.5
process.mytkselector.tip = 1.0
process.myRefittedTracks = RecoTracker.TrackProducer.TrackRefitter_cfi.TrackRefitter.clone()
process.myRefittedTracks.src= 'mytkselector'
process.myRefittedTracks.NavigationSchool = ''
process.myRefittedTracks.Fitter = 'FlexibleKFFittingSmoother'

### Analyzer
process.CPEanalysis = cms.EDAnalyzer('CPEanalyzer',
                                         minTracks=cms.untracked.uint32(0),
                                         tracks = cms.untracked.InputTag("ALCARECOSiStripCalMinBias",""),
                                         trajectories = cms.untracked.InputTag('myRefittedTracks'),
                                         association = cms.untracked.InputTag('myRefittedTracks'),
                                         clusters = cms.untracked.InputTag('ALCARECOSiStripCalMinBias'),
                                         StripCPE = cms.ESInputTag('StripCPEfromTrackAngleESProducer:StripCPEfromTrackAngle')
                             )

### TFileService: output histogram or ntuple
process.TFileService = cms.Service("TFileService",fileName = cms.string(options.outputFile))

### Finally, put together the sequence
process.p = cms.Path(process.offlineBeamSpot*process.mytkselector+process.myRefittedTracks+process.CPEanalysis)
