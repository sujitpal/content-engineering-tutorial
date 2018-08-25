import ahocorasick
import gensim
import json
import pickle
import numpy as np
import os
import requests
import urllib

class SearchClient(object):


    def __init__(self, solr_url, num_recs_per_page):
        self.solr_url = solr_url
        self.num_records_per_page = num_recs_per_page
        if os.path.exists("../data/stopwords.txt"):
            self.stopwords = set()
            with open("../data/stopwords.txt", 'r') as fstop:
                for line in fstop:
                    self.stopwords.add(line.strip())
        if (os.path.exists("../data/raw_keywords.txt") and 
                os.path.exists("../data/keyword_neardup_mappings.tsv") and 
                os.path.exists("../data/keyword_dedupe_mappings.tsv")):
            self.automaton = self.build_automaton()
        if os.path.exists("../data/topic_sims.npy"):
            self.topic_sims = np.load("../data/topic_sims.npy")
            self.topic_doc2corpus = pickle.load(open("../data/topic_docid2corpus.pkl", "rb"))
            self.topic_corpus2doc = {v:k for k, v in self.topic_doc2corpus.items()}
        if os.path.exists("../data/w2v_sims.npy"):
            self.w2v_sims = np.load("../data/w2v_sims.npy")
            self.w2v_doc2corpus = pickle.load(open("../data/w2v_docid2corpus.pkl", "rb"))
            self.w2v_corpus2doc = {v:k for k, v in self.w2v_doc2corpus.items()}
        if os.path.exists("../models/doc2vec_model.gensim"):
            self.d2v_model = gensim.models.doc2vec.Doc2Vec.load("../models/doc2vec_model.gensim")


    def build_automaton(self):
        keywords = set()
        # load from curated list
        with open("../data/raw_keywords.txt", "r") as fcurated:
            for line in fcurated:
                keywords.add(line.strip().lower())
        # load from near dup mappings
        with open("../data/keyword_neardup_mappings.tsv", "r") as fneardup:
            for line in fneardup:
                kleft, kright = line.strip().lower().split("\t")
                keywords.add(kleft)
                keywords.add(kright)
        # load from dedupe mappings
        with open("../data/keyword_dedupe_mappings.tsv", "r") as fdedupe:
            for line in fdedupe:
                kleft, kright, _ = line.strip().lower().split("\t")
                keywords.add(kleft)
                keywords.add(kright)
        keywords_list = list(keywords)
        automaton = ahocorasick.Automaton()
        for idx, keyword in enumerate(keywords_list):
            automaton.add_word(keyword, (idx, keyword))
        automaton.make_automaton()
        return automaton


    def parse_0(self, query):
        query_str = """ title:"{:s}"^5 abstract:"{:s}"^2 text:"{:s}" """.format(query, query, query).strip()
        return query_str
    

    def parse_1(self, query):
        terms = query.split(" ")
        query_parts = []
        for term in terms:
            query_parts.append(""" title:"{:s}"^5 abstract:"{:s}"^2 text:"{:s}" """.format(term, term, term).strip())
        return " ".join(query_parts)


    def parse_2(self, query):
        terms = query.split(" ")
        query_parts = []
        for term in terms:
            if term in self.stopwords:
                continue
            query_parts.append(""" title:"{:s}"^5 abstract:"{:s}"^2 text:"{:s}" """.format(term, term, term).strip())
        return " ".join(query_parts)


    def search_index0(self, query, page, search_cmd, search_type):
        query_str = None
        if search_type == 0:
            query_str = self.parse_0(query)
        elif search_type == 1:
            query_str = self.parse_1(query)
        elif search_type == 2:
            query_str = self.parse_2(query)
        field_list = "*,score"
        start = (int(page) - 1) * self.num_records_per_page
        if start < 0:
            start = 0
        payload = {
            "q": query_str, 
            "fl": field_list, 
            "cmd": search_cmd,
            "start": start, 
            "rows": self.num_records_per_page
        }
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = self.solr_url + "/select?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        docs = resp_json["response"]["docs"]
        start_offset = resp_json["response"]["start"] + 1
        end_offset = start + len(docs)
        meta = {
            "q": query,
            "qs": query_str,
            "page": int(page),
            "numFound": resp_json["response"]["numFound"],
            "start": start_offset,
            "end": end_offset
        } 
        return meta, docs


    def compose_facet_data(self, resp_json, facet_key):
        facet_counts_parent = resp_json["facet_counts"]["facet_fields"]
        facet_data = []
        if facet_key in facet_counts_parent.keys():
            counts_seq = facet_counts_parent[facet_key]
            pos = 0
            while True:
                key = counts_seq[pos]
                count = counts_seq[pos+1]
                facet_data.append((key, count))
                pos += 2
                if pos >= len(counts_seq):
                    break
        return facet_data


    def parse_3(self, query):
        clauses = []
        phrases = [item[1][1] for item in self.automaton.iter(query)]
        query_fields = ["title", "abstract", "text"]
        query_field_boosts = [10, 5, 1]
        for query_field, boost in zip(query_fields, query_field_boosts):
            query_field_clauses = []
            # entire input query, highest boost
            query_field_clauses.append("{:s}:\"{:s}\"^5".format(query_field, query))
            # each phrase is boosted to an intermediate boost
            for phrase in phrases:
                query_field_clauses.append("{:s}:\"{:s}\"^2".format(query_field, phrase))
