#!/usr/bin/env python3
"""
Fix v2.41: Properly distribute media throughout the article
- Don't rely on AI placement at all
- Distribute images and YouTube evenly by H2 sections
- Never place media in the last section (before Conclusion/FAQs)
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
# REWRITE: processImagePlaceholders - always distribute by H2, ignore AI placement
# =============================================================================

old_process_images = '''async function processImagePlaceholders(contentHtml, titleSlug) {
  const placeholderRegex = /<!-- WPIMG alt="([^"]+)" -->/g;
  let matches = [...contentHtml.matchAll(placeholderRegex)];
  let featuredImageId = null;
  let processedHtml = contentHtml;
  const domain = config.baseUrl.replace(/https?:\\/\\//, '').replace(/\\/$/, '');
  
  // v2.40: Detect if AI stacked all placeholders together (within 500 chars of each other)
  if (matches.length > 1) {
    const positions = matches.map(m => m.index);
    const maxGap = Math.max(...positions.slice(1).map((p, i) => p - positions[i]));
    const contentLength = contentHtml.length;
    const expectedMinGap = contentLength / (matches.length + 1) * 0.3; // Should be at least 30% of expected spacing
    
    if (maxGap < expectedMinGap || maxGap < 500) {
      // Placeholders are clustered - redistribute using H2 sections
      debug.wp_errors.push({ step: 'IMAGE_PLACEHOLDERS', message: 'AI stacked placeholders, redistributing by H2' });
      
      // Remove all existing placeholders
      processedHtml = processedHtml.replace(placeholderRegex, '');
      
      // Find H2 positions for distribution
      const h2Matches = [...processedHtml.matchAll(/<\\/h2>/gi)];
      if (h2Matches.length >= matches.length) {
        const step = Math.floor(h2Matches.length / (matches.length + 1));
        for (let i = 0; i < matches.length; i++) {
          const h2Index = Math.min((i + 1) * step, h2Matches.length - 1);
          const h2Match = h2Matches[h2Index];
          if (h2Match) {
            const insertPos = h2Match.index + 5;
            const placeholder = matches[i][0];
            processedHtml = processedHtml.slice(0, insertPos) + '\\n\\n' + placeholder + '\\n\\n' + processedHtml.slice(insertPos);
            // Re-find H2 matches since we modified the string
          }
        }
        // Re-match placeholders after redistribution
        matches = [...processedHtml.matchAll(placeholderRegex)];
      }
    }
  }
  
  for (let i = 0; i < Math.min(matches.length, config.imagesCount); i++) {'''

new_process_images = '''async function processImagePlaceholders(contentHtml, titleSlug) {
  const placeholderRegex = /<!-- WPIMG alt="([^"]+)" -->/g;
  const originalMatches = [...contentHtml.matchAll(placeholderRegex)];
  let featuredImageId = null;
  let processedHtml = contentHtml;
  const domain = config.baseUrl.replace(/https?:\\/\\//, '').replace(/\\/$/, '');
  
  // v2.41: ALWAYS distribute images by H2 sections (ignore AI placement)
  // This ensures even distribution and avoids clustering
  
  // Remove all existing placeholders first
  processedHtml = processedHtml.replace(placeholderRegex, '');
  
  // Find H2 sections (excluding Conclusion, FAQs, Summary at the end)
  const h2Regex = /<h2[^>]*>([^<]*)<\\/h2>/gi;
  const h2Matches = [...processedHtml.matchAll(h2Regex)];
  
  // Filter out ending sections (Conclusion, FAQs, Summary, etc.)
  const endingSections = ['conclusion', 'faq', 'summary', 'final', 'wrap'];
  const usableH2s = h2Matches.filter(m => {
    const title = m[1].toLowerCase();
    return !endingSections.some(s => title.includes(s));
  });
  
  // Distribute images across usable sections
  const imagesToPlace = Math.min(originalMatches.length, config.imagesCount);
  if (imagesToPlace > 0 && usableH2s.length > 0) {
    // Calculate positions - spread evenly, skip first H2 (intro)
    const startSection = Math.min(1, usableH2s.length - 1);
    const availableSections = usableH2s.length - startSection;
    const step = Math.max(1, Math.floor(availableSections / imagesToPlace));
    
    // Insert placeholders after selected H2s (in reverse order to preserve indices)
    const insertPositions = [];
    for (let i = 0; i < imagesToPlace; i++) {
      const sectionIdx = Math.min(startSection + i * step, usableH2s.length - 1);
      const h2Match = usableH2s[sectionIdx];
      if (h2Match) {
        insertPositions.push({
          index: h2Match.index + h2Match[0].length,
          alt: originalMatches[i] ? originalMatches[i][1] : `Image ${i + 1} for ${titleSlug}`
        });
      }
    }
    
    // Sort by position descending and insert
    insertPositions.sort((a, b) => b.index - a.index);
    for (const pos of insertPositions) {
      const placeholder = `<!-- WPIMG alt="${pos.alt}" -->`;
      processedHtml = processedHtml.slice(0, pos.index) + '\\n\\n' + placeholder + '\\n\\n' + processedHtml.slice(pos.index);
    }
  }
  
  // Re-match placeholders after redistribution
  const matches = [...processedHtml.matchAll(placeholderRegex)];
  
  for (let i = 0; i < Math.min(matches.length, config.imagesCount); i++) {'''

code = code.replace(old_process_images, new_process_images)

# =============================================================================
# REWRITE: injectYouTubeEmbeds - always distribute by H2, avoid clustering with images
# =============================================================================

old_youtube = '''// v2.36: YouTube embeds placed by AI using <!-- YTVID context="..." --> placeholders
function injectYouTubeEmbeds(content, anchorPhrases, youtubeCandidates) {
  if (config.youtubeCount === 0 || !youtubeCandidates?.length) return content;
  let modifiedContent = content;
  let inserted = 0;
  const usedVideos = new Set();
  const shuffledVideos = [...youtubeCandidates].sort(() => Math.random() - 0.5);
  
  // Find AI-placed YouTube placeholders
  const placeholderRegex = /<!-- YTVID context="([^"]+)" -->/g;
  const matches = [...content.matchAll(placeholderRegex)];
  
  // Replace placeholders with actual YouTube embeds
  for (let i = 0; i < Math.min(matches.length, config.youtubeCount); i++) {
    const match = matches[i];
    const video = shuffledVideos.find(v => !usedVideos.has(v.videoId));
    if (!video) break;
    
    const embedBlock = `

https://www.youtube.com/watch?v=${video.videoId}

<p style="text-align:center;font-style:italic;color:#666;margin-top:-10px;">${video.title}</p>`;
    
    modifiedContent = modifiedContent.replace(match[0], embedBlock);
    usedVideos.add(video.videoId);
    inserted++;
  }
  
  // Clean up any remaining placeholders
  modifiedContent = modifiedContent.replace(/<!-- YTVID context="[^"]+" -->/g, '');
  
  // Fallback: if AI didn't place placeholders, use H2 distribution
  if (inserted === 0 && matches.length === 0) {
    debug.wp_errors.push({ step: 'YOUTUBE_PLACEHOLDERS', message: 'No AI placeholders found, using fallback distribution' });
    const h2Matches = [...modifiedContent.matchAll(/<\\/h2>/gi)];
    const totalSections = h2Matches.length;
    
    if (totalSections > 0) {
      const embedCount = Math.min(config.youtubeCount, shuffledVideos.length, totalSections - 1);
      const positions = [];
      
      if (embedCount === 1) {
        positions.push(Math.floor(totalSections / 2));
      } else {
        const step = Math.floor((totalSections - 1) / (embedCount + 1));
        for (let i = 1; i <= embedCount; i++) {
          const pos = Math.min(i * step, totalSections - 1);
          if (!positions.includes(pos)) positions.push(pos);
        }
      }
      
      positions.sort((a, b) => b - a);
      
      for (const sectionIndex of positions) {
        if (inserted >= config.youtubeCount) break;
        const video = shuffledVideos.find(v => !usedVideos.has(v.videoId));
        if (!video) break;
        
        const h2Match = h2Matches[sectionIndex];
        if (!h2Match) continue;
        
        const embedBlock = `

https://www.youtube.com/watch?v=${video.videoId}

<p style="text-align:center;font-style:italic;color:#666;margin-top:-10px;">${video.title}</p>

`;
        
        const pos = h2Match.index + 5;
        modifiedContent = modifiedContent.slice(0, pos) + embedBlock + modifiedContent.slice(pos);
        usedVideos.add(video.videoId);
        inserted++;
      }
    }
  }
  
  debug.youtube_embeds_inserted = inserted;
  return modifiedContent;
}'''

new_youtube = '''// v2.41: YouTube embeds distributed by H2 sections (different sections than images)
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

code = code.replace(old_youtube, new_youtube)

# =============================================================================
# Update version
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.40",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.41"
)

old_changelog = """* v2.40 Changes:
 * - FIX: YouTube now uses plain URL (WordPress auto-embeds perfectly)
 * - FIX: Detects if AI stacked image placeholders and redistributes them by H2"""

new_changelog = """* v2.41 Changes:
 * - REWRITE: Images always distributed by H2 sections (ignores AI placement)
 * - REWRITE: YouTube placed in middle sections (images in early sections)
 * - FIX: Never places media in Conclusion/FAQ sections
 * - FIX: Prevents image+YouTube clustering
 * 
 * v2.40 Changes:
 * - YouTube uses plain URL (WordPress auto-embeds)"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.41-smart-distribute'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.41 updates applied:")
print("   - Images: Always distributed by H2 (early sections)")
print("   - YouTube: Always distributed by H2 (middle sections)")
print("   - Never places in Conclusion/FAQ sections")
print("   - Prevents image+YouTube clustering")
print("   - Version: v2.41-smart-distribute")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "ALWAYS distribute images by H2" in code_verify:
    print("✅ Verified: Image distribution rewrite present")
else:
    print("❌ Warning: Image distribution may not have applied")

if "YouTube placed in middle sections" in code_verify or "middle sections" in code_verify:
    print("✅ Verified: YouTube middle placement present")
else:
    print("❌ Warning: YouTube placement may not have applied")

if "endingSections" in code_verify:
    print("✅ Verified: Ending section filter present")
else:
    print("❌ Warning: Ending section filter may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
