import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import glob
import os, os.path

process = cms.Process("HitEff")
process.load("Configuration/StandardSequences/MagneticField_cff")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')  

options = VarParsing.VarParsing ('analysis')
options.parseArguments()
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

### initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.categories.append('HitEff')
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
                limit = cms.untracked.int32(-1)
                        )

run_Cosmis= False
run_UltaLegacyZeroBias = False
run_MinBiasExpress = True

if run_Cosmis:
    InputTagName = "ALCARECOSiStripCalCosmics"
    outputFile = "Run2018C_ALCARECOSiStripCalCosmics.root"
    fileNames=cms.untracked.vstring("file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/C88E7B45-E0DA-0742-B622-25C2C9E0AC58.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/08894276-BD9E-454E-96A9-8E30BE93C0C7.root",
				 	"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/FEA63E84-13F5-3246-BF7D-D7F4C257D419.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/09A05CD3-7D70-B141-870D-DE3BA2E58D96.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/47887C90-18C4-4B4D-86A3-70E6004E2076.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/B481DEBC-037D-1D4D-A767-38FE8A49F8E6.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/D53E4B8C-5D15-D14E-9ABA-047E21DF1A8C.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/330C361E-0D9E-2C46-9805-F292DCF3C3F9.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/510000/B2586374-7ED0-3C4A-9B2C-7A2991A32CDB.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/90CFCA29-7CB7-A145-9E37-779FEA9EDBBB.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/0C458F23-0922-164C-B1A6-306F77DDA853.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/8A5EC816-5F22-BA4F-B01C-36E33A1709DC.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/6737DF42-C8FE-2D42-934D-3C136DCF67A0.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/B803C62D-D3BE-AF42-86A5-239A23A27E46.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/1E91E801-2873-EE45-84FE-DBB752D30B3D.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/2E1015D3-911A-A749-B3B6-88722A7E28E3.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/6B69D370-A739-9D4C-AB04-7D3797214F7A.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/DB1B1C5E-6A8C-364A-814E-10CF7C6F0555.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/FC461B90-05AF-0D47-8381-75E5F8FE1BE6.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/98C6B766-5175-F944-9715-619949A53697.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/33B21065-5027-4442-804F-6C0A18500590.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/F6662AB1-DD84-DA4E-A0C9-F6F2F639821F.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/69ED8F1F-DFE7-EC44-B01A-3B98A03375F9.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/230000/477A0F21-EE03-0646-B94E-A69FE6854E6D.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/EB4BBA67-5816-954F-ADB9-88C9A98B5C28.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/10B71E29-B201-B248-AC9E-6FF3352488AC.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/974701BE-1BE9-8442-8DF4-3AC8C90DEEEB.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/CC0E661D-3AE2-4B49-85CE-2069A1E5FDFF.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/DC711AEB-F292-F344-91CF-718A8D0DEDF2.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/33CC1571-409F-404C-9AAC-DDCEFB21E963.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/421DD12A-ACE6-7641-A616-59DC3F36785A.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/EB34EA65-2772-CB42-857E-BD894F0DDBDB.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/AFF38795-5C87-9B4A-B755-99BAD0C416BB.root",
					"file:/eos/cms/store/data/Run2018C/Cosmics/ALCARECO/SiStripCalCosmics-UL18-v1/40000/68F16890-CF8F-284A-8818-EF0E0E786EFE.root")

