#!/usr/bin/env python3
"""
Fix Master Scheduler v2.4:
1. Fix last_posted_at update - use row_number instead of site_id matching
2. Add better error handling and logging
"""
import json

# Load the Master Scheduler JSON
with open('v2/1_Master_Scheduler.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find and fix the "Update Site last_posted_at" node
for node in workflow['nodes']:
    if node['id'] == 'update-site-001':
        # Change to use row_number for matching instead of site_id
        # This is more reliable because row_number is always accurate
        node['parameters']['columns'] = {
            "mappingMode": "defineBelow",
            "value": {
                "row_number": "={{ $json.site?.row_number || $json.site_config?.row_number }}",
                "last_posted_at": "={{ $now.toISO() }}"
            },
            "matchingColumns": ["row_number"],
            "schema": [
                { "id": "row_number", "displayName": "row_number", "type": "number", "canBeUsedToMatch": True },
                { "id": "last_posted_at", "displayName": "last_posted_at", "type": "string", "canBeUsedToMatch": False }
            ]
        }
        print("✅ Fixed: Update Site last_posted_at - now uses row_number matching")
        
    # Also fix Mark Topic DONE to use row_number
    if node['id'] == 'mark-done-001':
        node['parameters']['columns'] = {
            "mappingMode": "defineBelow",
            "value": {
                "row_number": "={{ $json.topicRow?.row_number }}",
                "status": "DONE",
                "post_id": "={{ $json.post_id }}",
                "post_url": "={{ $json.post_url }}",
                "error": "",
                "locked_at": "",
                "updated_at": "={{ $now.toISO() }}"
            },
            "matchingColumns": ["row_number"],
            "schema": [
                { "id": "row_number", "displayName": "row_number", "type": "number", "canBeUsedToMatch": True },
                { "id": "status", "displayName": "status", "type": "string", "canBeUsedToMatch": False },
                { "id": "post_id", "displayName": "post_id", "type": "string", "canBeUsedToMatch": False },
                { "id": "post_url", "displayName": "post_url", "type": "string", "canBeUsedToMatch": False },
                { "id": "error", "displayName": "error", "type": "string", "canBeUsedToMatch": False },
                { "id": "locked_at", "displayName": "locked_at", "type": "string", "canBeUsedToMatch": False },
                { "id": "updated_at", "displayName": "updated_at", "type": "string", "canBeUsedToMatch": False }
            ]
        }
        print("✅ Fixed: Mark Topic DONE - now uses row_number matching")
    
    # Also fix Mark Topic FAILED
    if node['id'] == 'mark-failed-001':
        node['parameters']['columns'] = {
            "mappingMode": "defineBelow",
            "value": {
                "row_number": "={{ $json.topicRow?.row_number }}",
                "status": "FAILED",
                "error": "={{ $json.error || $json.failed_at_step || 'Unknown error' }}",
                "locked_at": ""
            },
            "matchingColumns": ["row_number"],
            "schema": [
                { "id": "row_number", "displayName": "row_number", "type": "number", "canBeUsedToMatch": True },
                { "id": "status", "displayName": "status", "type": "string", "canBeUsedToMatch": False },
                { "id": "error", "displayName": "error", "type": "string", "canBeUsedToMatch": False },
                { "id": "locked_at", "displayName": "locked_at", "type": "string", "canBeUsedToMatch": False }
            ]
        }
        print("✅ Fixed: Mark Topic FAILED - now uses row_number matching")

# Update version
workflow['versionId'] = 'v2.4-fix-updates'

# Save
with open('v2/1_Master_Scheduler.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print(f"\n📄 Master Scheduler updated to: {workflow['versionId']}")
print("\nIMPORTANT: Make sure your Google Sheets have a 'row_number' column!")
print("The n8n Google Sheets node automatically adds this when reading.")
