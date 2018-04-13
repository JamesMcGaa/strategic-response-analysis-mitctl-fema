import os
import sys
import math
import numpy
import pickle as pickle
import csv
from copy import deepcopy
import time
import datetime
from datetime import *
from gurobipy import *
import matplotlib
import matplotlib.pyplot as plt
import os.path
#import random
#import subprocess
#from pylab import *
#from statlib import stats
#from pulp import *
#import shutil
#import fnmatch
#from scipy.stats import *
#from scipy.stats import truncnorm
#from Pycluster import *


runOnPCOrLionXF = 'MyPC' # 'LionXF' 'MyPC'
myLionThreads = 1

# This dictates the suffix for the param file, the outerloop file, and the output folder
myPBSBatch_outputFolder = '_017_testRun'
myPBSBatch_paramSuffix = 'Master'
myPBSBatch_outerLoopSuffix = 'Master'
myPBSBatch_runDescription = 'testRun'

gurobipy.setParam("OutputFlag",0)
gurobipy.setParam("NodefileStart", 0.5)
if runOnPCOrLionXF == 'MyPC':
  gurobipy.setParam("Threads", 1)
  gurobipy.setParam("Method", 1)
  gurobipy.setParam("NodefileDir", "C:/Temp/GurobiNodeFiles/")
  myMasterFilePath = os.getcwd()
  
elif runOnPCOrLionXF == 'LionXF':
  gurobipy.setParam("Threads", myLionThreads)
  gurobipy.setParam("NodefileDir", '/gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/JunkNodeFiles/')
  myMasterFilePath = '/gpfs/home/jaa26/work/humanJarrod/pythonCode/version01/'


# Where all of your scripts are, and the parent folder for your input and output files
myMasterFilePath = os.path.dirname(os.getcwd()) #Parent code location
codePath = os.getcwd() #Current location
print 'Master File Path'
print myMasterFilePath
os.chdir(myMasterFilePath)


print "I added some stuff here"

# ------------------------------------------------------------------------------
# Environment
# Where is your data stored, and where do you want new data saved
outputPath = os.path.join(myMasterFilePath, 'outputData', 'output' + myPBSBatch_outputFolder)

inputPath = os.path.join(myMasterFilePath, 'inputData/' + 'inputData03_US/' )
inputPathPickle_Cost = os.path.join(inputPath, 'pickled/' + myPBSBatch_outputFolder + "/a")
inputPathPickle_Beta = inputPath + 'pickled/'



# setParam(GRB.Param.Method, 0)
# setParam(GRB.Param.MIPGap, 0)

createLargeDictionariesFromScratch_Cost = True
createLargeDictionariesFromScratch_Beta = False


writeOutFlowFile = True
writeOutDualsByWarehouseAndDisaster = False


# ------------------------------------------------------------------------------
# A few basic functions
execfile(os.path.join(codePath,"GeneralFunctions.py" )) #Can add .replace("/","\\") if not working
ensure_dir(outputPath)

# ------------------------------------------------------------------------------
# Parameters
execfile(os.path.join(codePath,"Parameters.py" ))

# ------------------------------------------------------------------------------
# Run some files
execfile(os.path.join(codePath,"ReadInFiles.py" ))
execfile(os.path.join(codePath,"StochLPFunc.py" ))
execfile(os.path.join(codePath,"OutLoopIterate.py" ))


print 'You successfully finished'