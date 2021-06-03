import os
import sys
import ROOT
import glob
import argparse
import collections
import yaml
from copy import deepcopy
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def ResolutionsOverModules(path=None):
    colors = [ROOT.kViolet, ROOT.kBlack, ROOT.kRed, ROOT.kGreen, ROOT.kBlue, ROOT.kCyan, ROOT.kViolet, ROOT.kRed+2, ROOT.kYellow, ROOT.kMagenta, ROOT.kCyan, ROOT.kOrange, ROOT.kSpring, ROOT.kTeal]
    tree_tracks = ['track_momentum', 'track_eta', 'track_trackChi2']
    #tree_hitpair = {'momentum':100.,'numHits':, 'trackChi2':, 'detID1':, 'pitch1':, 'clusterW1':, 'expectedW1':, 'atEdge1':, 'simpleRes':, 'detID2':, 'clusterW2':, 'expectedW2':, 'atEdge2':, 'pairPath':, 'hitDX':, 'trackDX':, 'trackDXE':, 'trackParamX':, 'trackParamY':, 'trackParamDXDZ':, 'trackParamDYDZ':, 'trackParamXE':, 'trackParamYE':, 'trackParamDXDZE':, 'trackParamDYDZE':, 'pairsOnly':}
    
    analysisCfgs =os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "analysis.yml")
    with open(analysisCfgs,"r") as file:
        ymlConfiguration = yaml.load(file, Loader=yaml.FullLoader)
    
    tracks_and_hits = collections.defaultdict(dict)
    for rootf in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "outputs", "*.root")):
        smp = rootf.split('/')[-1]
        smpName = '{}'.format(smp.replace('.root', ''))
        
        era = ymlConfiguration["samples"][smpName]['era']
        plots_dir = os.path.join(path, "plots_run{}".format(era))
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)
        
        file_ = ROOT.TFile(rootf)
        file = file_.Get("anResol") # cd TDirectoryFile
        for obj_key in  file.GetListOfKeys():
            obj = file.Get(obj_key.GetName())
            print( obj_key.GetName())
            tree = file.Get("{}".format(obj.GetName()))
            N = tree.GetEntries()
            print( 'N events ', N )
            for branch in tree.GetListOfBranches():
                branchName = branch.GetName() 
                histo = tree.GetBranch(branchName)

                #tree.Draw("{}>>gethist(60,{},{})".format(branchName, tree.GetMinimum(branchName), tree.GetMaximum(branchName)))
                tree.Draw("{}>>gethist(60,{},{})".format(branchName, tree.GetMinimum(branchName), 1.))
                
                h = ROOT.gROOT.FindObject("gethist")
                if not h:
                    print('Could not find key - {} - in file : {}'.format(branchName, smp))
                else:
                    tracks_and_hits[branchName][smpName] = deepcopy(h)
                    #tracks[histoName][smpName].SetDirectory(0)
        file.Close()
    print( tracks_and_hits )
    for var_ToPlot in tracks_and_hits.keys(): 
        C = ROOT.TCanvas("c1","c1",500,400)
        legend = ROOT.TLegend(0.6, 0.6, 0.9, 0.9)
        legend.SetFillStyle(4000)
        legend.SetBorderSize(0)
        #C.SetLogy()
        #C.SetLogx()
        C.Clear()
        for i,(smpName, h) in enumerate(tracks_and_hits[var_ToPlot].items()):
            
            if h.Integral() ==0. :
                continue
            #h.Scale(1./h.Integral()) # normalized to 1 
            h.SetLineStyle(1)
            h.SetLineColor(colors[i])
            h.SetLineWidth(2)
            h.GetXaxis().SetTitle("{}".format(var_ToPlot))
            h.GetYaxis().SetTitle("Events")
            h.SetMaximum(h.GetMaximum()+1.1)
            h.SetMinimum(0.)
            legend.AddEntry(h,smpName + " ")
            h.Draw("H same")
            
        legend.Draw()
        C.Print("{}/{}.png".format(plots_dir, var_ToPlot))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--path', required=True, help='path to slurm output dir ')
    options = parser.parse_args()
    ResolutionsOverModules(path=options.path)
