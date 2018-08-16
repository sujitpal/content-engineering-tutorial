#!/bin/bash
curl -X POST -H 'Content-type:application/json' http://localhost:8983/solr/nips2index/config -d '{
  "add-searchcomponent": {
    "name": "mlt",
    "class": "MoreLikeThisComponent",
    "queryFieldType": "string"
  }
}'
