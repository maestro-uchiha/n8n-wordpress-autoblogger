#!/usr/bin/env python3
"""
Fix v2.37 updates:
1. Fix NaN bug for internal_links_count and external_links_count empty strings
2. Change YouTube embed format to use iframe (more reliable than oEmbed URL)
"""
import json
import re

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
# FIX 1: NaN bug for internal_links_count and external_links_count
# =============================================================================
# OLD: return site.internal_links_count !== undefined ? parseInt(site.internal_links_count) : 3;
# NEW: return site.internal_links_count !== undefined && site.internal_links_count !== '' ? parseInt(site.internal_links_count) : 3;

code = code.replace(
    "return site.internal_links_count !== undefined ? parseInt(site.internal_links_count) : 3;",
    "return site.internal_links_count !== undefined && site.internal_links_count !== '' ? parseInt(site.internal_links_count) : 3;"
)

code = code.replace(
    "return site.external_links_count !== undefined ? parseInt(site.external_links_count) : 5;",
    "return site.external_links_count !== undefined && site.external_links_count !== '' ? parseInt(site.external_links_count) : 5;"
)

# =============================================================================
# FIX 2: YouTube embed format - use iframe instead of oEmbed URL
# =============================================================================
# The oEmbed URL format requires WordPress to auto-embed, which doesn't always work
# Use direct iframe which is more reliable

# First embed block (in AI placeholder replacement)
old_embed_1 = '''const embedBlock = `<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=${video.videoId}
</div><figcaption>${video.title}</figcaption></figure>`;'''

new_embed_1 = '''const embedBlock = `<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/${video.videoId}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div><figcaption>${video.title}</figcaption></figure>`;'''

code = code.replace(old_embed_1, new_embed_1)

# Second embed block (in H2 fallback)
old_embed_2 = '''const embedBlock = `

<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=${video.videoId}
</div><figcaption>${video.title}</figcaption></figure>

`;'''

new_embed_2 = '''const embedBlock = `

<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/${video.videoId}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div><figcaption>${video.title}</figcaption></figure>

`;'''

code = code.replace(old_embed_2, new_embed_2)

# =============================================================================
# Update version comment
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.30",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.37"
)

# Add v2.37 changelog
old_changelog = """* v2.30 Changes:
 * - SEO: New plugin endpoint /n8n/v1/update-seo-meta for direct meta updates
 * - SEO: Shows which SEO plugins are detected (Yoast/RankMath)
 * - SEO: Uses update_post_meta() directly (bypasses REST API schema restrictions)"""

new_changelog = """* v2.37 Changes:
 * - FIX: Empty string handling for internal_links_count/external_links_count (was causing NaN)
 * - YouTube: Use iframe embed instead of oEmbed URL (more reliable rendering)
 * 
 * v2.36 Changes:
 * - YouTube/Images placed by AI using placeholder comments
 * 
 * v2.30 Changes:
 * - SEO: New plugin endpoint /n8n/v1/update-seo-meta for direct meta updates
 * - SEO: Shows which SEO plugins are detected (Yoast/RankMath)
 * - SEO: Uses update_post_meta() directly (bypasses REST API schema restrictions)"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.37-iframe-youtube'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.37 updates applied:")
print("   - Fixed NaN bug for internal_links_count empty string")
print("   - Fixed NaN bug for external_links_count empty string")
print("   - Changed YouTube embed to use iframe (more reliable)")
print("   - Updated version to v2.37-iframe-youtube")

# Verify the changes
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

# Check fixes applied
if "internal_links_count !== '' ?" in code_verify:
    print("✅ Verified: internal_links_count empty check present")
else:
    print("❌ Warning: internal_links_count fix may not have applied")

if "external_links_count !== '' ?" in code_verify:
    print("✅ Verified: external_links_count empty check present")
else:
    print("❌ Warning: external_links_count fix may not have applied")

if "youtube.com/embed/${video.videoId}" in code_verify:
    print("✅ Verified: iframe embed format present")
else:
    print("❌ Warning: iframe embed fix may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
