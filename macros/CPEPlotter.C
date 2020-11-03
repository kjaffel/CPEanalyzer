{

gROOT->SetStyle("Plain");
gROOT->ForceStyle();
gStyle->SetOptStat(111110);
//gStyle->SetOptStat(0);

gStyle->SetPalette(1);
////gStyle->SetNumberContours(20);  // Default: 20

gStyle->SetPadLeftMargin(0.15);
gStyle->SetPadRightMargin(0.11);

gStyle->SetPadTopMargin(0.125);
gStyle->SetPadBottomMargin(0.135);

gStyle->SetTitleOffset(1.3,"Y");
gStyle->SetTitleOffset(1.15,"X");

TGaxis::SetMaxDigits(3);
gStyle->SetTitleX(0.26);


gStyle->SetTitleXSize(0.05);
gStyle->SetTitleYSize(0.05);
gStyle->SetTitleSize(0.05,"XY");
gStyle->SetLabelSize(0.05,"XY");



gROOT->ProcessLine(".q");
gROOT->ProcessLine(".L CPEOverview.C");

//gROOT->ProcessLine("CPEOverview a1(\"../test/slurmOutput_v4/results/SiStripCalMinBias_Express_Run2018D.root\");");
gROOT->ProcessLine("CPEOverview a1(\"../test/slurmOutput_v3/Output_1.root\");");

gROOT->ProcessLine("a1.getOverview();");
gROOT->ProcessLine("a1.printOverview(\"../hists/plots/testSummary.ps\");");

}
