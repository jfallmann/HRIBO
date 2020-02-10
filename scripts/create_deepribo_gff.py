#!/usr/bin/env python
'''This script takes input files generated by
deepribo and creates a new data frame containing specified
information and writes it as gff3 format files.
'''

import pandas as pd
import re
import argparse
import numpy as np
import os
import csv
import collections



def to_gff3(args):
    inputDF = pd.read_csv(args.predictedORFs, sep=',')
    nTuple = collections.namedtuple('Pandas', ["seqName","source","type","start","stop","score","strand","phase","attribute"])

    # extract information from each row and build new dataframe in gff format
    rows = []
    rows_all = []
    for row in inputDF.itertuples(index=True, name='Pandas'):
        # txt file content
        filename = getattr(row, "filename")
        filename_counts = getattr(row, "filename_counts")
        label = bool(getattr(row, "label"))
        in_gene = getattr(row, "in_gene")
        strand = str(getattr(row, "strand"))
        coverage = str(getattr(row, "coverage"))
        coverage_elo = str(getattr(row, "coverage_elo"))
        rpk = str(getattr(row, "rpk"))
        rpk_elo = str(getattr(row, "rpk_elo"))
        start_site = str(getattr(row, "start_site"))
        start_codon = getattr(row, "start_codon")
        stop_site = str(getattr(row, "stop_site"))
        stop_codon = str(getattr(row, "stop_codon"))
        locus = str(getattr(row, "locus"))
        prot_seq = str(getattr(row, "prot_seq"))
        nuc_seq = str(getattr(row, "nuc_seq"))
        pred = float(getattr(row, "pred"))
        pred_rank = str(getattr(row, "pred_rank"))
        SS = str(getattr(row, "SS"))
        dist = int(getattr(row, "dist"))
        SS_pred_rank = getattr(row, "SS_pred_rank")

        # new content
        chromosome, rest = locus.split(":")
        start, stop = rest.split("-")

        if SS_pred_rank == 999999:
            continue

        if strand == "+":
            stop = int(stop) + 2
        else:
            start = int(start) - 2

        seqName = chromosome
        source = "deepribo"
        feature = "CDS"
        score = pred
        phase = "."
        attribute = "ID=" + chromosome + ":" + str(start) + "-" + str(stop) + ":" + strand \
                   + ";pred_value="+ str(pred)+";Method=deepribo" + ";Condition=" + args.condition + ";Replicate=" + args.replicate

        rows.append(nTuple(seqName, source, feature, start, stop, score, strand, dist, attribute))



    return pd.DataFrame.from_records(rows, columns=["seqName","source","type","start","stop","score","strand","phase","attribute"])


def main():
    # store commandline args
    parser = argparse.ArgumentParser(description='Converts reperation output to new data frame\
                                     containing specified information and saves it in gff3 format.')
    parser.add_argument("-i", "--inputCSV", action="store", dest="predictedORFs", required=True
                                          , help= "the input file. (created by reparation)")
    parser.add_argument("-c", "--condition", action="store", dest="condition", required=True
                                           , help= "the condition of the current file")
    parser.add_argument("-r", "--replicate", action="store", dest="replicate", required=True
                                           , help= "the condition of the current file")
    parser.add_argument("-o", "--outputGFF", action="store", dest="outputGFF", required=True
                                           , help= "the output file name (gff3 format)")

    args = parser.parse_args()

    gff3df = to_gff3(args)
    gff3df = gff3df.sort_values(by=["score"])
    gff3df.to_csv(args.outputGFF, sep="\t", header=False, index=False, quoting=csv.QUOTE_NONE)

if __name__ == '__main__':
    main()
