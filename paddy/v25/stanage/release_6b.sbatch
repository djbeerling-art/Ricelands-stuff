#!/bin/bash
# Start the Fig. 6b chains (w 0 and 0.4) together with the main ref chains: the running v25b pipeline submits them with
# a dependency on the main ref chains, so this poller clears that dependency as soon as they appear. They are the only
# v25ch jobs submitted with a dependency.
#SBATCH --job-name=rel6b
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --time=08:00:00
#SBATCH --mem=200M
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/%x_%j.out
n=0
while [ $n -lt 2 ]; do
  for j in $(squeue -u $USER -h -t PD -n v25ch -o '%F %r' | awk '$2=="Dependency"{print $1}' | sort -u); do
    scontrol update JobId=$j Dependency= && { echo "released $j"; n=$((n+1)); }
  done
  sleep 120
done
echo "both Fig. 6b arrays released"
