from datetime import datetime
import random

MOCK_RESOURCES = [
    {"name": "vm-web-prod-01", "type": "VirtualMachine", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Running", "location": "eastus", "tags": {"env": "prod", "team": "web"}},
    {"name": "vm-web-prod-02", "type": "VirtualMachine", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Running", "location": "eastus", "tags": {"env": "prod", "team": "web"}},
    {"name": "vm-db-prod-01", "type": "VirtualMachine", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Running", "location": "eastus", "tags": {"env": "prod", "team": "db"}},
    {"name": "aks-cluster-prod", "type": "AKS", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Running", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "aks-cluster-dev", "type": "AKS", "subscription_id": "sub-002", "resource_group": "rg-dev", "status": "Running", "location": "westus", "tags": {"env": "dev"}},
    {"name": "storage-prod-001", "type": "StorageAccount", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Available", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "storage-backup-001", "type": "StorageAccount", "subscription_id": "sub-001", "resource_group": "rg-backup", "status": "Available", "location": "eastus2", "tags": {"env": "prod", "purpose": "backup"}},
    {"name": "appservice-api-prod", "type": "AppService", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Running", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "appservice-web-prod", "type": "AppService", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Running", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "sql-prod-001", "type": "SQLDatabase", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Online", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "sql-dev-001", "type": "SQLDatabase", "subscription_id": "sub-002", "resource_group": "rg-dev", "status": "Online", "location": "westus", "tags": {"env": "dev"}},
    {"name": "keyvault-prod-001", "type": "KeyVault", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Active", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "vnet-prod-001", "type": "VirtualNetwork", "subscription_id": "sub-001", "resource_group": "rg-networking", "status": "Active", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "redis-cache-prod", "type": "RedisCache", "subscription_id": "sub-001", "resource_group": "rg-production", "status": "Running", "location": "eastus", "tags": {"env": "prod"}},
    {"name": "vm-legacy-001", "type": "VirtualMachine", "subscription_id": "sub-003", "resource_group": "rg-legacy", "status": "Stopped", "location": "eastus", "tags": {"env": "legacy", "deprecated": "true"}},
]

def get_inventory(subscription=None, resource_group=None, resource_type=None):
    resources = MOCK_RESOURCES.copy()
    if subscription:
        resources = [r for r in resources if r["subscription_id"] == subscription]
    if resource_group:
        resources = [r for r in resources if r["resource_group"] == resource_group]
    if resource_type:
        resources = [r for r in resources if r["type"].lower() == resource_type.lower()]
    return resources

def get_subscriptions():
    return list(set(r["subscription_id"] for r in MOCK_RESOURCES))

def get_resource_groups(subscription=None):
    resources = MOCK_RESOURCES if not subscription else [r for r in MOCK_RESOURCES if r["subscription_id"] == subscription]
    return list(set(r["resource_group"] for r in resources))
