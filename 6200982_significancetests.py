#!/usr/bin/env python
import sys
import pandas as pd
import numpy as np
from scipy import misc
import re

def sample_average_diff(sample1, sample2):
    return sample1.mean() - sample2.mean()

def randomization_test(sample1, sample2):
    num_iterations = 1000
    
    diffs = []
    for iteration in range(1,num_iterations):
        randombools = np.random.uniform(size=len(sample1)) > 0.5    
        swapped1 = sample1 * randombools + sample2 * (1 - randombools)
        swapped2 = sample1 * (1 - randombools) + sample2 * randombools
        diff = sample_average_diff(swapped1, swapped2)
        diffs.append(diff)
        
    percentiles = np.percentile(diffs,[2.5,97.5])
    actual_diff = sample_average_diff(sample1, sample2)
    if(actual_diff > percentiles[1] or actual_diff < percentiles[0]):
        return True
    return False
    
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
    print "sign test p-value:", sign_test(evaluations1.mean_reciprocal_rank, evaluations2.mean_reciprocal_rank)
    print "randomization test, different?", randomization_test(evaluations1.mean_reciprocal_rank, evaluations2.mean_reciprocal_rank)

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print "usage:%s system1_evaluations.csv system2_evaluations.csv\n"
        sys.exit(1)
    main(sys.argv[1],sys.argv[2])
