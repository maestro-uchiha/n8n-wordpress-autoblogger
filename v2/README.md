# n8n Autoblogger System v2.0 (Clean Edition)

A "set & forget" multi-site WordPress autoblogging system built for n8n Cloud v2.3.5.

## 📁 System Components

| Workflow | Description |
|----------|-------------|
| `1_Master_Scheduler.json` | Orchestrator - runs every 10 min, checks due sites, triggers publishing |
| `2_Publisher.json` | Core engine - generates content, images, and publishes to WordPress |
| `3_Cleanup.json` | Maintenance - resets FAILED and stuck PROCESSING posts to QUEUED |

---

## 🚀 Quick Setup

### Step 1: n8n Variables

Create these variables in **Settings → Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `SITE_REGISTRY_SPREADSHEET_ID` | Google Sheets document ID | `1ABC123...` |
| `SITE_REGISTRY_GID` | Numeric gid of Site_Registry sheet | `0` |
| `PUBLISHER_WORKFLOW_ID` | ID of the Publisher workflow (after import) | `abc123` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | Text model (default: gpt-4o-mini) | `gpt-4o-mini` |
| `OPENAI_IMAGE_MODEL` | Image model (default: dall-e-3) | `dall-e-3` |
| `GOOGLE_CSE_API_KEY` | Google Custom Search API key | `AIza...` |
| `GOOGLE_CSE_CX` | Google Custom Search Engine ID | `abc123:xyz` |
| `SERPER_API_KEY` | (Optional) Serper.dev API key (fallback for CSE) | `...` |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `AIza...` |
| `FAL_API_KEY` | (Optional) fal.ai API key | `...` |
| `PEXELS_API_KEY` | (Optional) Pexels API key | `...` |
| `FASTINDEX_API_KEY` | (Optional) FastIndex.eu API key | `...` |
| `TELEGRAM_BOT_TOKEN` | (Optional) Telegram notifications | `123456:ABC...` |
| `TELEGRAM_CHAT_ID` | (Optional) Telegram chat ID | `-1001234567890` |
| `PROCESSING_STUCK_THRESHOLD_MINUTES` | (Optional) Cleanup threshold (default: 30) | `60` |

### Step 2: Google Sheets Structure

#### Site_Registry Sheet (gid: 0)

| Column | Description |
|--------|-------------|
| `site_id` | Unique identifier (e.g., `site_001`) |
| `site_name` | Human-readable name |
| `base_url` | WordPress URL (no trailing slash) |
| `auth_mode` | `jwt` or `basic` |
| `jwt_user` | JWT username (if auth_mode=jwt) |
| `jwt_password` | JWT password (if auth_mode=jwt) |
| `jwt_token` | (Optional) Existing JWT token |
| `wp_user` | WP username (if auth_mode=basic) |
| `wp_app_password` | WP Application Password (if auth_mode=basic) |
| `topics_gid` | **Numeric gid** of this site's topics sheet |
| `post_interval_minutes` | Minutes between posts (e.g., 120) |
| `last_posted_at` | ISO timestamp (auto-updated) |
| `enabled` | `TRUE` or `FALSE` |
| `post_status` | `publish` or `draft` |
| `tone` | Writing tone (e.g., "informative and engaging") |
| `min_words` | Minimum word count (e.g., 1500) |
| `max_words` | Maximum word count (e.g., 2500) |
| `faq_count` | Number of FAQs (e.g., 5) |
| `images_count` | Number of images (e.g., 2) |
| `internal_links_count` | Internal links to add (e.g., 3) |
| `external_links_count` | External links from Google CSE (e.g., 5) |
| `youtube_embeds_count` | YouTube videos to embed (e.g., 1) |
| `image_provider_priority` | Fallback order: `openai,fal,pexels` |

#### Topics Sheet (one per site)

| Column | Description |
|--------|-------------|
| `topic` | The blog topic/keyword |
| `status` | `QUEUED`, `PROCESSING`, `DONE`, or `FAILED` |
| `locked_at` | ISO timestamp when processing started |
| `post_url` | Published post URL (auto-filled) |
| `error` | Error message if failed |
| `tags` | Comma-separated tags |
| `categories` | Comma-separated categories |
| `created_at` | When topic was added |
| `updated_at` | Last update timestamp |

**Finding the gid**: Open your sheet, look at the URL:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=414510277
                                                             ^^^^^^^^^^
                                                             This is the gid
