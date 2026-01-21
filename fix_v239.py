#!/usr/bin/env python3
"""
Fix v2.39: Simplify YouTube embed to just [embed] shortcode
The Gutenberg block JSON comments were causing 500 errors
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
# FIX: Simplify YouTube embed - just [embed] shortcode, no Gutenberg wrapper
# The JSON in Gutenberg comments was causing 500 errors
# =============================================================================

# First embed block (in AI placeholder replacement)
old_embed_1 = '''const embedBlock = `
<!-- wp:embed {"url":"https://www.youtube.com/watch?v=${video.videoId}","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div><figcaption>${video.title}</figcaption></figure>
<!-- /wp:embed -->`;'''

# Simple format - just the shortcode with a wrapper div
new_embed_1 = '''const embedBlock = `<div class="youtube-embed-wrapper" style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;margin:20px 0;">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div>
<p class="youtube-caption"><em>${video.title}</em></p>`;'''

code = code.replace(old_embed_1, new_embed_1)

# Second embed block (in H2 fallback)
old_embed_2 = '''const embedBlock = `

<!-- wp:embed {"url":"https://www.youtube.com/watch?v=${video.videoId}","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div><figcaption>${video.title}</figcaption></figure>
<!-- /wp:embed -->

`;'''

new_embed_2 = '''const embedBlock = `

<div class="youtube-embed-wrapper" style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;margin:20px 0;">
[embed]https://www.youtube.com/watch?v=${video.videoId}[/embed]
</div>
<p class="youtube-caption"><em>${video.title}</em></p>

`;'''

code = code.replace(old_embed_2, new_embed_2)

# =============================================================================
# Update version comment
# =============================================================================
code = code.replace(
    "* AUTOBLOGGER PUBLISHER ENGINE v2.38",
    "* AUTOBLOGGER PUBLISHER ENGINE v2.39"
)

# Add v2.39 changelog
old_changelog = """* v2.38 Changes:
 * - FIX: YouTube embeds now use [embed] shortcode (iframes stripped by wp_kses)
 * - Uses Gutenberg block comments for proper block recognition"""

new_changelog = """* v2.39 Changes:
 * - FIX: Simplified YouTube embed (Gutenberg JSON comments caused 500 errors)
 * - Now uses plain [embed] shortcode with simple wrapper div
 * 
 * v2.38 Changes:
 * - YouTube embeds use [embed] shortcode (iframes stripped by wp_kses)"""

code = code.replace(old_changelog, new_changelog)

# Update the node
engine_node['parameters']['jsCode'] = code

# Update versionId
workflow['versionId'] = 'v2.39-simple-embed'

# Save
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2)

print("✅ v2.39 updates applied:")
print("   - Simplified YouTube embed (removed Gutenberg JSON comments)")
print("   - Now uses plain [embed] shortcode with wrapper div")
print("   - Version: v2.39-simple-embed")

# Verify
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    verify = json.load(f)
    
code_verify = verify['nodes'][2]['parameters']['jsCode']

if "[embed]https://www.youtube.com/watch" in code_verify:
    print("✅ Verified: [embed] shortcode present")
else:
    print("❌ Warning: [embed] shortcode missing")
    
if "<!-- wp:embed" in code_verify:
    print("❌ Warning: Gutenberg comments still present (should be removed)")
else:
    print("✅ Verified: Gutenberg comments removed")

if "youtube-embed-wrapper" in code_verify:
    print("✅ Verified: Simple wrapper div present")
else:
    print("❌ Warning: Wrapper div missing")

print(f"\n📄 Version: {verify['versionId']}")