elif run_UltaLegacyZeroBias:
	InputTagName = "ALCARECOSiStripCalZeroBias"
	outputFile = "Run2018D-UL_ALCARECOSiStripCalZeroBias.root"
	fileNames=cms.untracked.vstring("file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/F3F28561-1B7E-0444-810D-A119929B4896.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/80508514-FC4F-5E48-84BD-A84EF28EEAE3.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/86DB491C-55E8-9C45-A748-632065719E7B.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/7D9F8691-6521-5247-88A8-97A9FD11EBB6.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280002/2185F94D-CE60-4541-A174-281FEC1217F6.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/5196D8AE-F413-4344-B14D-40CEB7B57736.root",
   				            "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/478C4A87-9779-4043-8EF1-5F0938FC9715.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280002/77E53E14-7349-7C4D-926E-0F7151278A53.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280002/5425331D-22AC-AC4D-A057-F031396B712B.root",
    			     	    "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/F05C07EA-AFA7-184C-8E88-7D1D0B6754FA.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/B559B4C1-A0EE-3444-B54E-0B6BD74E9C81.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/8DCD5AED-9053-0649-AF55-6FC644C84A26.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/232BDB85-A055-0641-BF22-28FF482621F5.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/76328DC5-3778-5E4B-BEC1-B1FCD8305D3C.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280001/A26F1C97-DF47-0248-8176-5EA46DC7083F.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/9831870B-57EF-4745-A70A-488A5E2D16FD.root",
    			  	        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/BC20D7BE-13C7-CD46-9748-09D79AEED760.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/EE51D346-A691-8744-8541-9B028E4BE5C0.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280002/001B8CC6-BBE5-174A-9D83-4126F609020F.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/9393F683-B456-414C-9494-A54BB8E60963.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/F3D0305D-CBB9-4946-8B86-CD0E97B947DC.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/4091B173-B4B9-6648-8474-B10500EB15F4.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/03F44D76-2079-C34C-8E5B-5214B22FE2DC.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280002/4688663E-2C2A-5D43-A0A6-7B1F3FDE7352.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/98DAF8BF-CA7D-1C4D-A6CD-7ACF1441F03D.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/9F86DA7C-1650-214B-A07E-1081DC1A3229.root",
    			 	        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280002/1D650158-4FD2-7345-9BC5-5995B61D9E95.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/3FEA0EC7-0301-364A-A356-D5223D970579.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/2CB86DCB-22E4-8245-9477-886B8C553D5E.root",
    				        "file:/eos/cms/store/data/Run2018D/ZeroBias/ALCARECO/SiStripCalMinBias-12Nov2019_UL2018-v3/280000/F5BBBBCF-2EC7-F54D-8A9C-A557B12F77C1.root")

elif run_MinBiasExpress: 
    InputTagName = "ALCARECOSiStripCalMinBias"
    outputFile=options.outputFile
    fileNames=cms.untracked.vstring(options.inputFiles)
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/230/00000/7281AF0F-36A0-E811-A56D-FA163E85FA06.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/3050E189-5CA0-E811-9C1D-FA163E2322D8.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/2674FDF6-54A0-E811-93EF-FA163E87D4FF.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/D4DC6162-5AA0-E811-8633-FA163EB31FD0.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/E47693E6-4FA0-E811-8F41-FA163E5DE1B1.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/4AE725A7-58A0-E811-A185-FA163EA1368E.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/18F70DC7-54A0-E811-AF25-FA163ED15970.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/1C42148A-5FA0-E811-815E-FA163E4041C8.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/7CF7A60E-47A0-E811-819E-FA163E528D9F.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/0CA49ADD-6AA0-E811-94F3-FA163EAAA5C2.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/72EE7B36-58A0-E811-81A1-FA163E24B9CF.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/5E5122BD-54A0-E811-B892-FA163E0E08DF.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/D25F0971-6EA0-E811-B33B-FA163E4E6CF7.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/8EAC7173-5FA0-E811-8551-FA163E2003A6.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/9A13EBBE-54A0-E811-A3C5-FA163E94BBA0.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/BAC5DD16-47A0-E811-98AF-FA163ED96F18.root",
               # "file:/storage/data/cms/store/express/Run2018D/StreamExpress/ALCARECO/SiStripCalMinBias-Express-v1/000/321/305/00000/D0DB0807-55A0-E811-9B00-FA163EE28A99.root")
else: 
    print( 'Unknown run !!!') 

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
