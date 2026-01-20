# n8n WordPress Autoblogger
## Complete User Guide v2.31

---

**Version:** 2.31  
**Last Updated:** January 2026  
**License:** MIT

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [System Requirements](#2-system-requirements)
3. [Quick Start Guide](#3-quick-start-guide)
4. [Detailed Setup](#4-detailed-setup)
5. [Configuration Reference](#5-configuration-reference)
6. [Using the System](#6-using-the-system)
7. [Troubleshooting](#7-troubleshooting)
8. [FAQ](#8-faq)
9. [Technical Reference](#9-technical-reference)

---

# 1. Introduction

## What is n8n WordPress Autoblogger?

The n8n WordPress Autoblogger is an automated content publishing system that:

- **Generates AI-powered blog articles** using OpenAI GPT-4
- **Creates and uploads images** using DALL-E, fal.ai, or Pexels
- **Automatically adds internal and external links** for SEO
- **Embeds relevant YouTube videos** for engagement
- **Manages SEO metadata** for Yoast SEO and RankMath
- **Supports multiple WordPress sites** from a single dashboard
- **Sends notifications** via Telegram, Email, and SpeedyIndex

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Google Sheets  │────▶│  n8n Workflows   │────▶│    WordPress    │
│  (Sites/Topics) │     │  (Orchestration) │     │  (Publishing)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

1. You add topics to a Google Sheet
2. n8n checks the sheet on a schedule
3. For each pending topic, AI generates a full article
4. Images are created and uploaded
5. Links and videos are automatically added
6. Post is published to WordPress
7. SEO metadata is configured
8. You get notified of success/failure

---

# 2. System Requirements

## Required

| Component | Requirement |
|-----------|-------------|
| **n8n** | Cloud (cloud.n8n.io) or self-hosted v1.0+ |
| **WordPress** | Version 5.0 or higher |
| **PHP** | Version 7.4 or higher (for plugin) |
| **OpenAI Account** | With API access and credits |
| **Google Account** | For Google Sheets |

## Optional (Recommended)

| Component | Purpose |
|-----------|---------|
| Google Custom Search API | External link sources |
| YouTube Data API | Video embeds |
| fal.ai Account | Fast AI image generation |
| Pexels API | Free stock photos |
| Telegram Bot | Real-time notifications |

---

# 3. Quick Start Guide

## 5-Minute Setup

### Step 1: Import Workflows

1. Log into n8n
2. Import these files from the `Current/` folder:
   - `Master Scheduler (Multi-site).json`
   - `Publisher (Autoblogging Engine).json`
   - `Cleanup (Stuck Locks).json`

### Step 2: Install WordPress Plugin

1. Download `wordpress-plugin/n8n-autoblogger-helper.zip`
2. WordPress Admin → Plugins → Add New → Upload Plugin
3. Install and Activate

### Step 3: Set Up Google Sheets

Create a spreadsheet with two sheets:

**Sites Sheet** (minimum columns):
| site_id | base_url | auth_mode | jwt_user | jwt_password | topics_spreadsheet_id | topics_gid | enabled |
|---------|----------|-----------|----------|--------------|----------------------|------------|---------|
| site_001 | https://yoursite.com | jwt | admin | password | SPREADSHEET_ID | GID | TRUE |

**Topics Sheet** (minimum columns):
| topic | status |
|-------|--------|
| Your Blog Topic Here | PENDING |

### Step 4: Add n8n Variables

Go to Settings → Variables and add:
- `OPENAI_API_KEY`: Your OpenAI API key

### Step 5: Test

1. Open the Master Scheduler workflow
2. Click "Test workflow"
3. Check WordPress for your new post!

---

# 4. Detailed Setup

## 4.1 Google Sheets Configuration

### Creating the Sites Sheet

Create a new Google Spreadsheet and add these columns:

#### Core Settings
| Column | Example | Description |
|--------|---------|-------------|
| site_id | site_001 | Unique identifier |
| site_name | My Blog | Display name |
| base_url | https://myblog.com | WordPress URL (no trailing /) |
| enabled | TRUE | Process this site? |

#### Authentication
| Column | Example | Description |
|--------|---------|-------------|
| auth_mode | jwt | "jwt" or "basic" |
| jwt_user | admin | WordPress username |
| jwt_password | pass123 | WordPress password |
| wp_user | admin | For basic auth |
| wp_app_password | xxxx xxxx | Application password |

#### Topics Configuration
| Column | Example | Description |
|--------|---------|-------------|
| topics_spreadsheet_id | 1ABC... | Google Sheets ID |
| topics_gid | 123456 | Sheet tab GID |
| post_interval_minutes | 60 | Min. minutes between posts |

#### Content Settings
| Column | Default | Description |
|--------|---------|-------------|
| post_status | draft | "draft" or "publish" |
| tone | informative | Writing style |
| min_words | 1500 | Minimum word count |
| max_words | 2500 | Maximum word count |
| faq_count | 5 | FAQ items to generate |

#### Enrichment
| Column | Default | Description |
|--------|---------|-------------|
| images_count | 1 | AI images (0 = none) |
| internal_links_count | 3 | Links to own posts |
| external_links_count | 5 | Links to external sites |
| youtube_embeds_count | 1 | Videos to embed |

#### Image Settings
| Column | Default | Description |
|--------|---------|-------------|
| image_provider_priority | fal,openai,pexels | Provider order |
| openai_image_model | dall-e-3 | DALL-E version |
| fal_model | fal-ai/flux/schnell | fal.ai model |

#### Notifications
| Column | Default | Description |
|--------|---------|-------------|
| speedyindex_enabled | FALSE | Submit to SpeedyIndex |
| telegram_enabled | TRUE | Telegram alerts |
| email_enabled | FALSE | Email notifications |

### Creating the Topics Sheet

| Column | Description |
|--------|-------------|
| topic | The blog post title/topic |
| status | PENDING, PROCESSING, DONE, ERROR |
| locked_at | Auto-filled timestamp |
| post_url | Auto-filled post URL |
| error | Auto-filled error message |
| tags | tag1, tag2, tag3 |
| categories | Category Name |

### Finding Spreadsheet ID and GID

**Spreadsheet ID** - From URL:
```
https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
```

**GID** - From URL when viewing the sheet:
```
https://docs.google.com/.../edit#gid=[GID]
```

---

## 4.2 WordPress Configuration

### Installing the Plugin

The n8n Autoblogger Helper plugin provides custom REST API endpoints for:
- Image uploads (base64 and URL sideload)
- SEO meta updates (Yoast/RankMath)
- Category creation

**Installation:**

1. Download `n8n-autoblogger-helper.zip`
2. Go to Plugins → Add New → Upload Plugin
3. Choose the file and click Install Now
4. Click Activate

**Verify Installation:**

Visit: `https://yoursite.com/wp-json/n8n/v1/`

### Setting Up Authentication

#### Option A: JWT Authentication (Recommended)

1. Install "JWT Authentication for WP REST API" plugin

2. Add to `wp-config.php`:
```php
define('JWT_AUTH_SECRET_KEY', 'your-unique-secret-key');
define('JWT_AUTH_CORS_ENABLE', true);
```

3. Add to `.htaccess` (before `# BEGIN WordPress`):
```apache
RewriteEngine on
RewriteCond %{HTTP:Authorization} ^(.*)
RewriteRule ^(.*) - [E=HTTP_AUTHORIZATION:%1]
SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1
```

4. In your Sites sheet:
   - Set `auth_mode` to `jwt`
   - Set `jwt_user` to your WordPress username
   - Set `jwt_password` to your WordPress password

#### Option B: Application Passwords

1. Go to Users → Your Profile → Application Passwords
2. Enter name "n8n" and click Add New
3. Copy the password (with spaces)

4. In your Sites sheet:
   - Set `auth_mode` to `basic`
   - Set `wp_user` to your username
   - Set `wp_app_password` to the generated password

---

## 4.3 n8n Variables

Go to **Settings → Variables** in n8n and add:

### Required
| Variable | Description |
|----------|-------------|
| OPENAI_API_KEY | Your OpenAI API key (sk-...) |

### Optional - Content Enhancement
| Variable | Description |
|----------|-------------|
| GOOGLE_CSE_API_KEY | Google Custom Search API key |
| GOOGLE_CSE_CX | Search Engine ID |
| YOUTUBE_API_KEY | YouTube Data API key |

### Optional - Image Generation
| Variable | Description |
|----------|-------------|
| FAL_API_KEY | fal.ai API key |
| PEXELS_API_KEY | Pexels API key |

### Optional - Notifications
| Variable | Description |
|----------|-------------|
| TELEGRAM_BOT_TOKEN | Telegram bot token |
| TELEGRAM_CHAT_ID | Chat/group ID |
| NOTIFICATION_EMAIL | Email recipient |
| RESEND_API_KEY | Resend.com API key |

---

# 5. Configuration Reference

## Complete Sites Sheet Columns

| Column | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| site_id | String | ✅ | - | Unique site identifier |
| site_name | String | | - | Display name for notifications |
| base_url | String | ✅ | - | WordPress site URL |
| auth_mode | String | ✅ | jwt | "jwt" or "basic" |
| jwt_user | String | * | - | JWT username |
| jwt_password | String | * | - | JWT password |
| jwt_token | String | | - | Cached token (auto-filled) |
| wp_user | String | * | - | Basic auth username |
| wp_app_password | String | * | - | Application password |
| topics_spreadsheet_id | String | ✅ | - | Topics sheet ID |
| topics_gid | Number | ✅ | - | Topics sheet GID |
| post_interval_minutes | Number | | 60 | Min. between posts |
| last_posted_at | DateTime | | - | Auto-filled |
| enabled | Boolean | | TRUE | Process this site |
| post_status | String | | draft | draft/publish |
| tone | String | | informative | Writing style |
| min_words | Number | | 1500 | Minimum words |
| max_words | Number | | 2500 | Maximum words |
| faq_count | Number | | 5 | FAQ items |
| default_category | String | | - | Fallback category |
| images_count | Number | | 0 | AI images |
| internal_links_count | Number | | 3 | Internal links |
| external_links_count | Number | | 5 | External links |
| youtube_embeds_count | Number | | 1 | Video embeds |
| image_provider_priority | String | | fal,openai,pexels | Provider order |
| openai_model | String | | gpt-4o-mini | GPT model |
| openai_image_model | String | | dall-e-3 | Image model |
| fal_model | String | | fal-ai/flux/schnell | fal model |
| speedyindex_enabled | Boolean | | FALSE | SpeedyIndex |
| telegram_enabled | Boolean | | TRUE | Telegram alerts |
| email_enabled | Boolean | | FALSE | Email alerts |

*Required depending on auth_mode

## Image Provider Comparison

| Provider | Type | Speed | Quality | Cost |
|----------|------|-------|---------|------|
| fal.ai | AI Generated | ⚡ Fast | ★★★★ | ~$0.01/img |
| OpenAI DALL-E 3 | AI Generated | Medium | ★★★★★ | ~$0.04/img |
| OpenAI DALL-E 2 | AI Generated | Medium | ★★★ | ~$0.02/img |
| Pexels | Stock Photo | ⚡⚡ Instant | Varies | Free |

---

# 6. Using the System

## Adding Topics

1. Open your Topics Google Sheet
2. Add topics in the `topic` column
3. Set `status` to `PENDING`
4. Optionally add:
   - `tags`: comma-separated tags
   - `categories`: comma-separated categories

**Example:**
| topic | status | tags | categories |
|-------|--------|------|------------|
| 10 Best Coffee Brewing Methods | PENDING | coffee, brewing | Lifestyle |
| How to Start a Home Garden | PENDING | gardening, home | DIY, Outdoors |

## Running Manually

1. Open the Master Scheduler workflow
2. Click "Test workflow"
3. Monitor the execution
4. Check output for success/errors

## Running on Schedule

1. Open Master Scheduler workflow
2. Click the Schedule Trigger node
3. Configure your desired interval (e.g., every 15 minutes)
4. Toggle the workflow to "Active"

## Monitoring Posts

**Check the Topics Sheet:**
- `status` changes to `DONE` on success
- `post_url` shows the published URL
- `error` shows any error messages

**Check WordPress:**
- Posts appear in Posts → All Posts
- Check draft or published status

## Understanding the Output

Each execution returns detailed debug info:

```json
{
  "ok": true,
  "post_id": 123,
  "post_url": "https://site.com/?p=123",
  "title": "Article Title",
  "debug": {
    "images_uploaded": 1,
    "internal_links_inserted": 2,
    "external_links_inserted": 3,
    "categories_found": [
      {"requested": "Tech", "matched": "Technology", "id": 5}
    ]
  }
}
```

---

# 7. Troubleshooting

## Authentication Errors

### "JWT authentication failed"

**Check:**
1. JWT plugin is installed and activated
2. `wp-config.php` has the secret key defined
3. `.htaccess` has the authorization rewrite rules
4. Username and password are correct

### "401 Unauthorized"

**For Basic Auth:**
1. Application password is correct (include spaces)
2. Username is exact (case-sensitive)
3. User has edit_posts capability

### "403 Forbidden"

**Causes:**
- Security plugin blocking REST API
- Cloudflare/WAF blocking requests

**Solutions:**
1. Whitelist n8n IPs in security plugins
2. Add bypass rule for `/wp-json/*`

## Image Issues

### Images Not Uploading

**Check:**
1. n8n Autoblogger Helper plugin is installed
2. User has upload_files capability
3. Check `debug.image_errors` for details

### 500 Error on Image Upload

**Solutions:**
1. Increase PHP memory: `define('WP_MEMORY_LIMIT', '256M');`
2. Use `dall-e-2` instead of `dall-e-3`
3. Use `fal` or `pexels` providers (smaller files)

## Category Issues

### Categories Not Created

**Solution:** Ensure plugin v1.2+ is installed (has `/create-category` endpoint)

### Categories Not Assigned

**Check:**
1. Category names spelled correctly
2. Check `debug.categories_found` in output

## SEO Issues

### Meta Not Saving

**Solution:** 
1. Install plugin v1.1+ (has `/update-seo-meta` endpoint)
2. Check `debug.seo_plugins` shows your plugin detected

## Topics Stuck in PROCESSING

**Solution:** Run the Cleanup workflow to reset stuck topics

---

# 8. FAQ

## General Questions

**Q: How many posts can I publish per day?**
A: There's no limit. Set `post_interval_minutes` to control spacing.

**Q: Can I use this with WordPress.com?**
A: Only with WordPress.com Business plan or higher (needs REST API access).

**Q: Does this work with custom post types?**
A: Currently supports standard posts only. Can be modified in the code.

## Content Questions

**Q: Can I edit posts before publishing?**
A: Yes, set `post_status` to `draft` to review before publishing.

**Q: How do I control the writing style?**
A: Use the `tone` field (e.g., "professional", "casual", "humorous").

**Q: Why are there no tables in my articles?**
A: The AI is instructed to include tables, but it depends on the topic. Technical topics usually include tables.

## Technical Questions

**Q: Can I use a different AI model?**
A: Yes, set `openai_model` to any compatible model (e.g., `gpt-4o`, `gpt-4o-mini`).

**Q: How do I add more image providers?**
A: See the Technical Reference for extending the system.

**Q: Is my data secure?**
A: API keys are stored in n8n Variables. Never commit them to version control.

---

# 9. Technical Reference

## Workflow Architecture

### Master Scheduler
- Triggered by cron or manual execution
- Fetches enabled sites from Google Sheets
- Checks posting intervals
- Locks topics before processing
- Calls Publisher for each topic
- Updates topic status

### Publisher Engine
A single Code node that handles:
1. WordPress authentication
2. SERP and YouTube data fetching
3. Content generation via OpenAI
4. Image generation and upload
5. Link and video injection
6. Category/tag management
7. Post publishing
8. SEO meta updates
9. Notifications

### Cleanup Workflow
Resets topics stuck in PROCESSING state after crashes.

## WordPress Plugin API

### POST /wp-json/n8n/v1/upload-image
Upload base64-encoded images.

### POST /wp-json/n8n/v1/sideload-image
Download and upload images from URLs.

### POST /wp-json/n8n/v1/update-seo-meta
Update Yoast/RankMath metadata.

### POST /wp-json/n8n/v1/create-category
Create categories (bypasses REST API permissions).

## Version History

| Version | Changes |
|---------|---------|
| v2.31 | Auto-category creation |
| v2.30 | SEO meta via plugin endpoint |
| v2.29 | Removed JSON-LD (WP blocks scripts) |
| v2.28 | Links only in paragraphs |
| v2.27 | Custom plugin for image uploads |

---

# Support

## Getting Help

1. Check the Troubleshooting section
2. Review the debug output
3. Open a GitHub issue with:
   - Error message
   - Debug output (redact sensitive data)
   - WordPress/n8n versions

## Contributing

See CONTRIBUTING.md for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting code changes

---

*© 2026 n8n WordPress Autoblogger - MIT License*
