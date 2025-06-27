## Cost Optimization Challenge: Managing Billing Records in Azure Serverless Architecture

## Problem Summary

- Billing records are stored in **Azure Cosmos DB**
- The system is **read-heavy**, with over **2 million records**
- Records older than **3 months are rarely accessed**
- Each record is up to **300 KB** in size
- This has led to high storage and throughput costs over time

## Goal

Design a solution that:
- Reduces Cosmos DB costs
- Keeps all data accessible (including old records)
- Maintains existing **API contracts**
- Requires **no downtime** and **no data loss**
- Is simple and easy to maintain

## Solution Overview: Hot + Cold Storage

We propose a **hybrid architecture** using:

- **Azure Cosmos DB** for hot (recent) records
- **Azure Blob Storage (Cool tier)** for cold (archived) records
- **Azure Functions** to automate archival and retrieval
- No changes to the frontend or API layer

## Architecture Diagram (ASCII)

User Request
    |
    v
----------------------
| Existing API Layer |
----------------------
        |
        v
+----------------------------+
| Azure Function / Proxy API |
| - Check record age         |
| - Route to Cosmos or Blob  |
+----------------------------+
        |             |
        v             v
+---------------+  +-------------------+
|  Cosmos DB    |  | Azure Blob Storage|
| (Hot records) |  |  (Cold records)   |
+---------------+  +-------------------+

## Core Components

| Component         | Purpose |
|------------------|---------|
| **Azure Cosmos DB** | Stores recent billing records (last 90 days) |
| **Azure Blob Storage (Cool Tier)** | Stores archived records older than 90 days |
| **Azure Functions** | Automates archival and record retrieval |
| **Optional Metadata Table** | Keeps track of archived record IDs |
| **Proxy Logic** | Decides where to fetch from (Cosmos or Blob) |

## Archival Strategy (Automated)

Archive all records older than 90 days to Azure Blob Storage.

### Archive Logic (Pseudocode)

```python
# archive_old_records.py
from datetime import datetime, timedelta

def archive_old_billing_records():
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    old_records = cosmos_query("SELECT * FROM Billing WHERE recordDate < @cutoff", cutoff_date)

    for record in old_records:
        blob_path = f"billing-archive/{record['id']}.json"
        upload_to_blob(blob_path, record)
        delete_from_cosmos(record['id'])

## Retrieval Strategy (Fallback Logic)

If the record is not found in Cosmos DB, fetch from Blob.

### Retrieval Logic (Pseudocode)

```python
# retrieve_record.py
def get_billing_record(record_id):
    record = cosmos_get(record_id)
    if record:
        return record
    else:
        return download_from_blob(f"billing-archive/{record_id}.json")

## Azure CLI Setup Commands

```bash
# Enable Blob Versioning (optional but recommended)
az storage account blob-service-properties update \
  --account-name <yourStorageAccount> \
  --enable-versioning true

# Create blob container for archived billing records
az storage container create \
  --name billing-archive \
  --account-name <yourStorageAccount>

# (Optional) Create a metadata table to track archived IDs
az cosmosdb table create \
  --resource-group <yourRG> \
  --account-name <yourCosmosDBAccount> \
  --name billingArchiveMeta

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Latency for old data retrieval | Use **Cool tier** instead of Archive for faster access |
| Data loss during migration | Test archival logic with sample data; enable blob versioning |
| Heavy reads on archived data | Add optional Redis caching for recent cold data |
| Function errors | Add logging, retry policies, and monitoring alerts |

## Bonus Ideas

- Implement an analytics dashboard to track cost savings over time
- Enable tagging of blobs by date/month for easy lifecycle management
- Schedule lifecycle rules to auto-delete blobs older than X years (compliance)

## How This Meets the HR Requirements

| Requirement | Met? | Details |
|-------------|--------|---------|
| No data loss | Archival function saves all records before deletion |
| No downtime |  Background job; no disruption to live APIs |
| No API changes | Proxy logic handles source selection behind-the-scenes |
| Simplicity | Uses native Azure tools (Cosmos DB, Blob, Functions) |
| Cost optimization | Cosmos DB cost reduced significantly by offloading cold data |

## Conclusion

This serverless hybrid architecture is:

- Simple to deploy
- Cost-efficient
- Robust and scalable
- Fully meets business and technical requirements

It ensures old billing records remain available without incurring unnecessary Cosmos DB costs, and future-proofs the system as it scales.