#            # each word of query (optional)
#            for word in query.split(" "):
#                query_field_clauses.append("{:s}:{:s}".format(query_field, word))
            # join the field and boost it
            clauses.append("({:s})^{:d}".format(" ".join(query_field_clauses), boost))
        return " ".join(clauses)

        
    def search_index1(self, query, keyword_facet, author_facet, org_facet, page, search_cmd, search_type):
        query_str = None
        query_str = None
        if search_type == 0:
            query_str = self.parse_0(query)
        elif search_type == 1:
            query_str = self.parse_1(query)
        elif search_type == 2:
            query_str = self.parse_2(query)
        elif search_type == 3:
            query_str = self.parse_3(query)
        field_list = "*,score"
        start = (int(page) - 1) * self.num_records_per_page
        if start < 0:
            start = 0
        url_params = [
            ("q", query_str),
            ("fl", field_list),
            ("start", start),
            ("rows", self.num_records_per_page),
            ("facet", "on"),
            ("facet.field", "keywords"),
            ("facet.field", "authors"),
            ("facet.field", "orgs")
        ]
        if keyword_facet:
            url_params.append(("fq", "keywords:\"" + keyword_facet + "\""))
        if author_facet:
            url_params.append(("fq", "authors:\"" + author_facet + "\""))
        if org_facet:
            url_params.append(("fq", "orgs:\"" + org_facet + "\""))
        params = urllib.parse.urlencode(url_params, 
                                        quote_via=urllib.parse.quote_plus)
        search_url = self.solr_url + "/select?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        docs = resp_json["response"]["docs"]
        start_offset = resp_json["response"]["start"] + 1
        end_offset = start + len(docs)
        meta = {
            "q": query,
            "qs": query_str,
            "cmd": search_cmd,
            "page": int(page),
            "numFound": resp_json["response"]["numFound"],
            "start": start_offset,
            "end": end_offset,
            "keyword_fq": keyword_facet,
            "author_fq": author_facet,
            "org_fq": org_facet
        }
        facets = {}
        facets["keywords"] = self.compose_facet_data(resp_json, "keywords")
        facets["authors"] = self.compose_facet_data(resp_json, "authors")
        facets["orgs"] = self.compose_facet_data(resp_json, "orgs")
        return meta, facets, docs


    def get(self, id):
        query_str = "id:{:s}".format(id)
        field_list = "*"
        payload = {"q": query_str, "fl": field_list, "start": 0, "rows": 1}
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = self.solr_url + "/select?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        doc = resp_json["response"]["docs"][0]
        return doc


    def get_mlt_docs(self, id, fields):
        query_str = "id:{:s}".format(id)
        field_list = "id,title"
        mlt_fields = ",".join(fields)
        payload = {
            "q": query_str, 
            "fl": field_list,
            "mlt": "true",
            "mlt.fl": mlt_fields
        }
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = self.solr_url + "/select?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        mlt_docs = resp_json["moreLikeThis"][id]["docs"]
        return mlt_docs


    def get_similar_docs(self, id, field_name):
        main_doc = self.get(id)
        if field_name not in main_doc.keys():
            return []
        field_values = main_doc[field_name]
        query_str = "{:s}:({:s})".format(field_name, " ".join(["\"" + field_value + "\"" for field_value in field_values]))
        field_list = ",".join(["id", "title", field_name])
        payload = {
          "q": query_str,
          "fl": field_list
        } 
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = self.solr_url + "/select?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        source_set = set(field_values)
        docs = resp_json["response"]["docs"]
        # ranking is close, but not perfect because of IDF, so rerank by jaccard
        scored_docs = []
        for doc in docs:
            if doc["id"] == id:
                continue
            target_set = set(doc[field_name])
            doc["jaccard_score"] = len(source_set.intersection(target_set)) / len(source_set.union(target_set))
            scored_docs.append(doc)
        sorted_docs = sorted(scored_docs, key=lambda x: x["jaccard_score"], reverse=True)
        return sorted_docs[0:5]


    def get_vecsim_docs(self, id, vec_name):
        if vec_name == "topic":
            row = self.topic_sims[self.topic_doc2corpus[int(id)], :]
            target_ids = [self.topic_corpus2doc[x] for x in np.argsort(-row)[0:6].tolist()]
        elif vec_name == "w2v":
            row = self.w2v_sims[self.w2v_doc2corpus[int(id)], :]
            target_ids = [self.w2v_corpus2doc[x] for x in np.argsort(-row)[0:6].tolist()]
        else:
            return []
        query_str = "id:({:s})".format(" ".join(['"' + str(x) + '"' for x in target_ids]))
        field_list = ",".join(["id", "title"])
        payload = {
          "q": query_str,
          "fl": field_list
        } 
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = self.solr_url + "/select?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        docs = resp_json["response"]["docs"]
        doc2title = {}
        for doc in docs:
            doc2title[int(doc["id"])] = doc["title"]
        sorted_docs = []
        for tid in target_ids:
            if tid == int(id):
                continue
            sorted_docs.append({"id": str(tid), "title": doc2title[tid]})
        return sorted_docs[0:5]


    def get_doc2vec_docs(self, id):
        sim_docs = self.d2v_model.docvecs.most_similar(positive=[int(id)], negative=[], topn=5)
        target_ids = [tid for tid, score in sim_docs]
        query_str = "id:({:s})".format(" ".join(['"' + str(x) + '"' for x in target_ids]))
        field_list = ",".join(["id", "title"])
        payload = {
          "q": query_str,
          "fl": field_list
        } 
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus)
        search_url = self.solr_url + "/select?" + params
        resp = requests.get(search_url)
        resp_json = json.loads(resp.text)
        docs = resp_json["response"]["docs"]
        doc2title = {}
        for doc in docs:
            doc2title[int(doc["id"])] = doc["title"]
        sorted_docs = []
        for tid in target_ids:
            if tid == int(id):
                continue
            sorted_docs.append({"id": str(tid), "title": doc2title[tid]})
        return sorted_docs

