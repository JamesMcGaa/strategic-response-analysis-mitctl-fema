# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 13:00:22 2018

@author: Alex Rothkopf
"""

import csv
import pandas
import time
from datetime import datetime

#AXR: Set variables
indent = '       '                     #AXR: This is just to have a nice output
myDropBoxFilePath = "C:/Users/alr06kc/Dropbox (MIT)/" #AXR: Change this path if code runs on a different machine
myMasterFilePath = myDropBoxFilePath + "Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/pythonCodeGetData/"
myOutputFilePath = myDropBoxFilePath + "Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/inputData/inputData03_US/"
betaConversionsOutputFileName = 'betaItemConversions.csv'
invData = 'depotInventoryData.csv'
#AXR: End of setting variables


#Item,Disaster Type,Month,gglCountry,PersonsPerItem


def writeBetaConvFile():
    print str(datetime.now()) + ' -- Reading source data'
    itemList1 = pandas.read_csv(myOutputFilePath + invData, usecols=[0])
    itemList1.drop_duplicates(subset='ItemName', inplace=True)
    itemList1.rename(columns={'ItemName':'Item'},inplace=True)
    itemList1.reset_index(drop=True, inplace=True)
    itemList1.insert(loc=1, column='Disaster Type', value='DEFAULT')
    itemList1.insert(loc=2, column='Month', value='DEFAULT')
    itemList1.insert(loc=3, column='gglCountry', value='DEFAULT')
    itemList1.insert(loc=4, column='PersonsPerItem', value=2.5)
    itemList2 = itemList1.copy(deep=True)
    itemList2.loc[itemList2['PersonsPerItem'] > 0, 'Month'] = -1
    itemList1 = itemList1.append(itemList2)
    print str(datetime.now()) + ' -- writing csv: ' + betaConversionsOutputFileName
    itemList1.to_csv(myOutputFilePath + betaConversionsOutputFileName, index=False)
    print indent + ' ... success'
    


#-------

writeBetaConvFile()