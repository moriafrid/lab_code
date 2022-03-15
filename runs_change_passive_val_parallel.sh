#!/bin/bash

#pass 1 argument = size of ipcluster
#pass 2 argument = RM
#pass 3 argument = RA
#pass 4 argument = CM
#pass 5 argumant = resize_dend_by
#pass 6 argument = shrinkage_by
#pass 7 argument = passive_vel_name


# Write output as following (%j is JOB_ID)
#SBATCH -o outputs/output-%j.out
#SBATCH -e errors/error-%j.err
#SBATCH --mem 60000
#SBATCH -t 2-0
#SBATCH -c 30


set -x

PWD=$(pwd)
LOGS=$PWD/logs
mkdir -p $LOGS
#
#export PATH="/ems/elsc-labs/segev-i/moria.fridman/anaconda3/bin:$PATH"  ## <<-- Change this to the path that you use
#export PYTHONDIR="/ems/elsc-labs/segev-i/moria.fridman/anaconda3/envs/project/bin/python"

export profile=moria$5$3  #Note the profile name, you will need to use it in the python script
ipython profile create --parallel --profile=${profile}

# ipcluster stop --profile=${profile} &
sleep 50
ipcluster start --profile=${profile} --n=$1 &
sleep 60

echo "Launching job"
conda init
conda activate project
echo $PATH
python MOO_get_parameters.py $1 $2 $3 $4 $5 $6 $7 ${profile}
#conda deactivate
