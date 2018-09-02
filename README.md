## Content Engineering Tutorial

### Abstract

According to Computer World magazine, unstructured text data accounts for roughly 70%-80% of all data in an organization. The most common approach to leveraging a company's text resources is to make it searchable using a search engine. While that in itself is a huge step forward, there is much more that can be done to extract further insight from the text. In this tutorial, we will look at extracting keywords and other features from the text, using well-known statistical and off-the-shelf machine learning techniques, improving both content search and discovery in the process. Finally we bring these threads together to build an ontology and a simple recommendation system. We will use Solr 7.x as our indexing platform and the NIPS papers dataset, a collection of 7000+ papers from the Neural Information Processing Systems Conference from 1987-2017, as our corpus. Tutorial is fairly code-heavy and Python based, and while knowledge of Python is not required, familiarity with a programming language would be very desirable.

### Getting started

Please refer to the [data/README.md](data/README.md) and [models/README.md](models/README.md) to download the dataset and third party models. 

Also refer to the [requirements.txt](requirements.txt) to find if you need to install additional libraries for your Python3 installation. The code was built using [Anaconda Python3](https://www.anaconda.com/download/#macos) which has many (not all) of these libraries already installed. The only one I couldn't get to work was the dedupe library, which I had to install on a separate Anaconda Python 2 installation.

Finally, the notebooks and web application both use [Solr 7.x](http://lucene.apache.org/solr/) as the search backend, so you need to install that. To start Solr, navigate to the Solr home directory, and run the following command. The Solr console can be accessed from your browser at [http://localhost:8983](http://localhost:8983).

    cd <solr_home>
    bin/solr start

To run the notebook server, navigate to the notebooks subdirectory, and then run the following command. By default, the default URL to navigate to on your browser to access the notebooks is [http://localhost:8888/](http://localhost:8888). You can also find the URL from the server logs that are written out on the console.

    cd <project_home>/notebooks
    jupyter notebook

To run the web application, navigate to the webtool subdirectory, then run the following command. The web application will start listening on port 5000. To get to the application from your browser, navigate to [http://localhost:5000](http://localhost:5000).

    cd <project_home>/webtool
    python webtool.py
