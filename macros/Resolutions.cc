using namespace ROOT; 
using ROOT::RDF::RNode;
using floats = ROOT::VecOps::RVec<float>;
using ints = ROOT::VecOps::RVec<int>;
using bools = ROOT::VecOps::RVec<bool>;
using chars = ROOT::VecOps::RVec<UChar_t>;
using doubles = ROOT::VecOps::RVec<double>;

vector<float> HitResolutionVector;
vector<float> DoubleDifferenceVector;
vector<float> HitDXVector;
vector<float> TrackDXVector;
vector<float> TrackDXEVector;
vector<float> CPEEstimatedVector;

std::string HitResoFileName;
std::string GaussianFitsFileName;
std::string suffix;


void ResolutionsCalculator(const string& region, const int& Unit_Int, const int& UL, const string& InputFileString, const string& cluster_width){

  std::string CutFlowReportString;
  std::string DoubleDiffString;
  std::string HitDXString;
  std::string TrackDXString;
  std::string TrackDXEString;
  std::string CPEEstimatedString;
  switch(UL){
	case 0: switch(Unit_Int){
        		case 0: GaussianFitsFileName = "GaussianFits_PitchUnits_clusterW" + cluster_width + "_ALCARECO.root"; 
                        HitResoFileName = "HitResolutionValues_clusterW" + cluster_width + "_" + "PitchUnits_ALCARECO.txt";
                        CutFlowReportString = "CutFlowReport_" + region + "_clusterW" + cluster_width + "_PitchUnits_ALCARECO.txt";
                        DoubleDiffString = "hitDX_OverPitch-trackDX_OverPitch";
                        HitDXString = "hitDX_OverPitch";
                        TrackDXString = "trackDX_OverPitch";
                        TrackDXEString = "trackDXE_OverPitch";
                        CPEEstimatedString = "StripErrorSquared1_OverPitch";
                        suffix = "  (pitch unit)";
				break;

        		case 1: GaussianFitsFileName = "GaussianFits_Centimetres_clusterW" + cluster_width + "_ALCARECO.root"; 
                        HitResoFileName = "HitResolutionValues_clusterW" + cluster_width + "_" + "Centimetres_ALCARECO.txt";
                        CutFlowReportString = "CutFlowReport_" + region + "_clusterW" + cluster_width + "_Centimetres_ALCARECO.txt";
                        DoubleDiffString = "hitDX-trackDX";
                        HitDXString = "hitDX";
                        TrackDXString = "trackDX";
                        TrackDXEString = "trackDXE"; 
                        CPEEstimatedString = "StripErrorSquared1";
                        suffix = "  (cm unit)";
				break;

        		default: std::cout << "ERROR: UnitInt must be 0 or 1." << std::endl; break;
  		}

		break;

	case 1: switch(Unit_Int){
        		case 0: GaussianFitsFileName = "GaussianFits_PitchUnits_clusterW" + cluster_width + "_ALCARECO_UL.root"; 
                        HitResoFileName = "HitResolutionValues_" + cluster_width + "_" + "PitchUnits_ALCARECO_UL.txt";
                        CutFlowReportString = "CutFlowReport_" + region + "_" + cluster_width + "_PitchUnits_ALCARECO_UL.txt";
                        DoubleDiffString = "hitDX_OverPitch-trackDX_OverPitch";
                        HitDXString = "hitDX_OverPitch";
                        TrackDXString = "trackDX_OverPitch";
                        TrackDXEString = "trackDXE_OverPitch";
                        CPEEstimatedString = "StripErrorSquared1_OverPitch";
                        suffix = "  (pitch unit)";
                break;

        		case 1: GaussianFitsFileName = "GaussianFits_Centimetres_clusterW" + cluster_width + "_ALCARECO_UL.root"; 
				        HitResoFileName = "HitResolutionValues_" + cluster_width + "_" + "Centimetres_ALCARECO_UL.txt";
                        CutFlowReportString = "CutFlowReport_" + region + "_" + cluster_width + "_Centimetres_ALCARECO_UL.txt";
                        DoubleDiffString = "hitDX-trackDX";
                        HitDXString = "hitDX";
                        TrackDXString = "trackDX";
                        TrackDXEString = "trackDXE"; 
                        CPEEstimatedString = "StripErrorSquared1";
                        suffix = "  (cm unit)";
                break;

                default: std::cout << "ERROR: UnitInt must be 0 or 1." << std::endl; break;
        }

		break;
	default: std::cout << "The UL input parameter must be set to 0 (for ALCARECO) or 1 (for UL ALCARECO)." << std::endl; break;
  }

  //opening the root file
  ROOT::RDataFrame d("anResol/reso", InputFileString);
  
  auto df = d.Define("partition", "(detID1>>25)&0x7").Filter("((detID2>>25)&0x7) == partition"); 
    // should let all pairs pass, they're in the same layer by definition;
  auto df_tib = df.Filter("partition == 3").Define("layer", "(detID1>>14)&0x7");
  auto df_tid = df.Filter("partition == 4").Define("side", "(detID1>>13)&0x3").Define("disk", "(detID1>>11)&0x3").Define("ring", "(detID1>>9)&0x3");
  auto df_tob = df.Filter("partition == 5").Define("layer", "(detID1>>14)&0x7");
  auto df_tec = df.Filter("partition == 6").Define("side", "(detID1>>18)&0x3").Define("wheel", "(detID1>>14)&0xF").Define("ring", "(detID1>>5)&0x7");

  int RegionInt = 0;

  if(region == "TIB_L1"){RegionInt = 1;}
  else if(region == "TIB_L2"){RegionInt = 2;}
  else if(region == "TIB_L3"){RegionInt = 3;}
  else if(region == "TIB_L4"){RegionInt = 4;}
  else if(region == "Side_TID"){RegionInt = 5;}
  else if(region == "Wheel_TID"){RegionInt = 6;}
  else if(region == "Ring_TID"){RegionInt = 7;}
  else if(region == "TOB_L1"){RegionInt = 8;}
  else if(region == "TOB_L2"){RegionInt = 9;}
  else if(region == "TOB_L3"){RegionInt = 10;}
  else if(region == "TOB_L4"){RegionInt = 11;}
  else if(region == "TOB_L5"){RegionInt = 12;}
  else if(region == "TOB_L6"){RegionInt = 13;}
  else if(region == "Side_TEC"){RegionInt = 14;}
  else if(region == "Wheel_TEC"){RegionInt = 15;}
  else if(region == "Ring_TEC"){RegionInt = 16;}
  else if(region == "TIB_All"){RegionInt = 17;}
  else if(region == "TOB_All"){RegionInt = 18;}
  else if(region == "TID_All"){RegionInt = 19;}
  else if(region == "TEC_All"){RegionInt = 20;}
  else if(region == "Pixel_Barrel"){RegionInt = 21;}
  else if(region == "Pixel_EndcapDisk"){RegionInt = 22;}
  else if (region == "TID_R1"){RegionInt = 23;}
  else if (region == "TID_R2"){RegionInt = 24;}
  else if (region == "TID_R3"){RegionInt = 25;}
  else if (region == "TEC_R1"){RegionInt = 26;}
  else if (region == "TEC_R2"){RegionInt = 27;}
  else if (region == "TEC_R3"){RegionInt = 28;}
  else if (region == "TEC_R4"){RegionInt = 29;}
  else if (region == "TEC_R5"){RegionInt = 30;}
  else if (region == "TEC_R6"){RegionInt = 31;}
  else if (region == "TEC_R7"){RegionInt = 32;}
  else{std::cout << "Error: The tracker region " << region << " was chosen. Please choose a region out of: TIB L1, TIB L2, TIB L3, TIB L4, Side TID, Wheel TID, Ring TID, TOB L1, TOB L2, TOB L3, TOB L4, TOB L5, TOB L6, Side TEC, Wheel TEC, Ring TEC, TID_R1, TID_R2, TID_R3, TEC_R1, TEC_R2, TEC_R3, TEC_R4, TEC_R5, TEC_R6 or TEC_R7" << std::endl; return 0;}



  //Lambda function to filter the detID for different layers
  auto SubDet_Function{[&RegionInt](const int& detID1_input, const int& detID2_input){
	
        bool OutputBool = 0;

	switch(RegionInt){

		case 1: {OutputBool = (((detID1_input>>25)&0x7) == 3) && ((detID1_input>>14)&0x7) == 1 &&
                              (((detID2_input>>25)&0x7) == 3) && ((detID2_input>>14)&0x7) == 1; //TIB L1 
			 break;}
		case 2: {OutputBool = (((detID1_input>>25)&0x7) == 3) && (((detID1_input>>14)&0x7) == 2) &&
				              (((detID2_input>>25)&0x7) == 3) && (((detID2_input>>14)&0x7) == 2); //TIB L2
			 break;}
		case 3: {OutputBool = (((detID1_input>>25)&0x7) == 3) && (((detID1_input>>14)&0x7) == 3) &&
				              (((detID2_input>>25)&0x7) == 3) && (((detID2_input>>14)&0x7) == 3); //TIB L3
			 break;}
		case 4: {OutputBool = (((detID1_input>>25)&0x7) == 3) && (((detID1_input>>14)&0x7) == 4) &&
				              (((detID2_input>>25)&0x7) == 3) && (((detID2_input>>14)&0x7) == 4); //TIB L4
			 break;}
		case 5: {OutputBool = ( (((detID1_input>>13)&0x3) == 1) && (((detID2_input>>13)&0x3) == 1) ) || 
                              ( (((detID1_input>>13)&0x3) == 2) && (((detID2_input>>13)&0x3) == 2) ); //TID Side (1 -> TID-, 2 -> TID+)  
    		 break;}
		case 6: {OutputBool = (((detID1_input>>11)&0x3) == 2) && (((detID2_input>>11)&0x3) == 2); //TID Wheel 
			 break;}
		case 7: {OutputBool = ( (((detID1_input>>9)&0x3) == 2) && (((detID2_input>>9)&0x3) == 2) ); //TID Ring 
 			 break;}
		case 8: {OutputBool = (((detID1_input>>25)&0x7) == 5) && (((detID1_input>>14)&0x7) == 1) &&
			 	              (((detID2_input>>25)&0x7) == 5) && (((detID2_input>>14)&0x7) == 1); //TOB L1 
			 break;}
		case 9: {OutputBool = (((detID1_input>>25)&0x7) == 5) && (((detID1_input>>14)&0x7) == 2) &&
			                  (((detID2_input>>25)&0x7) == 5) && (((detID2_input>>14)&0x7) == 2); //TOB L2  
			 break;}
		case 10: {OutputBool = (((detID1_input>>25)&0x7) == 5) && (((detID1_input>>14)&0x7) == 3) && 
				               (((detID2_input>>25)&0x7) == 5) && (((detID2_input>>14)&0x7) == 3); //TOB L3
			 break;}
		case 11: {OutputBool = (((detID1_input>>25)&0x7) == 5) && (((detID1_input>>14)&0x7) == 4) &&
				               (((detID2_input>>25)&0x7) == 5) && (((detID2_input>>14)&0x7) == 4); //TOB L4 
			 break;}
		case 12: {OutputBool = (((detID1_input>>25)&0x7) == 5) && (((detID1_input>>14)&0x7) == 5) &&
				               (((detID2_input>>25)&0x7) == 5) && (((detID2_input>>14)&0x7) == 5); //TOB L5 
			 break;}
		case 13: {OutputBool = (((detID1_input>>25)&0x7) == 5) && (((detID1_input>>14)&0x7) == 6) &&
				               (((detID2_input>>25)&0x7) == 5) && (((detID2_input>>14)&0x7) == 6); //TOB L6 
			 break;}
		case 14: {OutputBool = ( (((detID1_input>>18)&0x3) == 1) && (((detID2_input>>18)&0x3) == 1) ) ||
				               ( (((detID1_input>>18)&0x3) == 2) && (((detID2_input>>18)&0x3) == 2) ); //Side TEC (1 -> back, 2 -> front)
			 break;}
		case 15: {OutputBool = (((detID1_input>>14)&0xF) == 4) && (((detID2_input>>14)&0xF) == 4); //Wheel TEC 
			 break;}
		case 16: {OutputBool = (((detID1_input>>5)&0x7) == 3)  && (((detID2_input>>5)&0x7) == 3); //Ring TEC
			 break;}
		case 17: {OutputBool = ( (((detID1_input>>25)&0x7) == 3) && (((detID2_input>>25)&0x7) == 3) ); //All TIB
			  break;}
	 	case 18: {OutputBool = ( (((detID1_input>>25)&0x7) == 5) && (((detID2_input>>25)&0x7) == 5) ); //All TOB
			 break;}
		case 19: {OutputBool = ( (((detID1_input>>13)&0x3) == 1) && (((detID2_input>>13)&0x7) == 1) ) ||
				               ( (((detID1_input>>13)&0x3) == 2) && (((detID2_input>>13)&0x7) == 2) ) ||
				               ( (((detID1_input>>11)&0x3) == 2) && (((detID2_input>>11)&0x3) == 2) ) || 
				               ( (((detID1_input>>9)&0x3) == 2) && (((detID2_input>>9)&0x3) == 2) )   ||
			                   ( (((detID1_input>>7)&0x3) == 1) && (((detID2_input>>7)&0x3) == 1) )   ||
			 	               ( (((detID1_input>>7)&0x3) == 2) && (((detID2_input>>7)&0x3) == 2) )   ||
				               ( (((detID1_input>>2)&0x1F) == 5) && (((detID2_input>>2)&0x1F) == 5) ) ||
				               ( (((detID1_input>>0)&0x3) == 0) && (((detID2_input>>0)&0x3) == 0) ) ||
				               ( (((detID1_input>>0)&0x3) == 1) && (((detID2_input>>0)&0x3) == 1) ) ||
				               ( (((detID1_input>>0)&0x3) == 2) && (((detID2_input>>0)&0x3) == 2) ); //All TID 
			 break;}
		case 20: {OutputBool =  ( (((detID1_input>>18)&0x3) == 1) && (((detID2_input>>18)&0x3) == 1) ) ||
                                ( (((detID1_input>>18)&0x3) == 2) && (((detID2_input>>18)&0x3) == 2) ) ||
				                ( (((detID1_input>>14)&0xF) == 4) && (((detID2_input>>14)&0xF) == 4) ) ||
				                ( (((detID1_input>>12)&0x3) == 1) && (((detID2_input>>12)&0x3) == 1) ) ||
                                ( (((detID1_input>>12)&0x3) == 2) && (((detID2_input>>12)&0x3) == 2) ) || 
				                ( (((detID1_input>>8)&0xF) == 4) && (((detID2_input>>8)&0xF) == 4) ) ||
				                ( (((detID1_input>>5)&0x7) == 3) && (((detID2_input>>5)&0x7) == 3) ) ||
				                ( (((detID1_input>>2)&0x7) == 3) && (((detID2_input>>2)&0x7) == 3) ) || 
				                ( (((detID1_input>>0)&0x3) == 1) && (((detID2_input>>0)&0x3) == 1) ) ||
				                ( (((detID1_input>>0)&0x3) == 2) && (((detID2_input>>0)&0x3) == 2) ) ||
				                ( (((detID1_input>>0)&0x3) == 3) && (((detID2_input>>0)&0x3) == 3) ); //All TEC
			 break;}
		case 21: {OutputBool = (((detID1_input>>20)&0xF) == 4) && (((detID2_input>>20)&0xF) == 4); //pixel barrel (phase 1)
             break;}
		case 22: {OutputBool = (((detID1_input>>18)&0xF) == 4) && (((detID2_input>>18)&0xF) == 4); //pixel endcap disk (phase 1)
             break;}
        case 23:{OutputBool =( (((detID1_input>>9)&0x3) == 1) && (((detID2_input>>9)&0x3) == 1) );  // TID Ring 1
             break;}
        case 24:{OutputBool =( (((detID1_input>>9)&0x3) == 2) && (((detID2_input>>9)&0x3) == 2) );   // TID Ring 2
             break;}
        case 25:{OutputBool =( (((detID1_input>>9)&0x3) == 3) && (((detID2_input>>9)&0x3) == 3) ); //TID Ring 3
             break;}
        case 26:{OutputBool =(((detID1_input>>5)&0x7) == 1)  && (((detID2_input>>5)&0x7) == 1); // TEC Ring 1
            break;}
        case 27:{OutputBool =(((detID1_input>>5)&0x7) == 2)  && (((detID2_input>>5)&0x7) == 2); // TEC Ring 2
             break;}
        case 28:{OutputBool =(((detID1_input>>5)&0x7) == 3)  && (((detID2_input>>5)&0x7) == 3); // TEC Ring 3
             break;}
        case 29:{OutputBool =(((detID1_input>>5)&0x7) == 4)  && (((detID2_input>>5)&0x7) == 4); // TEC Ring 4
             break;}
        case 30:{OutputBool =(((detID1_input>>5)&0x7) == 5)  && (((detID2_input>>5)&0x7) == 5); // TEC Ring 5
             break;}
        case 31:{OutputBool =(((detID1_input>>5)&0x7) == 6)  && (((detID2_input>>5)&0x7) == 6); // TEC Ring 6
             break;}
        case 32:{OutputBool =(((detID1_input>>5)&0x7) == 7)  && (((detID2_input>>5)&0x7) == 7); // TEC Ring 7
             break;}
	}

	return OutputBool;

  }};

  //Function for expressing the hit resolution in either centimeters or pitch units.
  auto Pitch_Function{[&Unit_Int](const float& pitch, const float& input){

	float InputOverPitch = input/pitch;
  	return InputOverPitch;

  }};
  
  auto Pitch_Function_ext{[&Unit_Int](const float& pitch, const float& input){

	float InputOverPitch = input*1;
    return InputOverPitch;

  }};

  //Defining columns needed for the unit conversion into pitch units, and applying the filter for the subdetector
  auto dataframe = d.Define("hitDX_OverPitch", Pitch_Function, {"pitch1", "hitDX"})
	 	    .Define("trackDX_OverPitch", Pitch_Function, {"pitch1", "trackDX"})
		    .Define("trackDXE_OverPitch", Pitch_Function, {"pitch1", "trackDXE"})
		    .Define("StripErrorSquared1_OverPitch", Pitch_Function, {"pitch1", "StripErrorSquared1"})
		    .Filter(SubDet_Function, {"detID1", "detID2"}, "Subdetector filter");
  
  //Implementing selection criteria that were not implemented in HitResol.cc
  auto PairPathCriteriaFunction{[&RegionInt](const float& pairPath_input){

	if((RegionInt > 0 && RegionInt < 5) || (RegionInt > 7 || RegionInt < 13) || (RegionInt == 17) || (RegionInt == 18)){return abs(pairPath_input) < 7;} //for TIB and TOB
	else if(RegionInt == 21 || RegionInt == 22){return abs(pairPath_input) < 2;} //for pixels
	else{return abs(pairPath_input) < 20;}//for everything else (max value is 15cm so this will return all events anyway)
  }};

  auto MomentaFunction{[&RegionInt](const float& momentum_input){

	if(RegionInt == 21 || RegionInt == 22){return momentum_input > 5;} //pixels
	else{return momentum_input > 3;} //strips
  }};

  auto dataframe_filtered_ = dataframe.Filter(PairPathCriteriaFunction, {"pairPath"}, "Pair path criterion filter")
				     .Filter(MomentaFunction, {"momentum"}, "Momentum criterion filter")
			         .Filter("trackChi2 >= 0.001", "chi2 criterion filter")
				     .Filter("numHits >= 6", "numHits filter")
				     .Filter("trackDXE < 0.0025", "trackDXE filter");
				     //.Filter("(clusterW1 == clusterW2) && clusterW1 <= 4 && clusterW2 <= 4", "cluster filter");
  // cluster width in number of strips 
  string cluster_cut= "";
  if(cluster_width =="1"){cluster_cut = "(clusterW1 == clusterW2) && clusterW1 == 1 && clusterW2 == 1";}
  else if(cluster_width =="2"){cluster_cut = "(clusterW1 == clusterW2) && clusterW1 == 2 && clusterW2 == 2";}
  else if(cluster_width =="3"){cluster_cut = "(clusterW1 == clusterW2) && clusterW1 == 3 && clusterW2 == 3";}
  else if(cluster_width =="4"){cluster_cut = "(clusterW1 == clusterW2) && clusterW1 == 4 && clusterW2 == 4";}
  else {cluster_cut = "(clusterW1 == clusterW2) && clusterW1 > 4 && clusterW2 > 4";}

  auto dataframe_filtered = dataframe_filtered_.Filter(cluster_cut, "cluster filter");
  //Creating histograms for the difference between the two hit positions, the difference between the two predicted positions and for the double difference
  //hitDX = the difference in the hit positions for the pair
  //trackDX =  the difference in the track positions for the pair 

  auto HistoName_DoubleDiff = "DoubleDifference_" + region + "_clusterW" + cluster_width ;
  auto HistoName_HitDX = "HitDX_" + region + "_clusterW" + cluster_width ;
  auto HistoName_TrackDX = "TrackDX_" + region + "_clusterW" + cluster_width ; 
  auto HistoName_TrackDXE = "TrackDXE_" + region + "_clusterW" + cluster_width ;
  auto HistoName_CPEEstimated = "CPEEstimated_" + region + "_clusterW" + cluster_width ;

  auto h_DoubleDifference = dataframe_filtered.Define(HistoName_DoubleDiff, DoubleDiffString).Histo1D({HistoName_DoubleDiff.c_str(), HistoName_DoubleDiff.c_str(), 60, -0.5, 0.5}, HistoName_DoubleDiff); 
  auto h_hitDX = dataframe_filtered.Define(HistoName_HitDX, HitDXString).Histo1D(HistoName_HitDX);
  auto h_trackDX = dataframe_filtered.Define(HistoName_TrackDX, TrackDXString).Histo1D(HistoName_TrackDX);
  auto h_trackDXE = dataframe_filtered.Define(HistoName_TrackDXE, TrackDXEString).Histo1D(HistoName_TrackDXE);
  auto h_cpeEstimated = dataframe_filtered.Define(HistoName_CPEEstimated, CPEEstimatedString).Histo1D(HistoName_CPEEstimated);

  //Applying gaussian fits, taking the resolutions and squaring them
  h_DoubleDifference->Fit("gaus");
  
  auto double_diff_StdDev = h_DoubleDifference->GetStdDev();
  auto hitDX_StdDev = h_hitDX->GetStdDev();
  auto trackDX_StdDev = h_trackDX->GetStdDev();
  auto trackDXE_Mean = h_trackDXE->GetMean();
  auto cpeEstimated_squared = h_cpeEstimated->GetMean();
  
  auto sigma2_MeasMinusPred = pow(double_diff_StdDev, 2);
  auto sigma2_Meas = pow(hitDX_StdDev, 2);
  auto sigma2_Pred = pow(trackDX_StdDev, 2); 
  auto sigma2_PredError = pow(trackDXE_Mean, 2);
  auto sigma2_estimated = sqrt(cpeEstimated_squared);

  DoubleDifferenceVector.push_back(sigma2_MeasMinusPred);
  HitDXVector.push_back(sigma2_Meas);
  TrackDXVector.push_back(sigma2_Pred);
  TrackDXEVector.push_back(sigma2_PredError);
  CPEEstimatedVector.push_back(sigma2_estimated);

  //Saving the histograms with gaussian fits applied to an output root file
  TFile * output = new TFile(GaussianFitsFileName.c_str(), "UPDATE");

  h_DoubleDifference->Write();
  h_hitDX->Write();
  h_trackDX->Write();
  h_trackDXE->Write();
  h_cpeEstimated->Write();

  output->Close();
  
  //Calculating the hit resolution;
  auto numerator = sigma2_MeasMinusPred - sigma2_PredError;
  auto HitResolution = sqrt( numerator/2 );
  HitResolutionVector.push_back(HitResolution);

  //Printing the resolution 
  std::cout << "Hit resolution for tracker region " << region << " and of cluster width " <<  cluster_width << ":  "<< HitResolution << suffix << std::endl;
  std::cout << "Strip CPE parametrisation for tracker region " << region << " and of cluster width " <<  cluster_width << ":  "<< sigma2_estimated << suffix << std::endl;
  std::cout << "====================================================================================" << std::endl;
  //std::cout << '\n' << std::endl;

  //Cut flow report
  auto allCutsReport = d.Report();
  std::ofstream CutFlowReport;

  CutFlowReport.open(CutFlowReportString.c_str());

  for(auto&& cutInfo: allCutsReport){
  	CutFlowReport << cutInfo.GetName() << '\t' << cutInfo.GetAll() << '\t' << cutInfo.GetPass() << '\t' << cutInfo.GetEff() << " %" << std::endl;
  }

}

