#!/usr/bin/env python3
"""
v2.45: Add FastIndex.eu as fallback for SpeedyIndex
- SpeedyIndex tried first, FastIndex as fallback
- New variable: FASTINDEX_API_KEY
"""
import json

with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the engine node
engine_node = None
for node in workflow['nodes']:
    if node['id'] == 'engine-001':
        engine_node = node
        break

if not engine_node:
    print("ERROR: Could not find engine-001 node")
    exit(1)

code = engine_node['parameters']['jsCode']

# =============================================================================
# 1. Add FASTINDEX_API_KEY to globals
# =============================================================================

old_globals = """  SERPER_API_KEY: $vars.SERPER_API_KEY || '',
  TELEGRAM_BOT_TOKEN: $vars.TELEGRAM_BOT_TOKEN || '',"""

new_globals = """  SERPER_API_KEY: $vars.SERPER_API_KEY || '',
  FASTINDEX_API_KEY: $vars.FASTINDEX_API_KEY || '',
  TELEGRAM_BOT_TOKEN: $vars.TELEGRAM_BOT_TOKEN || '',"""

code = code.replace(old_globals, new_globals)

# =============================================================================
# 2. Add fastIndexKey to config
# =============================================================================

old_config = """  speedyIndexKey: globals.SPEEDYINDEX_API_KEY || '',
  telegramToken: globals.TELEGRAM_BOT_TOKEN || '',"""

new_config = """  speedyIndexKey: globals.SPEEDYINDEX_API_KEY || '',
  fastIndexKey: globals.FASTINDEX_API_KEY || '',
  telegramToken: globals.TELEGRAM_BOT_TOKEN || '',"""

code = code.replace(old_config, new_config)

# =============================================================================
# 3. Replace pingSpeedyIndex to support both SpeedyIndex and FastIndex
# =============================================================================

old_speedyindex = '''// v2.8: Per-site SpeedyIndex control
async function pingSpeedyIndex(postUrl) {
  if (!config.speedyindexEnabled) {
    debug.notifications.speedyindex = 'disabled_for_site';
    return false;
  }
  if (!config.speedyIndexKey) {
    debug.notifications.speedyindex = 'no_api_key';
    return false;
  }
  if (config.postStatus !== 'publish') {
    debug.notifications.speedyindex = 'post_not_published';
    return false;
  }
  try {
    await httpRequest.call(this, {
      method: 'POST',
      url: 'https://api.speedyindex.com/v1/index',
      headers: { 'Authorization': `Bearer ${config.speedyIndexKey}`, 'Content-Type': 'application/json' },
      body: { url: postUrl }
    });
    debug.notifications.speedyindex = true;
    return true;
  } catch (e) {
    debug.wp_errors.push({ step: 'SPEEDYINDEX', error: e.message });
    debug.notifications.speedyindex = `error: ${e.message}`;
    return false;
  }
}'''

new_speedyindex = '''// v2.45: SpeedyIndex with FastIndex fallback
async function pingSpeedyIndex(postUrl) {
  if (!config.speedyindexEnabled) {
    debug.notifications.speedyindex = 'disabled_for_site';
    return false;
  }
  if (config.postStatus !== 'publish') {
    debug.notifications.speedyindex = 'post_not_published';
    return false;
  }
  
  // Try SpeedyIndex first
  if (config.speedyIndexKey) {
    try {
      await httpRequest.call(this, {
        method: 'POST',
        url: 'https://api.speedyindex.com/v1/index',
        headers: { 'Authorization': `Bearer ${config.speedyIndexKey}`, 'Content-Type': 'application/json' },
        body: { url: postUrl }
      });
      debug.notifications.speedyindex = 'speedyindex_success';
      return true;
    } catch (e) {
      debug.wp_errors.push({ step: 'SPEEDYINDEX', error: e.message });
    }
  }
  
  // Fallback to FastIndex.eu
  if (config.fastIndexKey) {
    try {
      const resp = await httpRequest.call(this, {
        method: 'POST',
        url: 'https://host060126.eu/api/links',
        headers: { 
          'Authorization': `Bearer ${config.fastIndexKey}`, 
          'Content-Type': 'application/json' 
        },
        body: { 
          method: 'gold',
          links: [postUrl]
        }
      });
      if (resp?.status === 201 || resp?.msg?.includes('success')) {
        debug.notifications.speedyindex = 'fastindex_success';
        return true;
      }
      debug.wp_errors.push({ step: 'FASTINDEX', error: resp?.message || 'Unknown error' });
    } catch (e) {
      debug.wp_errors.push({ step: 'FASTINDEX', error: e.message });
    }
  }
  
  debug.notifications.speedyindex = 'no_indexing_service';
  return false;
}'''

code = code.replace(old_speedyindex, new_speedyindex)

# =============================================================================
# 4. Update version
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.44",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.45"
)

old_changelog = """* v2.44 Changes:
 * - Added Serper.dev as fallback SERP provider (new var: SERPER_API_KEY)
 * - Google CSE tried first, Serper.dev as fallback
 * - debug.serp_provider shows which service was used"""

new_changelog = """* v2.45 Changes:
 * - Added FastIndex.eu as fallback indexing service (new var: FASTINDEX_API_KEY)
 * - SpeedyIndex tried first, FastIndex as fallback
 * - debug.notifications.speedyindex shows which service was used
 * 
 * v2.44 Changes:
 * - Added Serper.dev as fallback SERP provider (SERPER_API_KEY)"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.45-fastindex-fallback'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.45 updates applied:")
print("   - Added FastIndex.eu as fallback for SpeedyIndex")
print("   - New variable: FASTINDEX_API_KEY")
print("   - SpeedyIndex tried first, FastIndex as fallback")
print("   - debug shows: speedyindex_success / fastindex_success / no_indexing_service")
print("   - Version: v2.45-fastindex-fallback")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "fastIndexKey" in code_verify and "host060126.eu" in code_verify:
    print("✅ Verified: FastIndex support present")
else:
    print("❌ Warning: FastIndex may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
