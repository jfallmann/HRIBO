import os
import re
import pandas as pd
import itertools as iter
from snakemake.utils import validate, min_version
min_version("5.3.0")

ADAPTERS=config["adapter"]
INDEXPATH=config["genomeindexpath"]
CODONS=config["alternativestartcodons"]

onstart:
   if not os.path.exists("logs"):
     os.makedirs("logs")

samples = pd.read_table(config["samples"], dtype=str).set_index(["method", "condition", "replicate"], drop=False)
samples.index = samples.index.set_levels([i.astype(str) for i in samples.index.levels])
validate(samples, schema="schemas/samples.schema.yaml")
report: "report/workflow.rst"
def getContrast(wildcards):
  conditions=samples["condition"].unique()
  print(conditions)
  contrastsTupleList=list((iter.combinations(conditions,2)))
  contrasts=[[('-'.join(str(i) for i in x))] for x in contrastsTupleList]
  flat_contrasts= [item for sublist in contrasts for item in sublist]
  elements = [("contrasts/"+((element.replace("[", '')).replace("]", '')).replace("'", '')) for element in flat_contrasts]
  return elements

def getContrastXtail(wildcards):
  conditions=samples["condition"].unique()
  contrastsTupleList=list((iter.combinations(conditions,2)))
  contrasts=[[('-'.join(str(i) for i in x))] for x in contrastsTupleList]
  flat_contrasts= [item for sublist in contrasts for item in sublist]
  elements = [("xtail/" + ((element.replace("[", '')).replace("]", '')).replace("'", '') + ".csv") for element in flat_contrasts]
  return elements

rule all:
   input:
       expand("maplink/RIBO/{sample.condition}-{sample.replicate}.qualdone", sample=samples.itertuples()),
       expand("ribotish/{sample.condition}-newORFs.tsv_all.txt", sample=samples.itertuples()),
       expand("tracks/{sample.condition}.ribotish.gff", sample=samples.itertuples()),
       expand("tracks/{sample.method}-{sample.condition}-{sample.replicate}.bw", sample=samples.itertuples()),
       expand("reparation/{sample.condition}-{sample.replicate}/Predicted_ORFs.txt", sample=samples.itertuples()),
       expand("tracks/{sample.condition}-{sample.replicate}.reparation.gff", sample=samples.itertuples()),
       #expand("xtailclassic/{sample.method}-{sample.condition}-{sample.replicate}.csv", sample=samples.itertuples()),
       unpack(getContrast),
       unpack(getContrastXtail),
       "qc/multi/multiqc_report.html"

onsuccess:
    print("Done, no error")

#Preprocessing
include: "rules/preprocessing.smk"
#Adaper removal and quality control
include: "rules/trimming.smk"
#removal of reads mapping to ribosomal rna genes
include: "rules/rrnafiltering.smk"
#mapping
include: "rules/mapping.smk"
#Visualization
include: "rules/visualization.smk"
#ribotish
include: "rules/ribotish.smk"
#xtail
include: "rules/xtail.smk"
#reparation
include: "rules/reparation.smk"
#xtail
#include: "rules/xtailclassic.smk"
#multiqc
include: "rules/qc.smk"
