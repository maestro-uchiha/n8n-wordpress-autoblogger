# Technical Reference

Architecture, internals, and advanced customization for the n8n WordPress Autoblogger.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Workflow Components](#workflow-components)
3. [WordPress Plugin API](#wordpress-plugin-api)
4. [Content Generation Pipeline](#content-generation-pipeline)
5. [Link Injection Algorithm](#link-injection-algorithm)
6. [Image Processing Flow](#image-processing-flow)
7. [Authentication Flow](#authentication-flow)
8. [Extending the System](#extending-the-system)
9. [Version History](#version-history)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        n8n Instance                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────────────────────┐  │
│  │ Master Scheduler │───▶│     Publisher Engine (Code)       │  │
│  │   (Cron/Manual)  │    │                                   │  │
│  └──────────────────┘    │  ┌─────────┐  ┌───────────────┐  │  │
│           │              │  │ Content │  │    Image      │  │  │
│           │              │  │   Gen   │──│  Processing   │  │  │
│           ▼              │  └────┬────┘  └───────┬───────┘  │  │
│  ┌──────────────────┐    │       │               │          │  │
│  │  Google Sheets   │    │  ┌────▼───────────────▼────┐     │  │
│  │   (Sites/Topics) │    │  │    Link & SEO Injection │     │  │
│  └──────────────────┘    │  └────────────┬───────────┘     │  │
│                          │               │                  │  │
│                          │  ┌────────────▼───────────┐     │  │
│                          │  │   WordPress Publisher   │     │  │
│                          │  └────────────────────────┘     │  │
│                          └──────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │   OpenAI    │          │  WordPress  │          │   External  │
    │  GPT / DALL │          │  REST API   │          │    APIs     │
    │             │          │  + Plugin   │          │ (YT, SERP)  │
    └─────────────┘          └─────────────┘          └─────────────┘
```

---

## Workflow Components

### 1. Master Scheduler (`1_Master_Scheduler.json`)

**Purpose**: Orchestrates multi-site publishing

**Flow**:
1. Triggered by cron or manual execution
2. Fetches enabled sites from Google Sheets
3. For each site, checks posting interval
4. Fetches pending topics from site's topic sheet
5. Locks topic (sets PROCESSING status)
6. Calls Publisher workflow
7. Updates topic status (DONE/ERROR)

**Key Nodes**:
- `Schedule Trigger` - Cron configuration
- `Fetch Sites` - Google Sheets read
- `Process Sites Loop` - Iteration logic
- `Lock Topic` - Prevents duplicate processing
- `Call Publisher` - Execute Workflow node

### 2. Publisher Engine (`2_Publisher.json`)

**Purpose**: Generates and publishes a single post

**Execution Steps**:
1. `WP_AUTH_CHECK` - Validate WordPress credentials
2. `FETCH_HINTS` - Get SERP results and YouTube videos
3. `GENERATE_CONTENT` - Call OpenAI for article
4. `PROCESS_IMAGES` - Generate and upload images
5. `INTERNAL_LINKS` - Inject links to existing posts
6. `EXTERNAL_LINKS` - Inject SERP-based external links
7. `YOUTUBE_EMBEDS` - Insert video embeds
8. `TERMS` - Create/assign tags and categories
9. `PUBLISH_POST` - Create WordPress post
10. `POST_PROCESSING` - SEO meta, notifications

**Single Code Node Architecture**:
All logic is in one large Code node for:
- Easier debugging
- No credential passing between nodes
- Atomic execution
- Simpler error handling

### 3. Cleanup Workflow (`3_Cleanup.json`)

**Purpose**: Reset stuck PROCESSING topics

**When to Use**:
- After workflow crashes
- When topics are stuck
- Manual recovery needed

---

## WordPress Plugin API

### Plugin: n8n Autoblogger Helper v1.2

**File**: `n8n-image-upload.php`

### Endpoints

#### POST `/wp-json/n8n/v1/upload-image`

Upload base64-encoded image.

**Request**:
```json
{
  "base64": "iVBORw0KGgo...",
  "filename": "my-image.png",
  "mime_type": "image/png",
  "alt_text": "Description",
  "title": "Image Title"
}
```

**Response**:
```json
{
  "success": true,
  "id": 123,
  "url": "https://site.com/wp-content/uploads/2024/01/my-image.png",
  "source_url": "https://site.com/wp-content/uploads/2024/01/my-image.png",
  "filename": "my-image.png",
  "size": 45678
}
```

#### POST `/wp-json/n8n/v1/sideload-image`

Download image from URL and add to media library.

**Request**:
```json
{
  "url": "https://external.com/image.jpg",
  "filename": "my-image.jpg",
  "alt_text": "Description",
  "title": "Image Title"
}
```

**Response**: Same as upload-image

#### POST `/wp-json/n8n/v1/update-seo-meta`

Update Yoast SEO or RankMath meta fields.

**Request**:
```json
{
  "post_id": 123,
  "focus_keyphrase": "main keyword",
  "meta_description": "SEO description",
  "seo_title": "Custom SEO Title"
}
```

**Response**:
```json
{
  "success": true,
  "post_id": 123,
  "seo_plugins": {
    "yoast": false,
    "rankmath": true
  },
  "updated": {
    "rankmath_focus_keyword": true,
    "rankmath_description": true,
    "rankmath_title": true
  }
}
```

#### POST `/wp-json/n8n/v1/create-category`

Create a category (bypasses REST API permission issues).

**Request**:
```json
{
  "name": "Category Name",
  "slug": "category-slug",
  "parent": 0
}
```

**Response**:
```json
{
  "success": true,
  "id": 42,
  "name": "Category Name",
  "slug": "category-slug",
  "created": true
}
```

### Permission Requirements

All endpoints require `edit_posts` capability (Editor role or higher).

---

## Content Generation Pipeline

### OpenAI Prompt Structure

**System Prompt** defines:
- Output JSON schema
- HTML formatting rules
- Image placeholder format
- Link phrase requirements
- Table requirements
- FAQ generation

**User Prompt** provides:
- Topic
- Word count targets
- Tone
- Required elements count

### JSON Schema Output

```json
{
  "title": "SEO-optimized title",
  "slug": "url-friendly-slug",
  "meta_description": "150-160 char description",
  "focus_keyphrase": "main SEO keyword",
  "tag_suggestions": ["tag1", "tag2"],
  "content_html": "<p>Full HTML article...</p>",
  "internal_anchor_phrases": ["phrase for internal links"],
  "external_anchor_phrases": ["phrase for external links"],
  "youtube_anchor_phrases": ["phrase near video spots"],
  "faq_items": [
    {"question": "FAQ?", "answer": "Answer"}
  ]
}
```

### Post-Processing

After AI generation:
1. Strip any `<a>` tags (AI sometimes ignores instructions)
2. Remove `href` attributes
3. Remove placeholder URLs
4. Validate required fields

---

## Link Injection Algorithm

### v2.28+ Safe Link Placement

Links are ONLY inserted in:
- `<p>` paragraphs
- `<li>` list items  
- `<td>` table cells

NEVER in:
- `<h1>` - `<h6>` headings
- `<figcaption>`
- Other elements

### Algorithm

```javascript
function isInsideHeading(content, phrase) {
  // Check if phrase appears in h1-h6
  const headingRegex = new RegExp(
    `<h[1-6][^>]*>[^<]*${escapedPhrase}[^<]*</h[1-6]>`, 'i'
  );
  return headingRegex.test(content);
}

// Only match in safe containers
const safeRegex = new RegExp(
  `(<(?:p|li|td)[^>]*>[^<]*?)(\\b${phrase}\\b)([^<]*?</(?:p|li|td)>)`,
  'i'
);
```

### Internal Link Matching

1. Get anchor phrases from AI
2. For each phrase:
   - Skip if in heading
   - Skip if already linked
   - Search WordPress for related posts
   - Insert link to best match

### External Link Matching

1. Fetch SERP results for topic
2. For each phrase:
   - Try exact match first
   - Fall back to finding SERP title words in content
   - Insert link with `target="_blank" rel="noopener"`

---

## Image Processing Flow

```
┌─────────────────┐
│ Parse Placeholder│
│ <!-- WPIMG --> │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Try Provider 1  │────▶│ Try Provider 2  │────▶ ...
│   (e.g., fal)   │fail │  (e.g., openai) │fail
└────────┬────────┘     └────────┬────────┘
         │success                │success
         ▼                       ▼
┌─────────────────────────────────────────┐
│           Upload to WordPress            │
├─────────────────────────────────────────┤
│ Base64 ──▶ /n8n/v1/upload-image         │
│ URL    ──▶ /n8n/v1/sideload-image       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│    Replace placeholder with <figure>     │
│    Set first image as featured_media     │
└─────────────────────────────────────────┘
```

### Provider-Specific Handling

| Provider | Output | Upload Method |
|----------|--------|---------------|
| OpenAI | base64 | upload-image |
| fal.ai | URL | sideload-image |
| Pexels | URL | sideload-image |

---

## Authentication Flow

### JWT Flow

```
┌──────────┐     ┌───────────┐     ┌────────────┐
│ n8n      │────▶│ Validate  │────▶│ Use cached │
│ Publisher│     │ cached    │yes  │ token      │
└──────────┘     │ token?    │     └────────────┘
                 └─────┬─────┘
                       │no/invalid
                       ▼
                 ┌───────────┐     ┌────────────┐
                 │ Fetch new │────▶│ Cache and  │
                 │ JWT token │     │ use token  │
                 └───────────┘     └────────────┘
```

### Token Validation

```javascript
POST /wp-json/jwt-auth/v1/token/validate
Authorization: Bearer <token>

// Valid response
{ "code": "jwt_auth_valid_token", "data": { "status": 200 } }
```

---

## Extending the System

### Adding a New Image Provider

1. Create generator function:
```javascript
async function generateImageNewProvider(prompt) {
  const resp = await httpRequest.call(this, {
    method: 'POST',
    url: 'https://api.newprovider.com/generate',
    headers: { 'Authorization': `Bearer ${config.newProviderKey}` },
    body: { prompt }
  });
  // Return { base64: '...' } or { url: '...' }
  return { url: resp.image_url };
}
```

2. Add to provider chain in `generateImage()`:
```javascript
if (provider === 'newprovider' && config.newProviderKey) {
  img = await generateImageNewProvider.call(this, prompt);
}
```

3. Add config variable and sheet column

### Adding a New Notification Channel

1. Create sender function:
```javascript
async function sendSlackNotification(message) {
  if (!config.slackEnabled) return false;
  // ... implementation
}
```

2. Call in POST_PROCESSING step

3. Add config options

### Custom Post Types

Modify the `publishPost()` function:

```javascript
const postData = {
  // Change endpoint for custom post type
  // POST /wp-json/wp/v2/custom_posts
};
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.31 | Jan 2026 | Auto-category creation via plugin endpoint |
| v2.30 | Jan 2026 | SEO meta via plugin (Yoast/RankMath) |
| v2.29 | Jan 2026 | Removed JSON-LD (WP blocks scripts) |
| v2.28 | Jan 2026 | Links only in paragraphs (not headings) |
| v2.27 | Jan 2026 | Custom plugin for image uploads |
| v2.23 | Jan 2026 | DALL-E 2 size fix (512x512) |
| v2.13 | Dec 2025 | External URL image fallback |
| v2.12 | Dec 2025 | Improved anchor phrase matching |
| v2.8 | Dec 2025 | Per-site notification controls |

### Plugin Versions

| Version | Changes |
|---------|---------|
| 1.2 | Added `/create-category` endpoint |
| 1.1 | Added `/update-seo-meta` endpoint |
| 1.0 | Initial: image upload and sideload |
