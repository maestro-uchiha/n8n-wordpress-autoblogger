#!/usr/bin/env python3
"""
Fix v2.48: Images generated even when AI doesn't include placeholders
"""

import json
import re

# Read the Publisher JSON
with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find the Code node with the Publisher Engine
for node in data['nodes']:
    if node.get('name') == 'Publisher Engine (Code)':
        code = node['parameters']['jsCode']
        
        # Fix 1: Change version header
        code = code.replace(
            '* AUTOBLOGGER PUBLISHER ENGINE v2.47',
            '* AUTOBLOGGER PUBLISHER ENGINE v2.48'
        )
        
        # Fix 2: Add v2.48 changelog
        code = code.replace(
            ' * v2.47 Changes:\n * - External links now distributed across content (prevents clustering)',
            ' * v2.48 Changes:\n * - FIX: Images now generated even when AI omits placeholders\n * - Uses section headings for alt text when AI placeholders missing\n * \n * v2.47 Changes:\n * - External links now distributed across content (prevents clustering)'
        )
        
        # Fix 3: The critical bug fix - change imagesToPlace logic
        # Old code: const imagesToPlace = Math.min(originalMatches.length, config.imagesCount);
        # New code: const imagesToPlace = config.imagesCount;  // v2.48: Always use requested count
        code = code.replace(
            '// Distribute images across usable sections\n  const imagesToPlace = Math.min(originalMatches.length, config.imagesCount);',
            '// v2.48: Always generate requested number of images (even if AI omitted placeholders)\n  const imagesToPlace = config.imagesCount;'
        )
        
        # Fix 4: Update alt text fallback to use section title
        # Old: alt: originalMatches[i] ? originalMatches[i][1] : `Image ${i + 1} for ${titleSlug}`
        # New: Use section heading for better alt text
        code = code.replace(
            "alt: originalMatches[i] ? originalMatches[i][1] : `Image ${i + 1} for ${titleSlug}`",
            "alt: originalMatches[i] ? originalMatches[i][1] : `${h2Match[1].trim()} - ${config.topic}`"
        )
        
        node['parameters']['jsCode'] = code
        break

# Update version ID
data['versionId'] = 'v2.48-image-fallback'

# Write back
with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Fixed! Publisher updated to v2.48")
print("- Images will now generate even when AI doesn't include placeholders")
print("- Alt text uses section headings + topic for better SEO")
