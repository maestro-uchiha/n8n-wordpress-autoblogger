#!/usr/bin/env python3
"""
Fix v2.38: Use WordPress [embed] shortcode for YouTube (iframes get stripped by wp_kses)
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
# FIX: YouTube embed format - use [embed] shortcode instead of iframe
# WordPress strips iframes via wp_kses when posting via REST API
# The [embed] shortcode is always processed by WordPress oEmbed
# =============================================================================

# First embed block (in AI placeholder replacement) - currently has iframe
old_embed_1 = '''const embedBlock = `<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/${video.videoId}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div><figcaption>${video.title}</figcaption></figure>`;'''

# New format using [embed] shortcode - guaranteed to work
new_embed_1 = '''const embedBlock = `
<!-- wp:embed {"url":"https://www.youtube.com/watch?v=${video.videoId}","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div><figcaption>${video.title}</figcaption></figure>
<!-- /wp:embed -->`;'''

code = code.replace(old_embed_1, new_embed_1)

# Second embed block (in H2 fallback) - currently has iframe
old_embed_2 = '''const embedBlock = `

<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/${video.videoId}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div><figcaption>${video.title}</figcaption></figure>

`;'''

new_embed_2 = '''const embedBlock = `

<!-- wp:embed {"url":"https://www.youtube.com/watch?v=${video.videoId}","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div><figcaption>${video.title}</figcaption></figure>
<!-- /wp:embed -->

`;'''

code = code.replace(old_embed_2, new_embed_2)

# =============================================================================
# Update version comment
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.37",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.38"
)

# Add v2.38 changelog
old_changelog = """* v2.37 Changes:
 * - FIX: Empty string handling for internal_links_count/external_links_count (was causing NaN)
 * - YouTube: Use iframe embed instead of oEmbed URL (more reliable rendering)"""

new_changelog = """* v2.38 Changes:
 * - FIX: YouTube embeds now use [embed] shortcode (iframes stripped by wp_kses)
 * - Uses Gutenberg block comments for proper block recognition
 * 
 * v2.37 Changes:
 * - FIX: Empty string handling for internal_links_count/external_links_count (was causing NaN)"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.38-embed-shortcode'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.38 updates applied:")
print("   - Changed YouTube from iframe to [embed] shortcode")
print("   - Added Gutenberg block comments for proper parsing")
print("   - Version: v2.38-embed-shortcode")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "[embed]https://www.youtube.com/watch" in code_verify:
    print("✅ Verified: [embed] shortcode format present")
else:
    print("❌ Warning: [embed] shortcode may not have applied")
    
if "<!-- wp:embed" in code_verify:
    print("✅ Verified: Gutenberg block comments present")
else:
    print("❌ Warning: Gutenberg comments may not have applied")

print(f"\n📄 Version: {verify['versionId']}")
