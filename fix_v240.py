#!/usr/bin/env python3
"""
Fix v2.40:
1. YouTube: Use plain URL on own line (WordPress auto-embeds this)
2. Better detection if AI stacked all placeholders together
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
# FIX 1: YouTube - use plain URL on its own line (WordPress auto-embeds)
# =============================================================================

# First embed block (in AI placeholder replacement)
old_embed_1 = '''const embedBlock = `<div class="youtube-embed-wrapper" style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;margin:20px 0;">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div>
<p class="youtube-caption"><em>${video.title}</em></p>`;'''

# Plain URL on its own line - WordPress auto-embeds this perfectly
new_embed_1 = '''const embedBlock = `

https://www.youtube.com/watch?v=${video.videoId}

<p style="text-align:center;font-style:italic;color:#666;margin-top:-10px;">${video.title}</p>`;'''

code = code.replace(old_embed_1, new_embed_1)

# Second embed block (in H2 fallback)
old_embed_2 = '''const embedBlock = `

<div class="youtube-embed-wrapper" style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;margin:20px 0;">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div>
<p class="youtube-caption"><em>${video.title}</em></p>

`;'''

new_embed_2 = '''const embedBlock = `

https://www.youtube.com/watch?v=${video.videoId}

<p style="text-align:center;font-style:italic;color:#666;margin-top:-10px;">${video.title}</p>

`;'''

code = code.replace(old_embed_2, new_embed_2)

# =============================================================================
# FIX 2: Detect if AI stacked placeholders and redistribute
# Add a check in processImagePlaceholders to detect clustering
# =============================================================================

# Find the processImagePlaceholders function and add clustering detection
old_process_start = '''async function processImagePlaceholders(contentHtml, titleSlug) {
  const placeholderRegex = /<!-- WPIMG alt="([^"]+)" -->/g;
  const matches = [...contentHtml.matchAll(placeholderRegex)];
  let featuredImageId = null;
  let processedHtml = contentHtml;
  const domain = config.baseUrl.replace(/https?:\\/\\//, '').replace(/\\/$/, '');'''

new_process_start = '''async function processImagePlaceholders(contentHtml, titleSlug) {
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
  }'''

code = code.replace(old_process_start, new_process_start)

# =============================================================================
# Update version
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.39",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.40"
)

old_changelog = """* v2.39 Changes:
 * - FIX: Simplified YouTube embed (Gutenberg JSON comments caused 500 errors)
 * - Now uses plain [embed] shortcode with simple wrapper div"""

new_changelog = """* v2.40 Changes:
 * - FIX: YouTube now uses plain URL (WordPress auto-embeds perfectly)
 * - FIX: Detects if AI stacked image placeholders and redistributes them by H2
 * 
 * v2.39 Changes:
 * - Simplified YouTube embed format"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.40-auto-distribute'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.40 updates applied:")
print("   - YouTube: Plain URL on own line (WordPress auto-embeds with full controls)")
print("   - Images: Detects stacked placeholders and redistributes by H2 sections")
print("   - Version: v2.40-auto-distribute")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "https://www.youtube.com/watch?v=${video.videoId}\n\n<p style" in code_verify:
    print("✅ Verified: Plain YouTube URL format")
else:
    print("❌ Warning: YouTube format may not have applied")

if "AI stacked placeholders" in code_verify:
    print("✅ Verified: Stacking detection present")
else:
    print("❌ Warning: Stacking detection may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
