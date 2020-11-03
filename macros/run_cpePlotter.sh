#!/bin/bash

DIRBASE="$CMSSW_BASE/src/SiStripCPE/CPEanalyzer"

mkdir $DIRBASE/plots/slurmOutput_v3/

root -l -b $DIRBASE/macros/CPEPlotter.C

ps2pdf $DIRBASE/plots/slurmOutput_v3/testSummary.ps $DIRBASE/plots/slurmOutput_v3/testSummary.pdf

