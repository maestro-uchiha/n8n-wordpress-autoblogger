#!/usr/bin/env python3
"""
Fix v2.42: Filter out YouTube Shorts from search results
"""
import json

# Load the Publisher JSON
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
# FIX: Filter out YouTube Shorts from search results
# =============================================================================

old_youtube_fetch = '''async function fetchYouTubeCandidates() {
  if (!config.youtubeKey || config.youtubeCount === 0) return [];
  try {
    const resp = await httpRequest.call(this, {
      method: 'GET',
      url: `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(config.topic)}&type=video&maxResults=5&key=${config.youtubeKey}`
    });
    const results = (resp?.items || []).map(item => ({
      videoId: item.id?.videoId,
      title: item.snippet?.title || 'Related Video',
      url: `https://www.youtube.com/watch?v=${item.id?.videoId}`
    }));
    debug.youtube_candidates_count = results.length;
    return results;
  } catch (e) {
    debug.wp_errors.push({ step: 'YOUTUBE', error: e.message });
    return [];
  }
}'''

# Add videoDuration=medium to exclude shorts (under 4 min) and filter by title
new_youtube_fetch = '''async function fetchYouTubeCandidates() {
  if (!config.youtubeKey || config.youtubeCount === 0) return [];
  try {
    // v2.42: Use videoDuration=medium to exclude Shorts (under 4 min)
    // Also fetch more results (15) so we have options after filtering
    const resp = await httpRequest.call(this, {
      method: 'GET',
      url: `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(config.topic)}&type=video&videoDuration=medium&maxResults=15&key=${config.youtubeKey}`
    });
    
    // Filter out any remaining shorts by title (some slip through)
    const shortsKeywords = ['#shorts', '#short', 'shorts', '60 sec', '30 sec', 'tiktok'];
    const results = (resp?.items || [])
      .filter(item => {
        const title = (item.snippet?.title || '').toLowerCase();
        return !shortsKeywords.some(kw => title.includes(kw));
      })
      .slice(0, 5) // Keep top 5 after filtering
      .map(item => ({
        videoId: item.id?.videoId,
        title: item.snippet?.title || 'Related Video',
        url: `https://www.youtube.com/watch?v=${item.id?.videoId}`
      }));
    
    debug.youtube_candidates_count = results.length;
    return results;
  } catch (e) {
    debug.wp_errors.push({ step: 'YOUTUBE', error: e.message });
    return [];
  }
}'''

code = code.replace(old_youtube_fetch, new_youtube_fetch)

# =============================================================================
# Update version
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.41",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.42"
)

old_changelog = """* v2.41 Changes:
 * - REWRITE: Images always distributed by H2 sections (ignores AI placement)
 * - REWRITE: YouTube placed in middle sections (images in early sections)
 * - FIX: Never places media in Conclusion/FAQ sections
 * - FIX: Prevents image+YouTube clustering"""

new_changelog = """* v2.42 Changes:
 * - FIX: Filter out YouTube Shorts (uses videoDuration=medium API param)
 * - FIX: Also filters titles containing #shorts, tiktok, etc.
 * 
 * v2.41 Changes:
 * - Images distributed across early H2 sections
 * - YouTube distributed across middle H2 sections
 * - Never places media in Conclusion/FAQ sections"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.42-no-shorts'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.42 updates applied:")
print("   - YouTube: Added videoDuration=medium to exclude Shorts")
print("   - YouTube: Filters titles containing #shorts, tiktok, etc.")
print("   - Version: v2.42-no-shorts")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "videoDuration=medium" in code_verify:
    print("✅ Verified: videoDuration=medium parameter present")
else:
    print("❌ Warning: videoDuration parameter may not have applied")

if "shortsKeywords" in code_verify:
    print("✅ Verified: Shorts title filter present")
else:
    print("❌ Warning: Title filter may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
