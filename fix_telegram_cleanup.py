#!/usr/bin/env python3
"""
Fix two issues:
1. Publisher: Add indexing status to Telegram notification
2. Cleanup: Reset stuck posts to QUEUED instead of FAILED
"""
import json

# =============================================================================
# 1. FIX PUBLISHER - Add indexing status to Telegram notification
# =============================================================================
print("Fixing Publisher...")

with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    publisher = json.load(f)

for node in publisher['nodes']:
    if node['id'] == 'engine-001':
        code = node['parameters']['jsCode']
        
        # Find and update the notifyMessage
        old_notify = r'''const notifyMessage = `\u2705 <b>New Post Published</b>\\n\\n\ud83d\udcdd ${contentJson.title}\\n\ud83c\udf10 ${site.site_name || config.baseUrl}\\n\ud83d\udd17 ${postResp.link || 'Draft'}\\n\ud83d\udcca Images: ${debug.images_uploaded}/${debug.images_requested}\\n\ud83d\udd17 Internal: ${debug.internal_links_inserted}/${debug.internal_links_requested}\\n\ud83c\udf10 External: ${debug.external_links_inserted}/${debug.external_links_requested}\\n\ud83d\udcfa YouTube: ${debug.youtube_embeds_inserted}/${debug.youtube_embeds_requested}\\n\ud83c\udff7\ufe0f Categories: ${categoryIds.length}`;'''
        
        # Add indexing status with emoji
        new_notify = r'''const indexStatus = debug.notifications.speedyindex === 'speedyindex_success' ? '\u2705 SpeedyIndex' : 
                       debug.notifications.speedyindex === 'fastindex_success' ? '\u2705 FastIndex' : 
                       debug.notifications.speedyindex === 'disabled_for_site' ? '\u23f8\ufe0f Disabled' :
                       debug.notifications.speedyindex === 'post_not_published' ? '\u23f8\ufe0f Draft' :
                       '\u274c Failed';
  const notifyMessage = `\u2705 <b>New Post Published</b>\\n\\n\ud83d\udcdd ${contentJson.title}\\n\ud83c\udf10 ${site.site_name || config.baseUrl}\\n\ud83d\udd17 ${postResp.link || 'Draft'}\\n\ud83d\udcca Images: ${debug.images_uploaded}/${debug.images_requested}\\n\ud83d\udd17 Internal: ${debug.internal_links_inserted}/${debug.internal_links_requested}\\n\ud83c\udf10 External: ${debug.external_links_inserted}/${debug.external_links_requested}\\n\ud83d\udcfa YouTube: ${debug.youtube_embeds_inserted}/${debug.youtube_embeds_requested}\\n\ud83c\udff7\ufe0f Categories: ${categoryIds.length}\\n\ud83d\udd0d Indexing: ${indexStatus}`;'''
        
        if old_notify in code:
            code = code.replace(old_notify, new_notify)
            node['parameters']['jsCode'] = code
            print("  ✅ Added indexing status to Telegram notification")
        else:
            print("  ❌ Could not find notifyMessage pattern")
        break

with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(publisher, f, indent=2)

# =============================================================================
# 2. FIX CLEANUP - Reset to QUEUED instead of FAILED
# =============================================================================
print("\nFixing Cleanup...")

with open('v2/3_Cleanup.json', 'r', encoding='utf-8') as f:
    cleanup = json.load(f)

for node in cleanup['nodes']:
    if node['id'] == 'reset-stuck-001':
        # Update the columns value
        if 'columns' in node['parameters'] and 'value' in node['parameters']['columns']:
            cols = node['parameters']['columns']['value']
            if cols.get('status') == 'FAILED':
                cols['status'] = 'QUEUED'
                cols['error'] = ''  # Clear error since it's being requeued
                print("  ✅ Changed status from FAILED to QUEUED")
            
        # Also update the node name for clarity
        if node['name'] == 'Reset to FAILED':
            node['name'] = 'Reset to QUEUED'
            print("  ✅ Renamed node to 'Reset to QUEUED'")
        break

with open('v2/3_Cleanup.json', 'w', encoding='utf-8') as f:
    json.dump(cleanup, f, indent=2)

print("\n✅ Both fixes applied!")
print("   - Publisher: Telegram now shows indexing status")
print("   - Cleanup: Stuck posts reset to QUEUED (not FAILED)")
