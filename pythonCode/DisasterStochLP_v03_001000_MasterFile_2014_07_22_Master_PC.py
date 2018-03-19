# This imports a lot of other packages, 

#python DisasterStochLP_v01_a_MasterFile_2013_07_08.py


import os
import sys
    #import random
import math
import numpy
import pickle as pickle
#import subprocess
#from pylab import *
#from statlib import stats
#from pulp import *
import csv
#import shutil
#import fnmatch
from copy import deepcopy
#from scipy.stats import *
import time
import datetime
# from scipy.stats import truncnorm
from datetime import *
from gurobipy import *
#from Pycluster import *
import matplotlib
import matplotlib.pyplot as plt
import os.path


runOnPCOrLionXF = 'MyPC' # 'LionXF' 'MyPC'
myLionThreads = 1

# This dictates the suffix for the param file, the outerloop file, and the output folder
myPBSBatch_outputFolder = '_016_testRun'
myPBSBatch_paramSuffix = 'Master'
myPBSBatch_outerLoopSuffix = 'Master'
myPBSBatch_runDescription = 'testRun'

gurobipy.setParam("OutputFlag",0)
gurobipy.setParam("NodefileStart", 0.5)
if runOnPCOrLionXF == 'MyPC':
  gurobipy.setParam("Threads", 1)
  gurobipy.setParam("Method", 1)
  gurobipy.setParam("NodefileDir", "C:/Temp/GurobiNodeFiles/")
  myMasterFilePath = "C:/Users/rothkopf/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/"
elif runOnPCOrLionXF == 'LionXF':
  gurobipy.setParam("Threads", myLionThreads)
  gurobipy.setParam("NodefileDir", '/gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/JunkNodeFiles/')
  myMasterFilePath = '/gpfs/home/jaa26/work/humanJarrod/pythonCode/version01/'

# Where all of your scripts are, and the parent folder for your input and output files
#    It may matter which way the slashes go, if it doesn't work, try the forward slash "/"

#myMasterFilePath = '/gpfs/home/jaa26/work/humanJarrod/index01/'

print 'Master File Path'
print myMasterFilePath



os.chdir( myMasterFilePath )


# ------------------------------------------------------------------------------
# Environment
# Where is your data stored, and where do you want new data saved
codePath = myMasterFilePath + 'pythonCode/'
#outputPath = myMasterFilePath + 'outputData/' + "output04_20140827_10e3_respond/"
#outputPath = myMasterFilePath + 'outputData/' + "output05_test/"
outputPath = myMasterFilePath + 'outputData/' + 'output' + myPBSBatch_outputFolder + "/"
#inputFilesFolderParent = myMasterFilePath + "inputDataSmall3FC/"
#inputPath = myMasterFilePath + 'inputData/' + 'inputDataTest02/' 
#inputPath = myMasterFilePath + 'inputData/' + 'inputData02_Pacific/' 
inputPath = myMasterFilePath + 'inputData/' + 'inputData03_US/' 
inputPathPickle_Cost = inputPath + 'pickled/' + myPBSBatch_outputFolder + "/"
inputPathPickle_Beta = inputPath + 'pickled/'



# setParam(GRB.Param.Method, 0)
# setParam(GRB.Param.MIPGap, 0)

createLargeDictionariesFromScratch_Cost = True
createLargeDictionariesFromScratch_Beta = False


writeOutFlowFile = True
writeOutDualsByWarehouseAndDisaster = False


# ------------------------------------------------------------------------------
# A few basic functions
execfile(codePath + "DisasterStochLP_v03_002000_GeneralFunctions_2014_07_22.py")
ensure_dir(outputPath)

# ------------------------------------------------------------------------------
# Parameters

execfile(codePath + "DisasterStochLP_v03_004000_Parameters_2014_07_22" + "__" + myPBSBatch_paramSuffix + ".py")




# ------------------------------------------------------------------------------
# Run some files
execfile(codePath + "DisasterStochLP_v03_005000_ReadInFiles_2014_07_22_b.py")
#raise NameError('STOPPPPP')


execfile(codePath + "DisasterStochLP_v03_003000_StochLPFunc_2014_07_22.py")
#execfile(codePath + "DisasterStochLP_v02_k_OutLoopIterate_2014_07_22.py")
execfile(codePath + "DisasterStochLP_v03_006000_OutLoopIterate_2014_07_22" + "__" + myPBSBatch_outerLoopSuffix + ".py")




#execfile(codePath + "DisasterStochLP_v02_d02_StochLPFunc_2014_07_22.py")

print 'You successfully finished'





















