# Setup Guide - n8n WordPress Autoblogger

This guide walks you through setting up the autoblogger from scratch. No coding required!

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Set Up Google Sheets](#step-1-set-up-google-sheets)
3. [Step 2: Install WordPress Plugin](#step-2-install-wordpress-plugin)
4. [Step 3: Configure WordPress Authentication](#step-3-configure-wordpress-authentication)
5. [Step 4: Get API Keys](#step-4-get-api-keys)
6. [Step 5: Import n8n Workflows](#step-5-import-n8n-workflows)
7. [Step 6: Configure n8n Variables](#step-6-configure-n8n-variables)
8. [Step 7: Test Your Setup](#step-7-test-your-setup)
9. [Step 8: Go Live](#step-8-go-live)

---

## Prerequisites

Before starting, you'll need:

- ✅ **n8n account** (cloud.n8n.io or self-hosted)
- ✅ **WordPress site(s)** with admin access
- ✅ **Google account** for Google Sheets
- ✅ **OpenAI account** with API access

---

## Step 1: Set Up Google Sheets

### Create the Sites Sheet

1. Create a new Google Spreadsheet
2. Rename the first sheet to **"Sites"**
3. Add these column headers in row 1:

| Column | Header | Example Value |
|--------|--------|---------------|
| A | site_id | site_001 |
| B | site_name | My Blog |
| C | base_url | https://myblog.com |
| D | auth_mode | jwt |
| E | jwt_user | n8n-admin |
| F | jwt_password | your-password |
| G | jwt_token | (leave empty) |
| H | wp_user | n8n-admin |
| I | wp_app_password | xxxx xxxx xxxx |
| J | topics_spreadsheet_id | (same as this sheet's ID) |
| K | topics_gid | (GID of Topics sheet) |
| L | post_interval_minutes | 60 |
| M | last_posted_at | (leave empty) |
| N | enabled | TRUE |
| O | post_status | draft |
| P | tone | informative and engaging |
| Q | min_words | 1500 |
| R | max_words | 2500 |
| S | faq_count | 5 |
| T | images_count | 1 |
| U | internal_links_count | 3 |
| V | external_links_count | 3 |
| W | youtube_embeds_count | 1 |
| X | image_provider_priority | fal,openai,pexels |
| Y | speedyindex_enabled | FALSE |
| Z | telegram_enabled | FALSE |
| AA | email_enabled | FALSE |
| AB | openai_model | gpt-4o-mini |
| AC | openai_image_model | dall-e-3 |
| AD | fal_model | fal-ai/flux/schnell |

### Create the Topics Sheet

1. Add a new sheet, name it **"Topics"** (or any name)
2. Note the **GID** from the URL: `#gid=123456789`
3. Add these column headers:

| Column | Header | Description |
|--------|--------|-------------|
| A | topic | The blog post topic/title |
| B | status | PENDING, PROCESSING, DONE, ERROR |
| C | locked_at | Timestamp when processing started |
| D | post_url | URL of published post |
| E | error | Error message if failed |
| F | tags | tag1, tag2, tag3 |
| G | categories | Category Name |

4. Add your topics in column A, set status to **PENDING**

### Get the Spreadsheet ID

From the URL: `https://docs.google.com/spreadsheets/d/`**`1ABC123xyz`**`/edit`

The part between `/d/` and `/edit` is your **Spreadsheet ID**.

---

## Step 2: Install WordPress Plugin

The plugin provides custom REST endpoints for images, SEO, and categories.

### Option A: Upload ZIP (Recommended)

1. Download `wordpress-plugin/n8n-autoblogger-helper.zip`
2. Go to WordPress Admin → **Plugins** → **Add New** → **Upload Plugin**
3. Choose the ZIP file and click **Install Now**
4. Click **Activate**

### Option B: Manual Upload

1. Upload `n8n-image-upload.php` to `/wp-content/plugins/`
2. Go to **Plugins** and activate "n8n Autoblogger Helper"

### Verify Installation

Visit: `https://yoursite.com/wp-json/n8n/v1/`

You should see the available endpoints (or a permissions error, which is normal).

---

## Step 3: Configure WordPress Authentication

Choose ONE method:

### Option A: JWT Authentication (Recommended)

1. Install the **JWT Authentication for WP REST API** plugin
2. Add to `wp-config.php`:
   ```php
   define('JWT_AUTH_SECRET_KEY', 'your-secret-key-here');
   define('JWT_AUTH_CORS_ENABLE', true);
   ```
3. Add to `.htaccess` (Apache) before `# BEGIN WordPress`:
   ```apache
   RewriteEngine on
   RewriteCond %{HTTP:Authorization} ^(.*)
   RewriteRule ^(.*) - [E=HTTP_AUTHORIZATION:%1]
   SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1
   ```
4. In your Sites sheet, set:
   - `auth_mode`: jwt
   - `jwt_user`: your WordPress username
   - `jwt_password`: your WordPress password

### Option B: Application Passwords

1. Go to **Users** → **Your Profile** → **Application Passwords**
2. Enter a name (e.g., "n8n") and click **Add New**
3. Copy the generated password (spaces included)
4. In your Sites sheet, set:
   - `auth_mode`: basic
   - `wp_user`: your WordPress username
   - `wp_app_password`: the generated password

---

## Step 4: Get API Keys

### Required: OpenAI

1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to **API Keys** → **Create new secret key**
3. Copy and save the key

### Optional: Google Custom Search (for external links)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Custom Search API**
4. Create credentials → **API Key**
5. Go to [Programmable Search Engine](https://programmablesearchengine.google.com)
6. Create a search engine for "entire web"
7. Copy the **Search Engine ID (cx)**

### Optional: YouTube API (for video embeds)

1. In Google Cloud Console, enable **YouTube Data API v3**
2. Use the same API key as Custom Search

### Optional: fal.ai (for images)

1. Go to [fal.ai](https://fal.ai)
2. Create account → **Settings** → **API Keys**
3. Create and copy the key

### Optional: Pexels (for stock photos)

1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Sign up and get your API key

---

## Step 5: Import n8n Workflows

1. Log into your n8n instance
2. Click **+ Add workflow**
3. Click the **⋯** menu → **Import from file**
4. Import these files in order:
   - `Current/Master Scheduler (Multi-site).json`
   - `Current/Publisher (Autoblogging Engine).json`
   - `Current/Cleanup (Stuck Locks).json`

---

## Step 6: Configure n8n Variables

1. Go to **Settings** → **Variables** (or **n8n Settings** → **Variables**)
2. Add these variables:

| Variable Name | Value | Required |
|---------------|-------|----------|
| OPENAI_API_KEY | sk-... | ✅ Yes |
| OPENAI_MODEL | gpt-4o-mini | Optional |
| OPENAI_IMAGE_MODEL | dall-e-3 | Optional |
| GOOGLE_CSE_API_KEY | AIza... | For links |
| GOOGLE_CSE_CX | 123abc:xyz | For links |
| YOUTUBE_API_KEY | AIza... | For videos |
| FAL_API_KEY | fal_... | For images |
| PEXELS_API_KEY | abc123 | For images |
| IMAGE_PROVIDER_PRIORITY_DEFAULT | fal,openai,pexels | Optional |
| SPEEDYINDEX_API_KEY | ... | For indexing |
| TELEGRAM_BOT_TOKEN | 123:ABC | For alerts |
| TELEGRAM_CHAT_ID | -100123 | For alerts |
| NOTIFICATION_EMAIL | you@email.com | For alerts |

---

## Step 7: Test Your Setup

### Test the Publisher Directly

1. Open **Publisher (Autoblogging Engine)** workflow
2. Click **Test workflow**
3. In the trigger node, enter test data:
   ```json
   {
     "site": {
       "base_url": "https://yoursite.com",
       "auth_mode": "jwt",
       "jwt_user": "admin",
       "jwt_password": "password",
       "post_status": "draft"
     },
     "topicRow": {
       "topic": "Test Article About Coffee"
     }
   }
   ```
4. Run and check the output for errors

### Test the Full Flow

1. Add a test topic to your Topics sheet with status **PENDING**
2. Open **Master Scheduler** workflow
3. Click **Test workflow**
4. Check if the post was created in WordPress

---

## Step 8: Go Live

### Activate the Master Scheduler

1. Open **Master Scheduler (Multi-site)** workflow
2. Click the **Active** toggle (top right)
3. Set your desired schedule (e.g., every 15 minutes)

### Monitor Your Posts

- Check the **Topics sheet** for status updates
- Check WordPress for new draft/published posts
- Enable Telegram notifications for real-time alerts

---

## 🎉 You're Done!

The system will now:
1. Check your Topics sheet on schedule
2. Find PENDING topics
3. Generate AI content with images
4. Publish to WordPress
5. Update the sheet status

---

## Next Steps

- Read [Configuration Guide](CONFIGURATION.md) to customize settings
- See [Troubleshooting](TROUBLESHOOTING.md) if you hit issues
- Check [Technical Reference](TECHNICAL.md) for advanced customization
