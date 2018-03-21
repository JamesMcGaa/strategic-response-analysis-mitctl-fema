#------------------------------------------------------------------------------
# Define some parameters
n_itemIter = 'BlanketGen'

## This determines whether the initial inventories are fixed, or whether they can be shifted to be "optimal"
#areInitialSuppliesVariables_Flag = 0

# Whether you want to calculate the beta's for the demand based on the month, i.e., need more blankets in winter than in summer.
# If this is set to 0, it uses the default month-agnostic version of the needs for each item.
careAboutMonthDemand_Beta_01 = 1
# Set t_month_Disaster to -1 if you don't care about the month.  This affects what disasters are included.
t_month_Disaster = -1
# If you do care about the month, you may want to look at each month on its own, or average several months'
#    disasters together
numMonthsToAvg = 3







#1990 to 2014 is entire range
minYearSubset = 1900
maxYearSubset = 2017

myRange = 10
myStep = 1

yearSubset_Set = [(i, i + myRange) for i in range(1980, 2014 - myRange, myStep)]


# If this is zero, then the item can only be reallocated in the current warehouses.
#    Otherwise, if it's 1, the item can be help in any warehouse that exists.
#  ON 9/13 THIS DOES NOT WORK SO WELL!!!!
#      I've changed the ReadInFiles code to use a subset of warehouses.  As such, i've
#      already added zeroes into that file for the subset of warehouses I want to keep.
#      Leaving this at zero is okay: it uses all warehouses that are not dups.  Changing it to 
#      1 right now would include all the dupes.  As of now, I do NOT have an option
#      that would drop the warehouses with zero inventory for each item.
#DO NOT CHANGE
expandWhichWarehousesCarryItem_01 = 0
#DO NOT CHANGE


# Efficient frontier parameters
plotEffFront_01 = 0
myNumEffFrontPoints = 10
optimizeTag = 'Cost'
constrainerTag = 'Time'
initiSupplyVar_TempFlag = 'Optimal'



# What to run parameters
myCostsToIterate_param = ['Cost', 'Time']
#myCostsToIterate_param = ['Time']
myCostsToCompare_param = ['Cost', 'Time', 'pureKM']
#myLPInitialSuppliesVariables_Flag_param = ['Optimal', 'Actual', 'Worst']
myLPInitialSuppliesVariables_Flag_param = ['Optimal', 'Actual']
#myLPInitialSuppliesVariables_Flag_param = ['Actual']
#myLPInitialSuppliesVariables_Flag_param = ['Optimal']

# This is only referenced if 'Actual' is NOT in the myLPInitialSuppliesVariables_Flag_param
#    otherwise, the actual inventory is used
initialInventoryToTest = 1000


writeOverOrAppendFiles = 'append'
# 'writeOver'  # Erase the old file.
# 'append'      # If the old file exists, it'll check the header.  If a match, append.
#------------------------------------------------------------------------------
# Here we assign many of the parameters from the master file:





# Here we do the thing where we have a cutoff on the time required.
minTimeRequiredToRespond = 1e6



#------------------------------------------------------------------------------
# Where I Do the loop iterations

for n_itemIter in itemNamesInventory:
    #for n_itemIter in ['BlanketGen']:
    #for (minYearSubset, maxYearSubset) in yearSubset_Set:
    execfile(os.path.join(codePath,'InnerLoopMakeSubsets.py'))
    execfile(os.path.join(codePath,'WriteOutFiles.py'))

"""
for n_itemIter in itemNamesInventory:
  for (minYearSubset, maxYearSubset) in [(i, i + 9) for i in range(1990, 2006, 1)]:
    execfile(codePath + 'DisasterStochLP_v02_m_InnerLoopMakeSubsets_2014_07_22.py')
    execfile(codePath + 'DisasterStochLP_v02_p_WriteOutFiles_2014_07_22.py') 
"""

                  




