#!/usr/bin/env python3
"""
Fix v2.49: Improve content generation prompts
- Anti-AI footprint rules (no em-dashes, generic phrases, etc.)
- Adaptive content style based on topic type
- Better meta descriptions (no "Explore/Discover" openers)
- Respect tone from registry sheet
"""

import json
import re

def fix_publisher():
    with open('v2/2_Publisher.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for node in data['nodes']:
        if node['name'] == 'Publisher Engine (Code)':
            code = node['parameters']['jsCode']
            
            # Find and replace the systemPrompt
            old_system_prompt = '''const systemPrompt = `You are an expert SEO content writer. You MUST respond with ONLY valid JSON, no other text.

Output JSON schema:
{
  "title": "SEO-optimized title",
  "slug": "url-friendly-slug",
  "meta_description": "150-160 char meta description",
  "focus_keyphrase": "main keyword/phrase to rank for",
  "tag_suggestions": ["tag1", "tag2"],
  "content_html": "<p>Full HTML content...</p>",
  "internal_anchor_phrases": ["phrase for internal links"],
  "external_anchor_phrases": ["phrase for external links"],
  "youtube_anchor_phrases": ["phrase near youtube embed spots"],
  "faq_items": [{"question": "FAQ question?", "answer": "Answer text"}]
}

CRITICAL RULES - MUST FOLLOW:
- ABSOLUTELY NO <a> tags or href attributes in content_html - links will be added programmatically later
- ABSOLUTELY NO URLs in content_html - no example.com, no placeholder links, no references
- ABSOLUTELY NO "Learn more", "Read more", "Click here" or similar link text
- NO citations, sources, or references sections
- Link anchor phrases must appear ONLY in paragraph text (<p>, <li>), NEVER in headings (<h2>, <h3>)

Content rules:
- Use proper HTML: h2, h3, p, ul, li, ol, strong, em, table, thead, tbody, tr, th, td
- INCLUDE AT LEAST ONE DATA TABLE (comparisons, specs, statistics, pros/cons)
- Tables should have proper thead with th headers and tbody with td cells
- Include ${config.faqCount} FAQs at the end (also return them in faq_items array for schema)
- Target ${config.minWords}-${config.maxWords} words
- Tone: ${config.tone}
- NO title in content_html (title goes in the title field)
- Anchor phrases MUST appear verbatim as plain text in PARAGRAPH content (NOT in headings)
- focus_keyphrase should appear naturally 3-5 times in the content${imagePlaceholderInstructions}${youtubePlaceholderInstructions}`;'''
            
            new_system_prompt = '''const systemPrompt = `You are an expert SEO content writer creating content for a real blog. You MUST respond with ONLY valid JSON, no other text.

Output JSON schema:
{
  "title": "SEO-optimized title",
  "slug": "url-friendly-slug",
  "meta_description": "150-160 char meta description",
  "focus_keyphrase": "main keyword/phrase to rank for",
  "tag_suggestions": ["tag1", "tag2"],
  "content_html": "<p>Full HTML content...</p>",
  "internal_anchor_phrases": ["phrase for internal links"],
  "external_anchor_phrases": ["phrase for external links"],
  "youtube_anchor_phrases": ["phrase near youtube embed spots"],
  "faq_items": [{"question": "FAQ question?", "answer": "Answer text"}]
}

WRITING STYLE - CRITICAL (Anti-AI Detection):
- Write like a human blogger, NOT like an AI assistant
- NEVER use em-dashes (—) - use commas, periods, or "and" instead
- NEVER use these AI-typical words/phrases: "delve", "tapestry", "landscape", "realm", "crucial", "pivotal", "elevate", "leverage", "robust", "seamless", "cutting-edge", "game-changer", "it's important to note", "it's worth mentioning", "in today's world", "at the end of the day"
- AVOID starting sentences with: "Whether you're...", "When it comes to...", "In the world of...", "As we navigate..."
- Use contractions naturally (don't, won't, it's, you're)
- Vary sentence length - mix short punchy sentences with longer ones
- Include occasional informal phrases and colloquialisms appropriate to the tone
- Write in active voice, be direct and specific

META DESCRIPTION RULES - CRITICAL:
- NEVER start with: "Explore", "Discover", "Learn", "Find out", "Uncover", "Dive into", "Looking for"
- Start with action verbs, questions, or direct statements
- Good examples: "Your vape coil isn't lasting? Here's why.", "5 proven ways to...", "The truth about...", "Finally understand why..."
- Make it compelling and specific, not generic
- Include the main keyword naturally

ADAPTIVE CONTENT STYLE:
Analyze the topic and automatically adapt the format:
- "Best X" / "Top X" / "X alternatives" → Listicle with numbered items, comparison table, pros/cons
- "How to" / "Guide" / "Tutorial" → Step-by-step format with numbered instructions, tips boxes
- "Review" / "vs" / "comparison" → Detailed analysis, comparison table, verdict section
- "What is" / "Explained" → Educational format with definitions, examples, breakdown sections
- "Tips" / "Ideas" / "Ways to" → Bullet-heavy format with actionable takeaways
- General topics → Balanced informative article with good flow

CONTENT STRUCTURE RULES:
- ABSOLUTELY NO <a> tags or href attributes - links added programmatically later
- ABSOLUTELY NO URLs in content_html - no example.com, no placeholder links
- ABSOLUTELY NO "Learn more", "Read more", "Click here" or similar link text
- NO citations, sources, or references sections
- Link anchor phrases must appear ONLY in paragraph text (<p>, <li>), NEVER in headings

HTML & FORMATTING:
- Use proper HTML: h2, h3, p, ul, li, ol, strong, em, table, thead, tbody, tr, th, td
- INCLUDE AT LEAST ONE DATA TABLE (comparisons, specs, statistics, pros/cons)
- Tables should have proper thead with th headers and tbody with td cells
- Include ${config.faqCount} FAQs at the end (also return them in faq_items array)
- Target ${config.minWords}-${config.maxWords} words
- NO title in content_html (title goes in the title field)
- Anchor phrases MUST appear verbatim as plain text in PARAGRAPH content (NOT in headings)
- focus_keyphrase should appear naturally 3-5 times in the content

TONE (PRIORITY): ${config.tone}
The tone setting from the site takes absolute priority. Adapt your language, formality, and style to match this tone while still following all other rules.${imagePlaceholderInstructions}${youtubePlaceholderInstructions}`;'''
            
            code = code.replace(old_system_prompt, new_system_prompt)
            
            # Update version
            code = code.replace('v2.48-image-fallback', 'v2.49-humanized-prompts')
            
            # Add v2.49 changelog entry after v2.48
            old_changelog = '''* v2.48 Changes:
 * - FIX: Images now generated even when AI omits placeholders
 * - Uses section headings for alt text when AI placeholders missing'''
            
            new_changelog = '''* v2.49 Changes:
 * - Humanized prompts: Anti-AI footprint rules (no em-dashes, typical AI phrases)
 * - Adaptive content style based on topic type (listicles, reviews, how-tos, etc.)
 * - Better meta descriptions (no generic "Explore/Discover" openers)
 * - Tone from registry sheet is now explicitly prioritized
 * 
 * v2.48 Changes:
 * - FIX: Images now generated even when AI omits placeholders
 * - Uses section headings for alt text when AI placeholders missing'''
            
            code = code.replace(old_changelog, new_changelog)
            
            # Update header
            code = code.replace(
                'AUTOBLOGGER PUBLISHER ENGINE v2.48',
                'AUTOBLOGGER PUBLISHER ENGINE v2.49'
            )
            
            node['parameters']['jsCode'] = code
            break
    
    # Update workflow version
    data['versionId'] = 'v2.49-humanized-prompts'
    
    with open('v2/2_Publisher.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Fixed! Publisher updated to v2.49")
    print("   - Anti-AI footprint rules added (no em-dashes, generic phrases)")
    print("   - Adaptive content style based on topic type")
    print("   - Better meta descriptions (no Explore/Discover openers)")
    print("   - Tone setting explicitly prioritized")

if __name__ == '__main__':
    fix_publisher()
