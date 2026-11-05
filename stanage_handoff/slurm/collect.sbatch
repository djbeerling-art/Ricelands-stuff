#!/bin/bash
# Run paddy/global/collect_chains.py as a batch job (not on a login node). Archived archetypes
# ($SCEPTER_OUT/paddy_tar/<arch>.tar.gz, arch_pack.sbatch TARSYNC=1) are unpacked one at a time to node-local $TMPDIR.
# Submit from the repo root with collect_chains.py's own arguments, e.g.
#   sbatch stanage_handoff/slurm/collect.sbatch $SCEPTER_OUT/paddy arch.csv cell_map.csv cells.csv outdir --doses=20 --years=25
#SBATCH --job-name=ricecol
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --output=logs/ricecol_%j.out
source stanage_handoff/slurm/modules.sh
export TMPDIR=${TMPDIR:-/tmp}
python3 paddy/global/collect_chains.py "$@"
