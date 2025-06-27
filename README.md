# Azure Cost Optimization for Billing Records

## Problem
Over time, the Azure Cosmos DB storing billing records has grown large and expensive. It is a read-heavy system, but records older than 3 months are rarely accessed.

## Objective
Optimize storage cost while maintaining:
- API contract (no change for clients)
- Data availability (even for old records)
- Zero downtime and zero data loss
- Simple implementation

## Solution
We propose a **Hot + Cold Storage** architecture:
- Keep last 3 months' data in Cosmos DB (Hot)
- Move older data to Azure Blob Storage (Cold)
- Use Azure Function proxy to fetch old data from Blob

