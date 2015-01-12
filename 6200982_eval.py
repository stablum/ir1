#!/usr/bin/env python
import sys
import pandas as pd

def evaluation_measures(qrels, results, k):

    #results = results[results["rank"]<=k]
    merged = qrels.merge(results, how="inner", on=["q","doc"])
    useful = merged[["q","doc","k","relevant"]].sort(columns=["q","k"]).set_index('q')
    useful['auto_increment'] = True
    num_relevant = useful.groupby(level=0).sum()
    qs = sorted(list(set(useful.index)))
    num_relevant = useful.groupby(level=0).sum()[["relevant","auto_increment"]]
    num_relevant.columns=["total_relevant","total"]

    # em: evaluation measures
    em = useful[['relevant','auto_increment']].groupby(level=0).cumsum()
    em.columns = ['relevant_at_k','k']
    em = em.join(num_relevant)
    em['precision_at_k'] = em.relevant_at_k.astype('double') / em.k
    em['recall'] = em.relevant_at_k.astype('double') / em.total_relevant
    
    ret = em.groupby(level=0).mean()[['precision_at_k']].rename(columns={'precision_at_k':'average_precision'})
    ret = ret.join(em[em.k == k][['precision_at_k']].rename(columns={'precision_at_k':'precision_at_'+str(k)}))
    
    
    return ret

def main(qrels_filename, results_filename):
    qrels = pd.read_csv(qrels_filename,delim_whitespace=True,header=None)
    qrels['relevant'] = (qrels.iloc[:,3] > 0)
    qrels.columns = ['q','something','doc','relevance', 'relevant']

    results = pd.read_csv(results_filename,delim_whitespace=True,header=None)
    results.columns = ['q','not_used','doc','k','other','algo']

    k = 10
    print evaluation_measures(qrels, results, k)
    
if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print "usage:%s qrels_filename results_filename\n"
    main(sys.argv[1],sys.argv[2])
