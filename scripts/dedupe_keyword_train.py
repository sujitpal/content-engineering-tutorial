# -*- coding: utf-8 -*-
import csv
import os
import dedupe

DATA_DIR = "../data"
MODEL_DIR = "../models"

RAW_INPUT = os.path.join(DATA_DIR, "curated_keywords_hash.csv")
SETTINGS_FILE = os.path.join(MODEL_DIR, "dedupe_keywords_learned_settings")
TRAINING_FILE = os.path.join(MODEL_DIR, "dedupe_keywords_training.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "keyword_dedupe_mappings.tsv")

# read training file (written using 09-keyword-dedupe) and transform
# into format suitable for use by dedupe
data = {}
with open(RAW_INPUT, "rb") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_id = int(row["id"])
        data[row_id] = dict(row.items())
        
# training
if os.path.exists(SETTINGS_FILE):
    print("reading from settings file {:s}".format(SETTINGS_FILE))
    with open(SETTINGS_FILE, "rb") as f:
        deduper = dedupe.StaticDedupe(f)
else:
    # define fields for deduper to pay attention to, here we
    # will ask for all fields except id
    field_names = ["col_{:d}".format(i+1) for i in range(25)]
    fields = [{"field": field_name, "type": "Exact"} 
              for field_name in field_names]
    fields.append({"field": "keyword", "type": "String"})
    deduper = dedupe.Dedupe(fields)
    # feed the deduper a sample of records for training
    deduper.sample(data, 15000)
    # use training data for previous run if available
    if os.path.exists(TRAINING_FILE):
        print("reading labeled examples from training file: {:s}"
              .format(TRAINING_FILE))
        with open(TRAINING_FILE, "rb") as f:
            deduper.readTraining(f)

    # active learning
    print("starting active labeling...")
    dedupe.consoleLabel(deduper)

    deduper.train()            
    
    # save training data to disk
    with open(TRAINING_FILE, "w") as f:
        deduper.writeTraining(f)
    with open(SETTINGS_FILE, "w") as f:
        deduper.writeSettings(f)
        
# blocking
print("blocking...")
threshold = deduper.threshold(data, recall_weight=1.5)

# clustering
print("clustering...")
clustered_dupes = deduper.match(data, threshold)

# write results
with open(OUTPUT_FILE, "w") as f:
    for cluster_id, cluster in enumerate(clustered_dupes):
        id_set, scores = cluster
        keywords = sorted([data[id]["keyword"] for id in id_set],
                          key=lambda x: len(x), reverse=True)
        f.write("{:s}\t{:s}\t{:.3f}\n".format(
            keywords[0], keywords[1], scores[0]))
