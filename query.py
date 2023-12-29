import json
import sys
import logging
from collections import defaultdict
import numpy as np
import pdb

def compute_tf(freq):
    return freq**0.5

def compute_idf(doc_count, freq):
    '''
    doc_count: documents count that contain this term
    freq: frequency in current document
    '''
    return 1 + np.log(doc_count/freq+1)

def compute_norm(term_count):
    return 1/(term_count**0.5)

def compute_tfidf(term, indices):
    # if term not in indices, return score of 0
    if term not in indices:
        return {}
    recs =  indices.get(term)
    doc_count = len(recs.keys())
    term_count = sum(recs.values())
    results = {}
    for page_id in recs:
        freq = recs[page_id]
        tf = compute_tf(freq)
        idf = compute_idf(doc_count, freq)
        norm = compute_norm(term_count)
        score = tf*idf*norm
        results[page_id] = score
    return results


def get_relevant_pages(search_term, indices, count=10):
    search_term_split = search_term.split(" ")
    results = defaultdict(lambda: 0.0)
    for term in search_term_split:
        term_scores = compute_tfidf(term, indices)
        for page_id in term_scores:
            results[page_id] += term_scores[page_id]
    page_tuples = sorted(results.items(), key=lambda kv: kv[1], reverse=True)[:count]
    if len(page_tuples) == 0:
        return []
    else:
        return [i[0] for i in page_tuples]

if __name__ == "__main__":
    # load index and load pages
    with open('indices/indices_latest.json') as f:
        indices = json.load(f)
    with open('pages/pages_latest.json') as f:
        pages_indices = json.load(f)
    if len(sys.argv) < 2:
        logging.error("please input search term")
        sys.exit(1)
    
    search_term = sys.argv[1]
    pages = get_relevant_pages(search_term=search_term, indices=indices)
    def get_relevant_page_names(pages, pages_indices):
        relevant_page_title = []
        for page in pages:
            relevant_page_title.append(pages_indices.get(page))
        return relevant_page_title
    
    print(f"query: {search_term}")
    if len(pages) == 0:
        print('no relevant articles')
        sys.exit(0)
    for page_found in get_relevant_page_names(pages, pages_indices):
        print(page_found)
    sys.exit(0)