echo "Indexing jobs from job_execution_log data"
es_host="http://localhost:9200"
updateScriptID=JobUpdater.painless


echo "Deleting old index: jobs"
curl -X DELETE "$es_host/jobs"
echo ""
echo "Creating new index: jobs"
curl -XPUT    "$es_host/jobs" -d '
{
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "job": {
            "properties": {
                "status": {
                    "type": "keyword"
                },
                "last_start_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm"
                },
                "last_end_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm"
                },
                "job_code": {
                    "type": "keyword"
                },
                "sessions": {
                    "properties": {
                        "session_id": {
                            "type": "keyword"
                        },
                        "start_date": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm"
                        },
                        "end_date": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm"
                        }
                    }
                },
                "last_session_id": {
                    "type": "keyword"
                }
            }
        }
    }
}
'
echo ""
echo "Indexing jobs from job_execution_log data"
python ../ESEntityCentricIndexing.py events eventQuery.json job_code jobs job $updateScriptID -scriptMode incremental
