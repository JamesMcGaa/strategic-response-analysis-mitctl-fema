#!/bin/bash

# dos2unix GenerateShellAndPythonScriptsFromSkeleton.sh
# bash GenerateShellAndPythonScriptsFromSkeleton.sh


# Put all the numbers in an array
#LISTNUM=( 12 25 50 100 200 400 800 1600 99999)
# JUNK WALLNUM=( '07:00:00' '12:00:00' '20:00:00' '20:00:00' '24:00:00' '24:00:00' '24:00:00')
#LISTNUM=( 200 500 923 )
LISTOUTPUTSUFFIX=(           'cntryResp10e3_truck10' 'cntryResp10e5_truck10' 'cntryResp10e3_truck20' 'cntryResp10e5_truck20')
LISTPARAMSUFFIX=(            'cntryResp10e3_truck10'              'cntryResp10e5_truck10'                 'cntryResp10e3_truck20'               'cntryResp10e5_truck20'           )
LISTOUTERLOOPSUFFIX=(        'ActualInv'                          'ActualInv'                             'ActualInv'                           'ActualInv'                       )
LISTRUNDESCRIPT=(            'cntryResp10e3_truck10_ActualInv'    'cntryResp10e5_truck10_ActualInv'       'cntryResp10e3_truck20_ActualInv'     'cntryResp10e5_truck20_ActualInv' )

LISTMYWALLTIME=(             '5:00:00'                            '5:00:00'                               '5:00:00'                              '5:00:00'                        )
LISTMYPPN=(                  '4'                                  '4'                                     '4'                                    '4'                              )
LISTMYPMEM=(                 '8gb'                                '8gb'                                   '8gb'                                  '8gb'                            )

LISTFOLDERNUMS=(             1                                    2                                        3                                     4                                )


BASEDIRECTORY=/gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/outputData
BASEBASEDIRECTORY='A_outputData_01'
if [ ! -d "$BASEDIRECTORY/$BASEBASEDIRECTORY" ]
then
  mkdir $BASEDIRECTORY/$BASEBASEDIRECTORY	
fi	


# Iterate over the array
for i in $(seq 0 $((${#LISTOUTPUTSUFFIX[*]}-1)))
do
	# Pad "i" with five zeroes: this is to name the master file
	# 001, 002, 005, 010, 020, 040, 400
	PADDED=`printf "%05d\n" ${LISTFOLDERNUMS[$i]}`

	# Specify the name of the directory
  OUTPUTSUB=$BASEBASEDIRECTORY/output_$PADDED'_'${LISTOUTPUTSUFFIX[$i]}
	DIRECTORY=$BASEDIRECTORY/$OUTPUTSUB

	# Create output directories, if they do not exist		
	# If the directory exists, we will just continue to fill it.
    
    
	if [ ! -d "$DIRECTORY" ]
	then
		mkdir $DIRECTORY	
        mkdir $DIRECTORY/outputLogFiles
	fi	
	
  
	# Copy all the data from a folder /the/origin/folder/ to each created directory
	cp /gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/pythonCode/DisasterStochLP_v02_f_Parameters_2014_07_22__${LISTPARAMSUFFIX[$i]}.py $DIRECTORY/
  cp /gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/pythonCode/DisasterStochLP_v02_k_OutLoopIterate_2014_07_22__${LISTOUTERLOOPSUFFIX[$i]}.py $DIRECTORY/

	# this python skeleton contains a simple skeleton without any values for the specified parameters
  dos2unix DisasterStochLP_v02_a01_MasterFile_2014_07_22_Skeleton_001.py
	#cat DisasterStochLP_v02_a01_MasterFile_2014_07_22_Skeleton_001.py | sed "s/MYOUTPUTFOLDER/$OUTPUTSUB/g" > $DIRECTORY/DisasterMaster_$PADDED.sa
  sed "s!MYOUTPUTFOLDER!$OUTPUTSUB!g" DisasterStochLP_v02_a01_MasterFile_2014_07_22_Skeleton_001.py > $DIRECTORY/DisasterMaster_$PADDED.py
  sed -i "s/MYPARAMFILENAMESUFFIX/${LISTPARAMSUFFIX[$i]}/g" $DIRECTORY/DisasterMaster_$PADDED.py
  sed -i "s/MYOUTERLOOPFILENAMESUFFIX/${LISTOUTERLOOPSUFFIX[$i]}/g" $DIRECTORY/DisasterMaster_$PADDED.py
  sed -i "s/MYRUNDESCRIPTION/${LISTRUNDESCRIPT[$i]}/g" $DIRECTORY/DisasterMaster_$PADDED.py


	# the pbs script skeleton contains a simple skeleton without the file name 
	# cat RunAmpleJasonPBS_SkeletonCluster2.sh | sed // > pbs_script_$i
  cat RunJarrod_Skeleton_001.sh | sed "s/MYWALLTIME/${LISTMYWALLTIME[$i]}/g" > $DIRECTORY/pbs_script_$PADDED.sh
  sed -i "s/MYPPN/${LISTMYPPN[$i]}/g" $DIRECTORY/pbs_script_$PADDED.sh
  sed -i "s/MYPMEM/${LISTMYPMEM[$i]}/g" $DIRECTORY/pbs_script_$PADDED.sh
  sed -i "s/MYMASTERFILENAME/DisasterMaster_$PADDED/g" $DIRECTORY/pbs_script_$PADDED.sh
  sed -i "s!MYOUTPUTFOLDER!$OUTPUTSUB!g" $DIRECTORY/pbs_script_$PADDED.sh

  
  dos2unix $DIRECTORY/pbs_script_$PADDED.sh



	# submit the job
    echo "qsub $DIRECTORY/pbs_script_$PADDED.sh" >> $BASEDIRECTORY/pbs_scripts_to_run.txt
	# qsub pbs_script_cluster_$PADDED.sh
done	
