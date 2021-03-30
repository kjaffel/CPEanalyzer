import FWCore.ParameterSet.Config as cms
import Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi
##
## FILTER for high purity tracks
##
HighPuritySelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
    applyBasicCuts = True,
    filter = True,
    src = 'ALCARECOTkAlMuonIsolated',
    etaMin = -999.,
    etaMax = 999.,
    trackQualities = ["highPurity"],
)

MinBiasSkimSelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
    applyBasicCuts = True,
    filter = True,
    src = 'ALCARECOTkAlMinBias',
    ptMin = 5.,
    pMin = 9.,
    etaMin = -999.,
    etaMax = 999.,
    d0Min = -2.,
    d0Max = 2.,
    dzMin = -25.,
    dzMax = 25.,
    nHitMin = 12,
    nHitMin2D = 2,
)

MuSkimSelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
    applyBasicCuts = True,
    filter = True,
    src = 'ALCARECOTkAlMuonIsolated',
    ptMin = 17.,
    pMin = 17.,
    etaMin = -2.5,
    etaMax = 2.5,
    d0Min = -2.,
    d0Max = 2.,
    dzMin = -25.,
    dzMax = 25.,
    nHitMin = 6,
    nHitMin2D = 0,
)

#import CommonTools.RecoAlgos.recoTrackRefSelector_cfi
#SiStripCalMinBiasSelector =commonTools.RecoAlgos.recoTrackRefSelector_cfi.recoTrackRefSelector.clone(
SiStripCalMinBiasSelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
    filter         = True ,##do not store empty events 
    src            = 'ALCARECOSiStripCalMinBias',
    applyBasicCuts = True,
    ptMin          = 0.8, ##GeV
    nHitMin        = 6, ## at least 6 hits required
    chi2nMax       = 10.,
)

DoubleMuSkimSelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
    applyBasicCuts = True,
    filter = True,
    src = 'ALCARECOTkAlZMuMu',
    ptMin = 17.,
    pMin = 17.,
    etaMin = -2.5,
    etaMax = 2.5,
    d0Min = -2.,
    d0Max = 2.,
    dzMin = -25.,
    dzMax = 25.,
    nHitMin = 6,
    nHitMin2D = 0,
)

CosmicsSkimSelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
    applyBasicCuts = True,
    filter = True,
    src = 'ALCARECOTkAlCosmicsCTF0T',
    etaMin = -2.5,
    etaMax = 2.5,
    nHitMin = 6,
    nHitMin2D = 0,
)
