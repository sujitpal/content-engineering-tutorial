from flask import Flask, flash, render_template, request, redirect
from forms import SearchForm
from services import SearchClient

import logging
import sys

app = Flask(__name__)
app.config.from_pyfile("app.cfg")

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/content0", methods=["GET"])
def content0():
    id = request.args.get("id")
    client = SearchClient(app.config["SOLR_INDEX_0"], app.config["NUM_RECS_PER_PAGE"])
    doc = client.get(id)
    return render_template("content0.html", doc=doc)


@app.route("/content1", methods=["GET"])
def content1():
    id = request.args.get("id")
    client = SearchClient(app.config["SOLR_INDEX_2"], app.config["NUM_RECS_PER_PAGE"])
    doc = client.get(id)
    meta = {}
    meta["mlt_text"] = client.get_mlt_docs(id, ["title", "abstract", "text"])
    meta["sim_keywords"] = client.get_similar_docs(id, "keywords")
    meta["sim_authors"] = client.get_similar_docs(id, "authors")
    meta["sim_orgs"] = client.get_similar_docs(id, "orgs")
    meta["mlt_kao"] = client.get_mlt_docs(id, ["kaoterms"])
    meta["vec_topic"] = client.get_vecsim_docs(id, "topic")
    return render_template("content1.html", meta=meta, doc=doc)


@app.route("/search0", methods=["GET", "POST"])
def search0():
    meta, docs = None, None
    q = request.args.get("q")
    page = request.args.get("page")
    page = page if page else 1
    if q:
        client = SearchClient(app.config["SOLR_INDEX_0"], app.config["NUM_RECS_PER_PAGE"])
        meta, docs = client.search_index0(q, page, "search0", 0)
    return render_template("search0.html", meta=meta, docs=docs)


@app.route("/search1", methods=["GET", "POST"])
def search1():
    meta, docs = None, None
    q = request.args.get("q")
    page = request.args.get("page")
    page = page if page else 1
    if q:
        client = SearchClient(app.config["SOLR_INDEX_0"], app.config["NUM_RECS_PER_PAGE"])
        meta, docs = client.search_index0(q, page, "search1", 1)
    return render_template("search0.html", meta=meta, docs=docs)


@app.route("/search2", methods=["GET", "POST"])
def search2():
    meta, docs = None, None
    q = request.args.get("q")
    page = request.args.get("page")
    page = page if page else 1
    if q:
        client = SearchClient(app.config["SOLR_INDEX_0"], app.config["NUM_RECS_PER_PAGE"])
        meta, docs = client.search_index0(q, page, "search2", 2)
    return render_template("search0.html", meta=meta, docs=docs)


@app.route("/search3", methods=["GET", "POST"])
def search3():
    meta, facets, docs = None, None, None
    q = request.args.get("q")
    fk = request.args.get("fk")
    fa = request.args.get("fa")
    page = request.args.get("page")
    page = page if page else 1
    if q:
        client = SearchClient(app.config["SOLR_INDEX_1"], app.config["NUM_RECS_PER_PAGE"])
        meta, facets, docs = client.search_index1(q, fk, fa, page, "search3", 1)
    return render_template("search1.html", meta=meta, facets=facets, docs=docs)


@app.route("/search4", methods=["GET", "POST"])
def search4():
    meta, facets, docs = None, None, None
    q = request.args.get("q")
    fk = request.args.get("fk")
    fa = request.args.get("fa")
    fo = request.args.get("fo")
    page = request.args.get("page")
    page = page if page else 1
    if q:
        client = SearchClient(app.config["SOLR_INDEX_2"], app.config["NUM_RECS_PER_PAGE"])
        meta, facets, docs = client.search_index1(q, fk, fa, fo, page, "search4", 3)
    return render_template("search1.html", meta=meta, facets=facets, docs=docs)


if __name__ == "__main__":
    app.run(debug=True)
