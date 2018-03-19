# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:33:30 2018

@author: alr06kc
"""
import csv
import pandas
from datetime import datetime
import random

print random.randint(0,120)

#myMasterFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/pythonCodeGetData/"
#depotWhichToUseReadInvFileName = '130628RawDataEMDAT.csv'
#
#disLocationHead = ['StartDate', 'EndDate', 'Country', 'Location', 'Type', 'SubType', 'Name', 'TotalKilled', 'TotalAffected', 'TotalDamage', 'DisasterNumber']
#disLocations = pandas.read_csv(myMasterFilePath + depotWhichToUseReadInvFileName, names=disLocationHead )
#disLocations['EndDate'] =  pandas.to_datetime(disLocations['EndDate'],format=)
#df['Day'] = pd.to_datetime(df['Day'])

str_date  = '17/8/1989'
print str_date

date_date = datetime.strptime(str_date, "%d/%m/%Y")
#datetime.strptime(str_date, "%d/%m/%y").strptime('%Y-%m-%d')
print date_date

myMasterFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/pythonCodeGetData/"
depotWhichToUseReadInvFileName = 'disasterlocations.csv'
print str(datetime.now()) + ' -- Reading ASCII disaster locations'
disLocationHead = ['StartDate', 'EndDate', 'Country', 'Location', 'Type', 'SubType', 'Name', 'TotalKilled', 'TotalAffected', 'TotalDamage', 'DisasterNumber']
disLocations = pandas.read_csv(myMasterFilePath + depotWhichToUseReadInvFileName, names=disLocationHead )

#%disLocations['EndDateDate'] = pandas.to_datetime(disLocations['EndDate'])
#%print disLocations.dtypes

disLocations['EndDate'] = pandas.to_datetime(disLocations['EndDate'], errors='coerce', dayfirst=True)
print disLocations.dtypes
disLocationsFiltered = disLocations[(disLocations.EndDate > '1990-01-01')]
#for i in range(len(disLocations)):
#    str_date = disLocations.iloc[(i,1)]
#    date_date = datetime.strptime(str_date, "%d/%m/%Y")
#    disLocations.at[(i,'EndDate')] = date_date


def ANewFunc(Parameter):
    return Parameter * 2

print ANewFunc(5)
