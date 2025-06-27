# functions/retrieve_record.py

def get_billing_record(record_id):
    """
    Retrieves a billing record by ID.
    First tries Cosmos DB; if not found, falls back to Blob Storage.
    """
    # Try to get the record from Cosmos DB
    record = cosmos_get(record_id)
    if record:
        return record
    
    # If not found, try fetching from Blob Storage
    blob_path = f"billing-archive/{record_id}.json"
    archived_record = download_from_blob(blob_path)

    if archived_record:
        return archived_record
    else:
        return {"error": "Record not found in hot or cold storage."}
