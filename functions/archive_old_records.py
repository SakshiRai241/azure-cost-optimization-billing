# functions/archive_old_records.py

from datetime import datetime, timedelta

def archive_old_billing_records():
    """
    Archives records older than 90 days from Cosmos DB to Blob Storage.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    # 1. Query old records from Cosmos DB
    old_records = cosmos_query("SELECT * FROM Billing WHERE recordDate < @cutoff", cutoff_date)

    # 2. For each record, move it to Blob Storage and delete from Cosmos
    for record in old_records:
        blob_path = f"billing-archive/{record['id']}.json"
        upload_to_blob(blob_path, record)
        delete_from_cosmos(record['id'])

    print(f"{len(old_records)} records archived to Blob Storage.")
