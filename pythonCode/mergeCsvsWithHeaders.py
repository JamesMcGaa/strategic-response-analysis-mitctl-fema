# This python script merges files together in a folder.  
import os
import os.path
import sys
import numpy
import time
import glob
import shutil

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
      #print 'about to wait'
      randWaitTime = numpy.random.uniform() * 10
      #print 'rnadom wait time + ' + str(randWaitTime)
      time.sleep(randWaitTime)
      d2 = os.path.dirname(f)
      if not os.path.exists(d2):
        os.makedirs(d2)



MASTER_FILE_PATH = 'C:/Users/jaa26/Dropbox/Academic/Papers/HumIndex/Jason/PythonCoding/DisasterAnalysis2.0/outputData/'
OUTPUT_FOLDER_STUB = 'analyze_004_collaborate/'
out_folder = MASTER_FILE_PATH + OUTPUT_FOLDER_STUB


os.chdir( MASTER_FILE_PATH )


# FOLDER_LIST = ['output_116_countryAbleRespond_100',
               # 'output_117_countryAbleRespond_1000',
               # 'output_118_countryAbleRespond_10000',
               # 'output_119_countryAbleRespond_100000',
               # 'output_120_countryAbleRespond_1000000',
               # 'output_121_countryAbleRespond_10000000'
              # ]


FOLDER_LIST = ['output_123_collaborateBreakdown_EqualNum_cost_002',
               'output_124_collaborateBreakdown_EqualNum_cost_005',
               'output_125_collaborateBreakdown_EqualNum_cost_010',
               'output_126_collaborateBreakdown_EqualNum_cost_020',
               'output_127_collaborateBreakdown_EqualNum_cost_050',
               'output_128_collaborateBreakdown_EqualNum_cost_100',
               'output_129_collaborateBreakdown_EqualNum_cost_200',
               'output_130_collaborateBreakdown_EqualNum_cost_500',
               'output_131_collaborateBreakdown_EqualNum_cost_001'               
              ]

              
              
              
ensure_dir( MASTER_FILE_PATH + OUTPUT_FOLDER_STUB)

folder_list_master = []



file_list = []
for file in glob.glob(MASTER_FILE_PATH + FOLDER_LIST[0] + "/" + "*"):
  if file.find('.csv') >= 0:
    if file.find('\\') >= 0:
      file = file[file.find('\\') + 1:]
    elif file.find('/') >= 0:  
      file = file[file.find('/') + 1:]
    file_list.append(file)  



for file in file_list:
  print ''
  print 'working on', file
  k = 0
  for folder in FOLDER_LIST:
    print '    about to copy', folder
    if k == 0:
      shutil.copyfile(folder + '/' + file, out_folder + file)
    else:
      fmain = open(out_folder + file, "at")
      fsnippet = open(folder + '/' + file, "rt")
      for line in fsnippet.readlines()[1:]:
        fmain.write(line )
      fsnippet.close()
      fmain.close() 
    k += 1      
  
print 'done'    
"""  
k = 0  
for file in file_list_master:
  file_list = []
  for file in glob.glob(folder + '/*.csv'):
    if file.find('\\') >= 0:
      file = file[file.find('\\') + 1:]
    elif file.find('/') >= 0:  
      file = file[file.find('/') + 1:]
    file_list_sub_csv.append(file)  
    
  
  if k == 0:
    for file in file_list_sub_csv:
      shutil.copyfile(folder + '/' + file, file)
  else:
    for file in file_list_sub_csv:
      fmain = open(file, "at")
      fsnippet = open(folder + '/' + file, "rt")
      for line in fsnippet.readlines()[1:]:
        fmain.write(line )
      fsnippet.close()
      fmain.close()
  os.rename(folder, 'archive/' + folder)
  k += 1

print 'done'  
  
"""  