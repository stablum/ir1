#!/usr/bin/env python
import sys
import pandas as pd
import numpy as np
from scipy import misc
import re

def binomial_distribution(k, n, p):
    return misc.comb(n,k) * np.power(p, k) * np.power( (1 - p), n - k )

def sign_test(sample1, sample2):
    num_successes = (sample2 - sample1 > 0).sum()
    num_trials = len(sample1)
    p_value = binomial_distribution(num_successes, num_trials, 0.5)
    return p_value

def main(filename1, filename2):
    evaluations1 = pd.read_csv(filename1)
    evaluations2 = pd.read_csv(filename2)
    print sign_test(evaluations1.mean_reciprocal_rank, evaluations2.mean_reciprocal_rank)

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print "usage:%s system1_evaluations.csv system2_evaluations.csv\n"
        sys.exit(1)
    main(sys.argv[1],sys.argv[2])
