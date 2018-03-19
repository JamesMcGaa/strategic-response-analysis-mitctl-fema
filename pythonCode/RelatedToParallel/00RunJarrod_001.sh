# This is a sample PBS script. It will request 1 processor on 1 node
# for 4 hours.
#   
#   Request 1 processors on 1 node 
#   
#PBS -l nodes=1:ppn=4
#
#   Request 4 hours of walltime
#
#PBS -l walltime=5:00:00
#
#   Request 1 gigabyte of memory per process
#
#PBS -l pmem=8gb
#
#   Request that regular output and terminal output go to the same file
#
#PBS -j oe
#PBS -o /gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/outputData/output100_cntryResp10e3_truck10/outputLogFiles/output01_o.out
#PBS -e /gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/outputData/output100_cntryResp10e3_truck10/outputLogFiles/output01_e.out
#
#   The following is the body of the script. By default,
#   PBS scripts execute in your home directory, not the
#   directory from which they were submitted. The following
#   line places you in the directory from which the job
#   was submitted.
#
#
#   Now we want to run the program "hello".  "hello" is in
#   the directory that this script is being submitted from,
#   $PBS_O_WORKDIR.
#
#
#
#PBS -m abe
#PBS -M jaa26@psu.edu

#>&! /gpfs/work/j/jaa26/amazon/paper1/2013-11-13/code/outputLogFiles/FulfillFastBig_Master_20111121_TweakedFor2013_OneAsin.out &
echo "  "
echo " "
echo "Job started on `hostname` at `date`"
module load python/2.7.3
module load gurobi
python /gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/pythonCode/DisasterStochLP_v02_a01_MasterFile_2014_07_22_001.py > /gpfs/work/j/jaa26/humanJarrod/pythonCode/version01/outputData/output100_cntryResp10e3_truck10/outputLogFiles/outputLog.txt
echo " "
echo "Job Ended at `date`"
echo " "
