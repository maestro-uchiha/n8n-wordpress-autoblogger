#!/usr/bin/env python3
"""
Fix two issues:
1. Publisher: Add indexing status to Telegram notification
2. Cleanup: Already fixed to QUEUED
"""
import json

# =============================================================================
# FIX PUBLISHER - Add indexing status to Telegram notification
# =============================================================================
print("Fixing Publisher Telegram notification...")

with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    publisher = json.load(f)

for node in publisher['nodes']:
    if node['id'] == 'engine-001':
        code = node['parameters']['jsCode']
        
        # Find the current notification message and add indexing status
        # The message is constructed right after pingSpeedyIndex
        old_telegram = '''// Telegram (respects per-site setting)
  const notifyMessage = `✅ <b>New Post Published</b>\\n\\n📝 ${contentJson.title}\\n🌐 ${site.site_name || config.baseUrl}\\n🔗 ${postResp.link || 'Draft'}\\n📊 Images: ${debug.images_uploaded}/${debug.images_requested}\\n🔗 Internal: ${debug.internal_links_inserted}/${debug.internal_links_requested}\\n🌐 External: ${debug.external_links_inserted}/${debug.external_links_requested}\\n📺 YouTube: ${debug.youtube_embeds_inserted}/${debug.youtube_embeds_requested}\\n🏷️ Categories: ${categoryIds.length}`;
  await sendTelegramNotification.call(this, notifyMessage);'''
        
        new_telegram = '''// Telegram (respects per-site setting)
  const indexStatus = debug.notifications.speedyindex === 'speedyindex_success' ? '✅ SpeedyIndex' : 
                       debug.notifications.speedyindex === 'fastindex_success' ? '✅ FastIndex' : 
                       debug.notifications.speedyindex === 'disabled_for_site' ? '⏸️ Disabled' :
                       debug.notifications.speedyindex === 'post_not_published' ? '⏸️ Draft' :
                       '❌ Failed';
  const notifyMessage = `✅ <b>New Post Published</b>\\n\\n📝 ${contentJson.title}\\n🌐 ${site.site_name || config.baseUrl}\\n🔗 ${postResp.link || 'Draft'}\\n📊 Images: ${debug.images_uploaded}/${debug.images_requested}\\n🔗 Internal: ${debug.internal_links_inserted}/${debug.internal_links_requested}\\n🌐 External: ${debug.external_links_inserted}/${debug.external_links_requested}\\n📺 YouTube: ${debug.youtube_embeds_inserted}/${debug.youtube_embeds_requested}\\n🏷️ Categories: ${categoryIds.length}\\n🔍 Indexing: ${indexStatus}`;
  await sendTelegramNotification.call(this, notifyMessage);'''
        
        if old_telegram in code:
            code = code.replace(old_telegram, new_telegram)
            node['parameters']['jsCode'] = code
            print("  ✅ Added indexing status to Telegram notification")
        else:
            print("  ❌ Pattern not found - trying alternate approach")
            # Try finding just the notifyMessage line
            if 'Categories: ${categoryIds.length}`' in code and '🔍 Indexing' not in code:
                code = code.replace(
                    '🏷️ Categories: ${categoryIds.length}`;',
                    '🏷️ Categories: ${categoryIds.length}\\n🔍 Indexing: ${indexStatus}`;'
                )
                # Add indexStatus calculation before notifyMessage
                code = code.replace(
                    "// Telegram (respects per-site setting)\n  const notifyMessage",
                    "// Telegram (respects per-site setting)\n  const indexStatus = debug.notifications.speedyindex === 'speedyindex_success' ? '✅ SpeedyIndex' : \n                       debug.notifications.speedyindex === 'fastindex_success' ? '✅ FastIndex' : \n                       debug.notifications.speedyindex === 'disabled_for_site' ? '⏸️ Disabled' :\n                       debug.notifications.speedyindex === 'post_not_published' ? '⏸️ Draft' :\n                       '❌ Failed';\n  const notifyMessage"
                )
                node['parameters']['jsCode'] = code
                print("  ✅ Added indexing status (alternate method)")
        break

with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(publisher, f, indent=2)

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    check = json.load(f)
    
for node in check['nodes']:
    if node['id'] == 'engine-001':
        if 'indexStatus' in node['parameters']['jsCode'] and 'Indexing:' in node['parameters']['jsCode']:
            print("  ✅ Verified: indexStatus present in code")
        else:
            print("  ❌ Verification failed")
        break

print("\n✅ Done!")
