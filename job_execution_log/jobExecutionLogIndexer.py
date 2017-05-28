import csv
from elasticsearch import helpers
from elasticsearch import Elasticsearch
import sys
import zipfile
import os
import StringIO

filename = 'job_execution_logs.mini.csv.zip'
es = Elasticsearch([{'host': '192.168.56.101', 'port': 9200}])
indexName = "job_execution_logs"
actionsPerBulk=5000
es.indices.delete(index=indexName, ignore=[400, 404])
indexSettings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "job_execution_log": {
            "properties": {
                "sessionId": {
                    "type": "keyword"
                },
                "code": {
                    "type": "keyword"
                },
                "date": {
                    "type": "date",
                    "format" : "yyyy-MM-dd HH:mm"
                },
                "message": {
                    "type": "keyword"
                },
                "eventType": {
                    "type": "integer"
                }

            }
        }
    }
}
es.indices.create(index=indexName, body=indexSettings)
actions = []

fields = []

full_path = os.getcwd() + "/" + filename
with zipfile.ZipFile(full_path) as z:
    for zippedFilename in z.namelist():
        numLines = 0
        data = StringIO.StringIO(z.read(zippedFilename))
        reader = csv.reader(data)
        for row in reader:
            numLines += 1
            if numLines == 1:
                fields = row
            else:
                if len(row) < 1:
                    break
                doc = {
                	'sessionId': row[0],
                 	'code': row[1],
                 	'date':row[3],
                    'message':row[4],
                    'eventType':int(row[2])
                }
                action = {
                        "_index": indexName,
                        '_op_type': 'index',
                        "_type": "job_execution_log",
                        "_source": doc
                }
                actions.append(action)
                # Flush bulk indexing action if necessary
                if len(actions) >= actionsPerBulk:
                    try:
                        helpers.bulk(es, actions)
                    except:
                        print ("Unexpected error:", sys.exc_info()[0])
                    del actions[0:len(actions)]
                    print (numLines)

if len(actions) > 0:
    helpers.bulk(es, actions)
