#!/usr/bin/env python3
"""
Fix v2.6: Add Preserve Data node between Mark Topic DONE and Update Site last_posted_at
The Google Sheets node overwrites $json with its response, losing the original Publisher data.
"""
import json

with open('v2/1_Master_Scheduler.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the position of Update Site last_posted_at for positioning the new node
update_site_node = None
for node in workflow['nodes']:
    if node['name'] == 'Update Site last_posted_at':
        update_site_node = node
        break

if not update_site_node:
    print("ERROR: Could not find Update Site last_posted_at node")
    exit(1)

# Create the new Preserve Data node - position it between Mark Topic DONE and Update Site
preserve_node = {
    "parameters": {
        "jsCode": """/**
 * Preserve Publisher Data - Google Sheets node overwrites $json
 * We need to pass the original Publisher output to Update Site last_posted_at
 */
const publisherOutput = $('Execute Publisher').first().json;

return [{
  json: {
    site_row_number: publisherOutput.site?.row_number || publisherOutput.site_config?.row_number,
    site_id: publisherOutput.site?.site_id || publisherOutput.site_config?.site_id,
    post_id: publisherOutput.post_id,
    post_url: publisherOutput.post_url,
    ok: publisherOutput.ok
  }
}];
"""
    },
    "id": "preserve-data-001",
    "name": "Preserve Publisher Data",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [
        update_site_node['position'][0] - 110,  # Position before Update Site
        update_site_node['position'][1]
    ]
}

# Add the new node
workflow['nodes'].append(preserve_node)

# Update connections: Mark Topic DONE -> Preserve Publisher Data -> Update Site last_posted_at
workflow['connections']['Mark Topic DONE'] = {
    "main": [[{"node": "Preserve Publisher Data", "type": "main", "index": 0}]]
}

workflow['connections']['Preserve Publisher Data'] = {
    "main": [[{"node": "Update Site last_posted_at", "type": "main", "index": 0}]]
}

# Update the Update Site last_posted_at node to use the preserved data
for node in workflow['nodes']:
    if node['name'] == 'Update Site last_posted_at':
        node['parameters']['columns']['value']['row_number'] = "={{ $json.site_row_number }}"
        break

# Update version
workflow['versionId'] = 'v2.6-preserve-data'

# Save
with open('v2/1_Master_Scheduler.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.6 updates applied:")
print("   - Added 'Preserve Publisher Data' node after Mark Topic DONE")
print("   - This node extracts site_row_number from Publisher output")
print("   - Update Site last_posted_at now uses $json.site_row_number")
print("   - Version: v2.6-preserve-data")

# Verify
with open('v2/1_Master_Scheduler.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)

found_preserve = False
for node in verify['nodes']:
    if node['name'] == 'Preserve Publisher Data':
        found_preserve = True
        break

if found_preserve:
    print("✅ Verified: Preserve Publisher Data node added")
else:
    print("❌ Warning: Preserve Publisher Data node not found")

print(f"\n📄 Version: {verify['versionId']}")
