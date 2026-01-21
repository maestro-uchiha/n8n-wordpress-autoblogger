#!/usr/bin/env python3
"""
Fix v2.43: YouTube videos matched to section headings
- Search YouTube with the H2 heading where video will be placed
- Much more relevant results
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
# FIX: YouTube search - use section heading instead of main topic
# =============================================================================

old_youtube_inject = '''// v2.41: YouTube embeds distributed by H2 sections (different sections than images)
function injectYouTubeEmbeds(content, anchorPhrases, youtubeCandidates) {
  if (config.youtubeCount === 0 || !youtubeCandidates?.length) return content;
  let modifiedContent = content;
  let inserted = 0;
  const usedVideos = new Set();
  const shuffledVideos = [...youtubeCandidates].sort(() => Math.random() - 0.5);
  
  // Remove any AI-placed YouTube placeholders (we'll distribute ourselves)
  modifiedContent = modifiedContent.replace(/<!-- YTVID context="[^"]+" -->/g, '');
  
  // Find H2 sections (excluding Conclusion, FAQs, Summary at the end)
  const h2Regex = /<h2[^>]*>([^<]*)<\\/h2>/gi;
  const h2Matches = [...modifiedContent.matchAll(h2Regex)];
  
  // Filter out ending sections
  const endingSections = ['conclusion', 'faq', 'summary', 'final', 'wrap'];
  const usableH2s = h2Matches.filter(m => {
    const title = m[1].toLowerCase();
    return !endingSections.some(s => title.includes(s));
  });
  
  if (usableH2s.length === 0) {
    debug.youtube_embeds_inserted = 0;
    return modifiedContent;
  }
  
  // Place YouTube in MIDDLE sections (images go in early sections)
  // This prevents clustering
  const embedCount = Math.min(config.youtubeCount, shuffledVideos.length, usableH2s.length);
  const midPoint = Math.floor(usableH2s.length / 2);
  
  // Insert embeds (in reverse order to preserve indices)
  const insertPositions = [];
  for (let i = 0; i < embedCount; i++) {
    // Start from middle, alternate forward/backward
    let sectionIdx;
    if (embedCount === 1) {
      sectionIdx = midPoint;
    } else {
      sectionIdx = midPoint + (i % 2 === 0 ? Math.floor(i/2) : -Math.ceil(i/2));
      sectionIdx = Math.max(0, Math.min(sectionIdx, usableH2s.length - 1));
    }
    
    const h2Match = usableH2s[sectionIdx];
    const video = shuffledVideos[i];
    if (h2Match && video && !usedVideos.has(video.videoId)) {
      insertPositions.push({
        index: h2Match.index + h2Match[0].length,
        video: video
      });
      usedVideos.add(video.videoId);
    }
  }
  
  // Sort by position descending and insert
  insertPositions.sort((a, b) => b.index - a.index);
  for (const pos of insertPositions) {
    const embedBlock = `

https://www.youtube.com/watch?v=${pos.video.videoId}

<p style="text-align:center;font-style:italic;color:#666;margin-top:-10px;">${pos.video.title}</p>

`;
    modifiedContent = modifiedContent.slice(0, pos.index) + embedBlock + modifiedContent.slice(pos.index);
    inserted++;
  }
  
  debug.youtube_embeds_inserted = inserted;
  return modifiedContent;
}'''

# New version that takes section context and searches per-section
new_youtube_inject = '''// v2.43: YouTube embeds matched to section headings for relevance
async function injectYouTubeEmbeds(content, anchorPhrases, youtubeCandidates) {
  if (config.youtubeCount === 0) return content;
  let modifiedContent = content;
  let inserted = 0;
  const usedVideos = new Set();
  
  // Remove any AI-placed YouTube placeholders
  modifiedContent = modifiedContent.replace(/<!-- YTVID context="[^"]+" -->/g, '');
  
  // Find H2 sections (excluding Conclusion, FAQs, Summary at the end)
  const h2Regex = /<h2[^>]*>([^<]*)<\\/h2>/gi;
  const h2Matches = [...modifiedContent.matchAll(h2Regex)];
  
  // Filter out ending sections
  const endingSections = ['conclusion', 'faq', 'summary', 'final', 'wrap'];
  const usableH2s = h2Matches.filter(m => {
    const title = m[1].toLowerCase();
    return !endingSections.some(s => title.includes(s));
  });
  
  if (usableH2s.length === 0) {
    debug.youtube_embeds_inserted = 0;
    return modifiedContent;
  }
  
  // Place YouTube in MIDDLE sections
  const embedCount = Math.min(config.youtubeCount, usableH2s.length);
  const midPoint = Math.floor(usableH2s.length / 2);
  
  // Determine which sections get videos
  const sectionsForVideos = [];
  for (let i = 0; i < embedCount; i++) {
    let sectionIdx;
    if (embedCount === 1) {
      sectionIdx = midPoint;
    } else {
      sectionIdx = midPoint + (i % 2 === 0 ? Math.floor(i/2) : -Math.ceil(i/2));
      sectionIdx = Math.max(0, Math.min(sectionIdx, usableH2s.length - 1));
    }
    if (!sectionsForVideos.includes(sectionIdx)) {
      sectionsForVideos.push(sectionIdx);
    }
  }
  
  // v2.43: Search YouTube for EACH section heading for better relevance
  const insertPositions = [];
  for (const sectionIdx of sectionsForVideos) {
    const h2Match = usableH2s[sectionIdx];
    if (!h2Match) continue;
    
    const sectionTitle = h2Match[1].trim();
    
    // Search YouTube with section heading + topic for context
    const searchQuery = `${sectionTitle} ${config.topic}`.substring(0, 100);
    
    try {
      const resp = await httpRequest.call(this, {
        method: 'GET',
        url: `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(searchQuery)}&type=video&videoDuration=medium&maxResults=5&key=${config.youtubeKey}`
      });
      
      // Filter shorts and find unused video
      const shortsKeywords = ['#shorts', '#short', 'shorts', '60 sec', '30 sec', 'tiktok'];
      const videos = (resp?.items || [])
        .filter(item => {
          const title = (item.snippet?.title || '').toLowerCase();
          return !shortsKeywords.some(kw => title.includes(kw));
        })
        .map(item => ({
          videoId: item.id?.videoId,
          title: item.snippet?.title || 'Related Video'
        }));
      
      const video = videos.find(v => v.videoId && !usedVideos.has(v.videoId));
      if (video) {
        insertPositions.push({
          index: h2Match.index + h2Match[0].length,
          video: video,
          sectionTitle: sectionTitle
        });
        usedVideos.add(video.videoId);
      }
    } catch (e) {
      debug.wp_errors.push({ step: 'YOUTUBE_SECTION_SEARCH', section: sectionTitle, error: e.message });
      // Fall back to pre-fetched candidates if section search fails
      if (youtubeCandidates?.length > 0) {
        const video = youtubeCandidates.find(v => !usedVideos.has(v.videoId));
        if (video) {
          insertPositions.push({
            index: h2Match.index + h2Match[0].length,
            video: video,
            sectionTitle: sectionTitle
          });
          usedVideos.add(video.videoId);
        }
      }
    }
  }
  
  // Sort by position descending and insert
  insertPositions.sort((a, b) => b.index - a.index);
  for (const pos of insertPositions) {
    const embedBlock = `

https://www.youtube.com/watch?v=${pos.video.videoId}

<p style="text-align:center;font-style:italic;color:#666;margin-top:-10px;">${pos.video.title}</p>

`;
    modifiedContent = modifiedContent.slice(0, pos.index) + embedBlock + modifiedContent.slice(pos.index);
    inserted++;
  }
  
  debug.youtube_embeds_inserted = inserted;
  return modifiedContent;
}'''

code = code.replace(old_youtube_inject, new_youtube_inject)

# Also need to update the call site to be async
old_call = '''currentStep = 'YOUTUBE_EMBEDS';
  if (config.youtubeCount > 0 && youtubeCandidates.length > 0) {
    executionLog.push({ step: currentStep, status: 'started' });
    processedHtml = injectYouTubeEmbeds(processedHtml, contentJson.youtube_anchor_phrases, youtubeCandidates);'''

new_call = '''currentStep = 'YOUTUBE_EMBEDS';
  if (config.youtubeCount > 0 && config.youtubeKey) {
    executionLog.push({ step: currentStep, status: 'started' });
    processedHtml = await injectYouTubeEmbeds.call(this, processedHtml, contentJson.youtube_anchor_phrases, youtubeCandidates);'''

code = code.replace(old_call, new_call)

# =============================================================================
# Update version
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.42",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.43"
)

old_changelog = """* v2.42 Changes:
 * - FIX: Filter out YouTube Shorts (uses videoDuration=medium API param)
 * - FIX: Also filters titles containing #shorts, tiktok, etc."""

new_changelog = """* v2.43 Changes:
 * - YouTube: Now searches per-section heading for much better relevance
 * - YouTube: Combines section title + topic for search query
 * - Falls back to pre-fetched candidates if per-section search fails
 * 
 * v2.42 Changes:
 * - Filter out YouTube Shorts (videoDuration=medium)"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.43-relevant-youtube'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.43 updates applied:")
print("   - YouTube: Now searches per-section for better relevance")
print("   - Search query: '{Section Heading} {Topic}'")
print("   - Falls back to pre-fetched if section search fails")
print("   - Version: v2.43-relevant-youtube")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "sectionTitle" in code_verify and "searchQuery" in code_verify:
    print("✅ Verified: Per-section YouTube search present")
else:
    print("❌ Warning: Per-section search may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
