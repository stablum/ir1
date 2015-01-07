#!/usr/bin/env python
import sys
import pandas as pd

def precisions(qrels, results, k):
    ret = []
    results = results[results["rank"]<=k]
    merged = qrels.merge(results, how="inner", on=["query","doc"])
    useful = merged[["query","doc","rank","relevant"]].sort(columns=["query","rank"])
    queries = sorted(list(set(useful["query"])))
    for curr_query in queries:
        print "query", curr_query
        curr_query_data = useful[useful["query"] == curr_query]
        ranks = set(curr_query_data["rank"])
        max_rank = max(ranks)
        
        total = 0
        relevant_count = 0
        for curr_rank in range(max_rank+1) :
            if curr_rank in ranks:
                row = curr_query_data[useful["rank"] == curr_rank]
                if row.iloc[0]["relevant"]:
                    relevant_count = relevant_count + 1
            total = total + 1
            precision = float(relevant_count)/float(total)
            print row.iloc[0]["query"],row.iloc[0]["rank"],precision
            row["precision"] = precision
    
    return ret
    
def main(qrels_filename, results_filename):
    qrels = pd.read_csv(qrels_filename,delim_whitespace=True,header=None)
    qrels['relevant'] = (qrels.iloc[:,3] > 0)
    qrels.columns = ['query','something','doc','relevance', 'relevant']

    results = pd.read_csv(results_filename,delim_whitespace=True,header=None)
    results.columns = ['query','not_used','doc','rank','other','algo']

    k = 10
    print "precisions", precisions(qrels, results,k)
    
if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print "usage:%s qrels_filename results_filename\n"
    main(sys.argv[1],sys.argv[2])
