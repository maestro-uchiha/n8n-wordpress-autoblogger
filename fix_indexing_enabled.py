#!/usr/bin/env python3
"""
Rename speedyindex_enabled to indexing_enabled for generic indexing control
"""
import json

print("Renaming speedyindex_enabled to indexing_enabled...")

with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    publisher = json.load(f)

for node in publisher['nodes']:
    if node['id'] == 'engine-001':
        code = node['parameters']['jsCode']
        
        # Replace in config extraction (site.speedyindex_enabled -> site.indexing_enabled)
        code = code.replace(
            "speedyindexEnabled: site.speedyindex_enabled === true || String(site.speedyindex_enabled || '').toLowerCase() === 'true',",
            "indexingEnabled: site.indexing_enabled === true || String(site.indexing_enabled || '').toLowerCase() === 'true',"
        )
        
        # Replace in pingSpeedyIndex function
        code = code.replace(
            "if (!config.speedyindexEnabled) {",
            "if (!config.indexingEnabled) {"
        )
        
        # Update function comment
        code = code.replace(
            "// v2.45: SpeedyIndex with FastIndex fallback",
            "// v2.46: Generic indexing with SpeedyIndex/FastIndex fallback"
        )
        
        # Rename function to pingIndexingService for clarity
        code = code.replace(
            "async function pingSpeedyIndex(postUrl) {",
            "async function pingIndexingService(postUrl) {"
        )
        
        # Update call to the function
        code = code.replace(
            "await pingSpeedyIndex.call(this, postResp.link);",
            "await pingIndexingService.call(this, postResp.link);"
        )
        
        # Update version
        code = code.replace(
            "* AUTOBLOGGER PUBLISHER ENGINE v2.45",
            "* AUTOBLOGGER PUBLISHER ENGINE v2.46"
        )
        
        # Update changelog
        old_changelog = """* v2.45 Changes:
 * - Added FastIndex.eu as fallback indexing service (new var: FASTINDEX_API_KEY)
 * - SpeedyIndex tried first, FastIndex as fallback
 * - debug.notifications.speedyindex shows which service was used"""
        
        new_changelog = """* v2.46 Changes:
 * - Renamed speedyindex_enabled to indexing_enabled (generic control)
 * - Renamed function to pingIndexingService
 * 
 * v2.45 Changes:
 * - Added FastIndex.eu as fallback (FASTINDEX_API_KEY)"""
        
        code = code.replace(old_changelog, new_changelog)
        
        node['parameters']['jsCode'] = code
        print("  ✅ Updated engine code")
        break

# Update versionId
publisher['versionId'] = 'v2.46-indexing-enabled'

with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(publisher, f, indent=2)

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    check = json.load(f)
    
for node in check['nodes']:
    if node['id'] == 'engine-001':
        code = node['parameters']['jsCode']
        if 'indexingEnabled' in code and 'indexing_enabled' in code:
            print("  ✅ Verified: indexing_enabled present")
        else:
            print("  ❌ Verification failed")
        if 'pingIndexingService' in code:
            print("  ✅ Verified: pingIndexingService function present")
        break

print("\n✅ Done!")
print("\nSite Registry column change:")
print("  OLD: speedyindex_enabled (TRUE/FALSE)")
print("  NEW: indexing_enabled (TRUE/FALSE)")
