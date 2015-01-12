#!/usr/bin/env python
import sys
import pandas as pd
import numpy as np

def evaluation_measures(qrels, results, k):

    #results = results[results["rank"]<=k]
    merged = qrels.merge(results, how="inner", on=["q","doc"])
    useful = merged[["q","doc","k","relevant","relevance"]].sort(columns=["q","k"]).set_index(['q'])
    useful['auto_increment'] = True
    num_relevant = useful.groupby(level=0).sum()
    qs = sorted(list(set(useful.index)))
    num_relevant = useful.groupby(level=0).sum()[["relevant","auto_increment"]]\
        .rename(columns={'relevant':"total_relevant",'auto_increment':"total"})

    # em: evaluation measurese
    em = useful[['relevant','auto_increment']].groupby(level=0).cumsum()
    em.columns = ['relevant_at_k','k']
    em = em.join(num_relevant)
    
    em['precision_at_k'] = em.relevant_at_k.astype('double') / em.k
    em['recall'] = em.relevant_at_k.astype('double') / em.total_relevant
    em['reciprocal_k'] = 1/em.k * em.relevant_at_k.astype('int')
    
    useful = useful.reset_index().set_index(['q','k'])
    em = em.reset_index().set_index(['q','k'])
    em = em.join(useful[['relevance']]).fillna(0).rename(columns={'relevance':'gain'})
    em.gain = np.power(2,em.gain) - 1
    
    em['discount'] = np.log2(em.index.get_level_values(1)+1)
    em['discounted_gain'] = em.gain / em.discount
    em['dcg'] = em[['discounted_gain']].groupby(level=0).cumsum()
    max_dcg = em[['dcg']].groupby(level=0).max().rename(columns={'dcg':'max_dcg'})
    em = em.reset_index().set_index(['q'])
    em = em.join(max_dcg)
    em['ndcg'] = em.dcg/em.max_dcg
    
    ret = em.groupby(level=0).mean()[['precision_at_k']].rename(columns={'precision_at_k':'average_precision'})
    ret = ret.join(em[em.k == k][['precision_at_k','ndcg']].rename(columns={'precision_at_k':'precision_at_'+str(k),'ndcg':'ndcg_at_'+str(k)}))
    ret = ret.join(em[['reciprocal_k']].groupby(level=0).mean().rename(columns={'reciprocal_k':'mean_reciprocal_rank'}))

    return ret

def main(qrels_filename, results_filename):
    qrels = pd.read_csv(qrels_filename,delim_whitespace=True,header=None)
    qrels['relevant'] = (qrels.iloc[:,3] > 0)
    qrels.columns = ['q','something','doc','relevance', 'relevant']

    results = pd.read_csv(results_filename,delim_whitespace=True,header=None)
    results.columns = ['q','not_used','doc','k','other','algo']
    results.k = results.k + 1
    k = 10
    print evaluation_measures(qrels, results, k)
    
if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print "usage:%s qrels_filename results_filename\n"
    main(sys.argv[1],sys.argv[2])
