import sys #TODO change to opt_parse
import os
import ROOT
from ROOT import TFile, TH1, TH2, TCanvas

ROOT.gROOT.SetBatch(True)

if not len(sys.argv) == 3:
    print("Error, expecting 2 args (input file and output dir)")
    sys.exit()

file_in    = sys.argv[1]
folder_out = sys.argv[2]

if not os.path.isdir(folder_out):
    print("Error, {} is not a folder".format(folder_out))
    sys.exit()

ff = TFile(file_in)
to_print2D = []
to_print1D = []
for obj_key in ff.GetListOfKeys():
    obj = ff.Get(obj_key.GetName()) #TODO change me
    if isinstance(obj,TH2):
        to_print2D.append(obj)
    elif isinstance(obj,TH1):
        to_print1D.append(obj)
if len(to_print2D) != 0:
    for i,obj in enumerate(to_print2D):
        print ("Drawing {}/{} : ".format(i+1,len(to_print2D),obj.GetName()))
        canvas = TCanvas()
        obj.Draw("col0z")
        canvas.Print("{}/{}.png".format(folder_out,obj.GetName()))
if len(to_print1D) != 0:
    for i,obj in enumerate(to_print1D):
        print ("Drawing {}/{} : ".format(i+1,len(to_print1D),obj.GetName()))
        canvas = TCanvas()
        obj.SetLineWidth(2)
        obj.SetLineColor(ROOT.kBlue)
        obj.Draw("A")
        canvas.Print("{}/{}.png".format(folder_out,obj.GetName()))

