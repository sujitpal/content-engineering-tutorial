## Content Engineering Tutorial :: Data

The base data for this project is available at from the [NIPS Dataset Repository on Kaggle](https://www.kaggle.com/benhamner/nips-papers) contributed by Ben Hamner. It contains the titles, authors, abstracts and extracted text for all NIPS papers from 1987 to 2017. You will need the following files.

* authors.csv
* paper\_authors.csv
* papers.csv

We also need the following dictionary files for extracting ORGs from our text

* [World universities list](https://github.com/endSly/world-universities-csv)
* [Top 2000 companies according to Forbes](https://www.someka.net/excel-template/forbes-global-2000-list-2017/)


All other files can be derived (sometimes at significant expense of processing time) from these 3 files.

In addition, since the aim of this project is to create data that makes the search experience better, you also need a search engine. This tutorial requires a Solr server to be installed and available.

