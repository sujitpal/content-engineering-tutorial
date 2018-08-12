curl -X POST -H "Content-Type: application/json" http://localhost:8983/solr/nips1index/schema -d '{
    "add-field-type": {
        "name": "text",
        "class": "solr.TextField",
        "analyzer": {
          "tokenizer": { "class": "solr.StandardTokenizerFactory" },
          "filters": [
              { "class": "solr.ASCIIFoldingFilterFactory" },
              { "class": "solr.EnglishPossessiveFilterFactory" },
              { "class": "solr.LowerCaseFilterFactory" },
              { "class": "solr.StopFilterFactory" },
              { "class": "solr.PorterStemFilterFactory" }
          ]
        }
    },
    "add-field": {
        "name": "year",
        "type": "string",
        "stored": true,
        "indexed" : true,
        "multiValued": false
    },
    "add-field": {
        "name": "title",
        "type": "text",
        "stored": true,
        "indexed": true,
        "multiValued": false
    },
    "add-field": {
        "name": "abstract",
        "type": "text",
        "stored": true,
        "indexed": true,
        "multiValued": false
    },
    "add-field": {
        "name": "text",
        "type" : "text",
        "stored": true,
        "indexed": true,
        "multiValued": false
    },
    "add-field": {
        "name": "authors",
        "type": "string",
        "stored": true,
        "indexed": true,
        "multiValued": true
    },
    "add-field": {
        "name": "keywords",
        "type": "string",
        "stored": true,
        "indexed": true,
        "multiValued": true
    }
}'