```

### Step 3: Import Workflows

1. Import all 3 JSON files into n8n
2. **Update Google Sheets credentials** in each workflow
3. Set `PUBLISHER_WORKFLOW_ID` to the Publisher workflow's ID
4. Activate the Master Scheduler and Cleanup workflows

### Step 4: WordPress Setup

#### Option A: JWT Authentication (Recommended)
1. Install "JWT Authentication for WP REST API" plugin
2. Add to `wp-config.php`:
   ```php
   define('JWT_AUTH_SECRET_KEY', 'your-strong-secret-key');
   define('JWT_AUTH_CORS_ENABLE', true);
   ```
3. Create a WordPress user with Editor/Admin role
4. Use that username/password in `jwt_user` and `jwt_password`

#### Option B: Basic Authentication
1. Go to **Users → Profile → Application Passwords**
2. Create a new application password
3. Use your WP username and the generated password

---

## 🔧 How It Works

### Flow Diagram

```
Master Scheduler (every 10 min)
    │
    ├─→ Read Site Registry
    │
    ├─→ Schedule Gate (filter due sites)
    │
    └─→ For Each Due Site:
            │
            ├─→ Read Topics Sheet
            ├─→ Pick first QUEUED topic
            ├─→ Lock it (status = PROCESSING)
            ├─→ Execute Publisher workflow
            │       │
            │       ├─→ Generate article (OpenAI)
            │       ├─→ Generate images (OpenAI/fal/Pexels)
            │       ├─→ Fetch external links (Google CSE)
            │       ├─→ Fetch YouTube videos
            │       ├─→ Fetch internal links
            │       ├─→ Enrich content (inject links/videos)
            │       └─→ Publish to WordPress
            │
            ├─→ On Success: Mark DONE, update last_posted_at
            └─→ On Failure: Mark FAILED with error

Cleanup (every hour)
    │
    ├─→ Find FAILED rows (reset for retry)
    ├─→ Find PROCESSING rows older than threshold
    └─→ Reset all to QUEUED, clear locked_at
```

---

## 🐛 Troubleshooting

### "Can not get sheet 'undefined'"
- Ensure `topics_gid` contains the **numeric gid** (e.g., `414510277`)
- Check that all Google Sheets nodes use `"mode": "id"` for sheet references

### "Sheet with ID X not found"
- Verify the gid exists in your spreadsheet
- Open the sheet and confirm the gid in the URL

### "JWT authentication failed"
- Verify the JWT plugin is installed and configured
- Check `wp-config.php` has the JWT secret key
- Test the endpoint: `POST /wp-json/jwt-auth/v1/token`

### "Missing topic" error
- Check the Topics sheet has a column named exactly `topic`
- Ensure at least one row has `status` = `QUEUED`

### Images not generating
- Check `OPENAI_API_KEY` is set
- Verify `image_provider_priority` contains valid providers
- Check the `image_errors` array in the output for details

### External links not inserting
- Verify `GOOGLE_CSE_API_KEY` and `GOOGLE_CSE_CX` are set, OR `SERPER_API_KEY` as fallback
- Check `external_links_count` is > 0
- Look at `enrichment.external_links_inserted` in output

---

## 📊 Monitoring

The Publisher returns detailed output:

```json
{
  "ok": true,
  "post_id": 12345,
  "post_url": "https://example.com/blog-post-title/",
  "title": "Blog Post Title",
  "slug": "blog-post-title",
  "status": "publish",
  "featured_image_id": 67890,
  "enrichment": {
    "external_links": 5,
    "external_links_inserted": 4,
    "youtube_videos": 1,
    "internal_links": 3
  },
  "image_errors": []
}
```

---

## 📝 Adding New Sites

1. Add a new row to Site_Registry with all required fields
2. Create a new Topics sheet tab
3. Get its gid from the URL
4. Put the gid in the `topics_gid` column
5. Add topics with `status` = `QUEUED`

---

## ⚡ Performance Tips

1. **Post Interval**: Set `post_interval_minutes` to at least 60 to avoid rate limits
2. **Image Providers**: Use the fallback chain `openai,fal,pexels` for reliability
3. **Word Count**: 1500-2500 words is optimal for SEO without timeouts
4. **Parallel Sites**: The system processes one site at a time to prevent conflicts

---

## 🔄 Version History

- **v2.47**: Serper.dev fallback for Google CSE, FastIndex integration, distributed external links (no clustering), Cleanup resets FAILED+PROCESSING
- **v2.0**: Clean rebuild with hardened input parsing, improved link injection, proper YouTube embeds
