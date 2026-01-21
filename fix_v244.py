#!/usr/bin/env python3
"""
v2.44: Add Serper.dev support for external link SERP
- Falls back to Serper.dev if Google CSE fails or isn't configured
- New variable: SERPER_API_KEY
"""
import json
import re

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
# 1. Add SERPER_API_KEY to globals
# =============================================================================

old_globals = """  SPEEDYINDEX_API_KEY: $vars.SPEEDYINDEX_API_KEY || '',
  TELEGRAM_BOT_TOKEN: $vars.TELEGRAM_BOT_TOKEN || '',"""

new_globals = """  SPEEDYINDEX_API_KEY: $vars.SPEEDYINDEX_API_KEY || '',
  SERPER_API_KEY: $vars.SERPER_API_KEY || '',
  TELEGRAM_BOT_TOKEN: $vars.TELEGRAM_BOT_TOKEN || '',"""

code = code.replace(old_globals, new_globals)

# =============================================================================
# 2. Add serperKey to config
# =============================================================================

old_config_serp = """  googleCseKey: globals.GOOGLE_CSE_API_KEY || '',
  googleCseCx: globals.GOOGLE_CSE_CX || '',"""

new_config_serp = """  googleCseKey: globals.GOOGLE_CSE_API_KEY || '',
  googleCseCx: globals.GOOGLE_CSE_CX || '',
  serperKey: globals.SERPER_API_KEY || '',"""

code = code.replace(old_config_serp, new_config_serp)

# =============================================================================
# 3. Replace fetchSerpHints to support both Google CSE and Serper.dev
# =============================================================================

old_fetch_serp = '''async function fetchSerpHints() {
  if (!config.googleCseKey || !config.googleCseCx) return [];
  try {
    const resp = await httpRequest.call(this, {
      method: 'GET',
      url: `https://www.googleapis.com/customsearch/v1?key=${config.googleCseKey}&cx=${config.googleCseCx}&q=${encodeURIComponent(config.topic)}&num=10`
    });
    const results = (resp?.items || []).map(item => ({ title: item.title, url: item.link, snippet: item.snippet }));
    debug.serp_count = results.length;
    return results;
  } catch (e) {
    debug.wp_errors.push({ step: 'SERP', error: e.message });
    return [];
  }
}'''

new_fetch_serp = '''async function fetchSerpHints() {
  // v2.44: Try Google CSE first, fall back to Serper.dev
  
  // Try Google CSE
  if (config.googleCseKey && config.googleCseCx) {
    try {
      const resp = await httpRequest.call(this, {
        method: 'GET',
        url: `https://www.googleapis.com/customsearch/v1?key=${config.googleCseKey}&cx=${config.googleCseCx}&q=${encodeURIComponent(config.topic)}&num=10`
      });
      const results = (resp?.items || []).map(item => ({ title: item.title, url: item.link, snippet: item.snippet }));
      if (results.length > 0) {
        debug.serp_count = results.length;
        debug.serp_provider = 'google_cse';
        return results;
      }
    } catch (e) {
      debug.wp_errors.push({ step: 'SERP_GOOGLE_CSE', error: e.message });
    }
  }
  
  // Fallback to Serper.dev
  if (config.serperKey) {
    try {
      const resp = await httpRequest.call(this, {
        method: 'POST',
        url: 'https://google.serper.dev/search',
        headers: {
          'X-API-KEY': config.serperKey,
          'Content-Type': 'application/json'
        },
        body: { q: config.topic, num: 10 }
      });
      const results = (resp?.organic || []).map(item => ({ 
        title: item.title, 
        url: item.link, 
        snippet: item.snippet 
      }));
      debug.serp_count = results.length;
      debug.serp_provider = 'serper';
      return results;
    } catch (e) {
      debug.wp_errors.push({ step: 'SERP_SERPER', error: e.message });
    }
  }
  
  debug.serp_provider = 'none';
  return [];
}'''

code = code.replace(old_fetch_serp, new_fetch_serp)

# =============================================================================
# 4. Add serp_provider to debug object
# =============================================================================

old_debug = """const debug = {
  serp_count: 0,
  youtube_candidates_count: 0,"""

new_debug = """const debug = {
  serp_count: 0,
  serp_provider: 'none',
  youtube_candidates_count: 0,"""

code = code.replace(old_debug, new_debug)

# =============================================================================
# 5. Update version
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.43",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.44"
)

old_changelog = """* v2.43 Changes:
 * - YouTube: Now searches per-section heading for much better relevance
 * - YouTube: Combines section title + topic for search query
 * - Falls back to pre-fetched candidates if per-section search fails"""

new_changelog = """* v2.44 Changes:
 * - Added Serper.dev as fallback SERP provider (new var: SERPER_API_KEY)
 * - Google CSE tried first, Serper.dev as fallback
 * - debug.serp_provider shows which service was used
 * 
 * v2.43 Changes:
 * - YouTube: Now searches per-section heading for much better relevance"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.44-serper-support'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.44 updates applied:")
print("   - Added Serper.dev support as fallback SERP provider")
print("   - New variable: SERPER_API_KEY")
print("   - Google CSE tried first, then Serper.dev")
print("   - debug.serp_provider shows which was used")
print("   - Version: v2.44-serper-support")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "serperKey" in code_verify and "google.serper.dev" in code_verify:
    print("✅ Verified: Serper.dev support present")
else:
    print("❌ Warning: Serper.dev may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