void Resolutions(const int& Unit_Int, const int& UL, const string& InputFileString, const string& InputFilePath, const bool& DOESEXIST){

  vector<std::string> LayerNames = {"TIB_L1",   "TIB_L2",   "TIB_L3",   "TIB_L4",
				                    "Side_TID", "Wheel_TID","Ring_TID", 
                                    "TOB_L1",   "TOB_L2",   "TOB_L3",   "TOB_L4",  "TOB_L5",  "TOB_L6",   
                                    "Side_TEC", "Wheel_TEC","Ring_TEC", 
				                    "TIB_All",  "TOB_All",  "TID_All",  "TEC_All",
				                    "Pixel_Barrel", "Pixel_EndcapDisk",
                                    "TID_R1",   "TID_R2",   "TID_R3", 
                                    "TEC_R1",   "TEC_R2",   "TEC_R3",   "TEC_R4",   "TEC_R5",   "TEC_R6",   "TEC_R7"};
  
  vector<std::string> ClusterWidth = { "1", "2", "3", "4", "5"};
  for( int j =0; j < ClusterWidth.size(); j++ ){
    std::cout << "================================================================" << std::endl;
    std::cout << "  values of 1D Gaussian Fit for Strips with "<< ClusterWidth.at(j) << " cluster size" << std::endl;
    std::cout << "================================================================" << std::endl;
    for( int i = 0; i < LayerNames.size(); i++){ResolutionsCalculator(LayerNames.at(i), Unit_Int, UL, InputFileString, ClusterWidth.at(j));}
  
    std::ofstream HitResoTextFile;
    HitResoTextFile.open(HitResoFileName);
    auto Width = 28;
    
    HitResoTextFile << std::right << "Layer " << std::setw(Width) << " Resolution " << std::setw(Width) << " sigma2_HitDX " << std::setw(Width) << " sigma2_trackDX " << std::setw(Width) << " sigma2_trackDXE " << std::setw(Width) << " sigma2_DoubleDifference " << std::setw(Width) << " CPE current parametrisation "<< std::endl;
    
    for(int i = 0; i < HitResolutionVector.size(); i++){
        HitResoTextFile << std::right << LayerNames.at(i) << std::setw(Width) << HitResolutionVector.at(i) << std::setw(Width) << HitDXVector.at(i)  << std::setw(Width) << TrackDXVector.at(i) << std::setw(Width) << TrackDXEVector.at(i) << std::setw(Width) << DoubleDifferenceVector.at(i) << std::setw(Width) << CPEEstimatedVector.at(i) << std::endl;
    
    }
    
    if (DOESEXIST){
        /* Directory exists. */
        string cmd = "mv ";
        std::cout << " /HitResolutionValues, /GaussianFits , /CutFlowReports exists ! " << std::endl;
        cmd = cmd + "CutFlowReport_* "+InputFilePath +"/CutFlowReports/; mv HitResolutionValues_* "+ InputFilePath + "/HitResolutionValues/; mv GaussianFits_* "+ InputFilePath +"/GaussianFits/;";
        std::cout << "cmd :" << cmd << std::endl; 
        // Convert string to const char * as system requires
        // parameter of type const char *
        const char *command1 = cmd.c_str();
        system(command1);} 
    else{ 
        /* Directory does not exist. */
        string cmd = "mkdir ";
        cmd = cmd + InputFilePath +"/HitResolutionValues; mkdir " + InputFilePath+ "/GaussianFits; mkdir "+ InputFilePath +"/CutFlowReports; mv CutFlowReport_* "+InputFilePath +"/CutFlowReports/; mv HitResolutionValues_* "+ InputFilePath + "/HitResolutionValues/; mv GaussianFits_* "+ InputFilePath +"/GaussianFits/;";
        std::cout << "cmd :" << cmd << std::endl; 
        const char *command2 = cmd.c_str();
        system(command2);
        }
    }
}
