#qstat -u jaa26 | grep "jaa26" | cut -d"." -f1 | xargs qdel

import os
import os.path
import sys
import numpy
import time


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


SKELETON_FILE_PATH = "C:/Users/jaa26/Dropbox/Academic/Papers/HumIndex/Jason/PythonCoding/DisasterAnalysis2.0/pythonCode/"
SKELETON_FILE_PATH_OUT = "C:/Users/jaa26/Dropbox/Academic/Papers/HumIndex/Jason/PythonCoding/DisasterAnalysis2.0/outputData/"
#SKELETON_FILE_PATH = "/gpfs/work/j/jaa26/amazon/paper2/2015-06-08/code/"

SKELETON_FILE_NAME_MASTER = "DisasterStochLP_v02_a01_MasterFile_2014_07_22_Skel_01.py"
SKELETON_FILE_NAME_PARAM = "DisasterStochLP_v02_f_Parameters_2014_07_22__Skel_01.py"
SKELETON_FILE_NAME_OUTER = "DisasterStochLP_v02_k_OutLoopIterate_2014_07_22__Skel_01.py"

SKELETON_OUT_FOLDER_STUB = "output_"
SKELETON_OUT_FOLDER_COUNT_START = 116

# First the description, then the set of 2-element lists of PARAM replacement 
#    words, then set of 2-element lists of OUTERLOOP replacement words
PARAM_VAR_SET = [
                  [
                    'countryAbleRespond_100',
                    [
                      ['GENFILE_CNTRYABLETORESPONDFILENAME', 'countryAbilityToRespond_100.csv']
                    ],
                    [
                    ],
                  ],
                  [
                    'countryAbleRespond_1000',
                    [
                      ['GENFILE_CNTRYABLETORESPONDFILENAME', 'countryAbilityToRespond_1000.csv']
                    ],
                    [
                    ],
                  ],
                  [
                    'countryAbleRespond_10000',
                    [
                      ['GENFILE_CNTRYABLETORESPONDFILENAME', 'countryAbilityToRespond_10000.csv']
                    ],
                    [
                    ],
                  ],
                  [
                    'countryAbleRespond_100000',
                    [
                      ['GENFILE_CNTRYABLETORESPONDFILENAME', 'countryAbilityToRespond_100000.csv']
                    ],
                    [
                    ],
                  ],
                  [
                    'countryAbleRespond_1000000',
                    [
                      ['GENFILE_CNTRYABLETORESPONDFILENAME', 'countryAbilityToRespond_1000000.csv']
                    ],
                    [
                    ],
                  ],
                  [
                    'countryAbleRespond_10000000',
                    [
                      ['GENFILE_CNTRYABLETORESPONDFILENAME', 'countryAbilityToRespond_10000000.csv']
                    ],
                    [
                    ],
                  ]             
                ]  
                    



print 'len(PARAM_VAR_SET) = ', len(PARAM_VAR_SET )


#SKELETON_OUT_FOLDER = "output_0020_chkSmp"

#ensure_dir(skeleton_scripts_folder)


for i_output in range(len(PARAM_VAR_SET)):
  desc_tmp = PARAM_VAR_SET[i_output][0]
  num_desc = '%03d_%s' % (i_output + SKELETON_OUT_FOLDER_COUNT_START, desc_tmp)
  output_data = SKELETON_FILE_PATH_OUT + SKELETON_OUT_FOLDER_STUB + num_desc
  ensure_dir(output_data)
  output_scripts = output_data + '/scripts/'
  ensure_dir(output_scripts)
  file_name_tmp_master = output_scripts + 'skeleton_master_' + num_desc + '.py'
  file_name_tmp_param = output_scripts + 'skeleton_param_' + num_desc + '.py'
  file_name_tmp_outer = output_scripts + 'skeleton_outer_' + num_desc + '.py'
  
  ensure_dir(SKELETON_FILE_PATH + 'tmpJunk/')
  fin = open(SKELETON_FILE_PATH + SKELETON_FILE_NAME_MASTER, "rt")
  fout = open(file_name_tmp_master, "wt")
  fout2 = open(SKELETON_FILE_PATH + 'tmpJunk/' + 'skeleton_master_' + num_desc + '.py', "wt")

  for line in fin:
    line = line.replace("GENFILE_OUTFOLDERSTUB", '_' + num_desc)
    line = line.replace('GENFILE_PARAMSUFFIX', num_desc)
    line = line.replace('GENFILE_OUTLOOPSUFFIX', num_desc)
    line = line.replace('GENFILE_DESC', desc_tmp)
    fout.write(line )
    fout2.write(line )
  fout.close()
  fout2.close()
  fin.close() 



  
  fin = open(SKELETON_FILE_PATH + SKELETON_FILE_NAME_PARAM, "rt")
  fout = open(file_name_tmp_param, "wt")

  for line in fin:
    for i_word in range(len(PARAM_VAR_SET[i_output][1])):
      line = line.replace(PARAM_VAR_SET[i_output][1][i_word][0], PARAM_VAR_SET[i_output][1][i_word][1])
    fout.write(line )
  fout.close()
  fin.close() 


  
  
  fin = open(SKELETON_FILE_PATH + SKELETON_FILE_NAME_OUTER, "rt")
  fout = open(file_name_tmp_outer, "wt")

  for line in fin:
    for i_word in range(len(PARAM_VAR_SET[i_output][2])):
      line = line.replace(PARAM_VAR_SET[i_output][2][i_word][0], PARAM_VAR_SET[i_output][2][i_word][1])
    fout.write(line )
  fout.close()
  fin.close()   
  
  
  
 
print 'done'
