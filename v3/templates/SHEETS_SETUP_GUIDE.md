# Google Sheets Setup Guide (v3 - No Globals)

## ⚠️ v3 Difference

In v3, **all API keys are stored in the Site_Registry sheet** instead of n8n global variables. This allows the system to work on n8n's Free tier.

---

## Step-by-Step Setup

### 1. Create the Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it something like "Autoblogger - Site Registry"
4. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/1ABC123XYZ.../edit
                                          ^^^^^^^^^^^^
                                          This is your SITE_REGISTRY_SPREADSHEET_ID
   ```

### 2. Set Up Site_Registry Sheet

1. The first sheet (Sheet1) will be your Site_Registry
2. Rename it to "Site_Registry" (optional but recommended)
3. Note the **gid** from the URL (usually `0` for the first sheet):
   ```
   https://docs.google.com/spreadsheets/d/.../edit#gid=0
                                                     ^
                                                     This is SITE_REGISTRY_GID
   ```

4. **Import the template:**
   - Go to File → Import → Upload
   - Upload `Site_Registry.csv`
   - Choose "Replace current sheet"

### 3. Fill in Your API Keys ⭐

**CRITICAL for v3:** You must add your API keys to the sheet.

| Column | Where to Get It |
|--------|-----------------|
| `openai_api_key` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) - **REQUIRED** |
| `google_cse_api_key` | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `google_cse_cx` | [Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all) |
| `youtube_api_key` | [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com) |
| `fal_api_key` | [fal.ai/dashboard](https://fal.ai/dashboard) |
| `pexels_api_key` | [pexels.com/api](https://www.pexels.com/api/) |
| `serper_api_key` | [serper.dev](https://serper.dev/) |
| `speedyindex_api_key` | [SpeedyIndex](https://speedyindex.com/) |
| `fastindex_api_key` | [FastIndex.eu](https://fastindex.eu/) |
| `telegram_bot_token` | [BotFather](https://t.me/BotFather) |
| `telegram_chat_id` | [Get your chat ID](https://api.telegram.org/bot<TOKEN>/getUpdates) |

### 4. Create Topics Sheets (One Per Site)

1. Click the **+** button at the bottom to add a new sheet
2. Name it something like "Topics_Site001" or your site name
3. **Get the gid** from the URL when viewing this sheet:
   ```
   https://docs.google.com/spreadsheets/d/.../edit#gid=414510277
                                                     ^^^^^^^^^^
                                                     This is topics_gid for Site_Registry
   ```

4. **Import the template:**
   - Go to File → Import → Upload
   - Upload `Topics_Template.csv`
   - Choose "Insert new sheet" or "Replace current sheet"

5. **Put the gid number** in the `topics_gid` column of Site_Registry

### 5. Update Workflows with Your IDs

After importing the v3 workflows, you need to manually replace placeholders:

**In Master Scheduler (1_Master_Scheduler.json):**
1. Open "Read Site Registry" node
2. Replace `SITE_REGISTRY_SPREADSHEET_ID` with your actual ID
3. Replace `SITE_REGISTRY_GID` with your GID

**In Cleanup (3_Cleanup.json):**
1. Same process - update the "Read Site Registry" node

---

## Column Reference

### Site_Registry Core Columns

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `site_id` | ✅ | Unique identifier | `site_001` |
| `site_name` | ✅ | Display name | `My Tech Blog` |
| `base_url` | ✅ | WordPress URL (no trailing /) | `https://myblog.com` |
| `auth_mode` | ✅ | `jwt` or `basic` | `jwt` |
| `jwt_user` | If jwt | JWT username | `admin` |
| `jwt_password` | If jwt | JWT password | `secretpass123` |
| `jwt_token` | Optional | Cached JWT token | (auto-managed) |
| `jwt_token_endpoint` | Optional | Custom JWT endpoint URL | (default: /wp-json/jwt-auth/v1/token) |
| `wp_user` | If basic | WordPress username | `editor` |
| `wp_app_password` | If basic | Application password | `xxxx xxxx xxxx xxxx` |
| `topics_spreadsheet_id` | ✅ | Spreadsheet ID for topics | Same as registry or different |
| `topics_gid` | ✅ | **Numeric gid** of topics sheet | `414510277` |
| `post_interval_minutes` | ✅ | Minutes between posts | `120` |
| `last_posted_at` | Auto | Last post timestamp | (auto-updated) |
| `enabled` | ✅ | `TRUE` or `FALSE` | `TRUE` |

### Content Settings Columns

| Column | Required | Description | Default |
|--------|----------|-------------|---------|
| `post_status` | Optional | `publish` or `draft` | `draft` |
| `default_category` | Optional | Default category if none specified | - |
| `tone` | Optional | Writing style | `informative and engaging` |
| `min_words` | Optional | Min article length | `1500` |
| `max_words` | Optional | Max article length | `2500` |
| `faq_count` | Optional | Number of FAQs | `5` |
| `images_count` | Optional | Fixed images count | `2` |
| `images_min` | Optional | Min images (random) | - |
| `images_max` | Optional | Max images (random) | - |
| `internal_links_count` | Optional | Internal links | `3` |
| `internal_links_min` | Optional | Min internal (random) | - |
| `internal_links_max` | Optional | Max internal (random) | - |
| `external_links_count` | Optional | External links | `5` |
| `external_links_min` | Optional | Min external (random) | - |
| `external_links_max` | Optional | Max external (random) | - |
| `youtube_embeds_count` | Optional | YouTube videos | `1` |
| `youtube_embeds_min` | Optional | Min YouTube (random) | - |
| `youtube_embeds_max` | Optional | Max YouTube (random) | - |
| `image_provider_priority` | Optional | Fallback order | `fal,pexels,openai` |

### API Key Columns (v3 Specific) ⭐

| Column | Required | Description |
|--------|----------|-------------|
| `openai_api_key` | ✅ **Yes** | OpenAI API key for content generation |
| `openai_model` | Optional | Model name (default: `gpt-4o-mini`) |
| `openai_image_model` | Optional | Image model (default: `dall-e-2`) |
| `google_cse_api_key` | Optional | Google Custom Search API key |
| `google_cse_cx` | Optional | Google Custom Search Engine ID |
| `youtube_api_key` | Optional | YouTube Data API v3 key |
| `fal_api_key` | Optional | fal.ai API key |
| `fal_model` | Optional | fal model (default: `fal-ai/flux/schnell`) |
| `pexels_api_key` | Optional | Pexels API key |
| `serper_api_key` | Optional | Serper.dev API key (SERP fallback) |
| `speedyindex_api_key` | Optional | SpeedyIndex API key |
| `fastindex_api_key` | Optional | FastIndex.eu API key |

### Notification Columns

| Column | Required | Description |
|--------|----------|-------------|
| `indexing_enabled` | Optional | Enable auto-indexing (`true`/`false`) |
| `telegram_enabled` | Optional | Enable Telegram notifications |
| `telegram_bot_token` | If telegram | Bot token from BotFather |
| `telegram_chat_id` | If telegram | Your chat ID |
| `email_enabled` | Optional | Enable email notifications |
| `notification_email` | If email | Recipient email |
| `email_from` | If email | Sender address |
| `email_provider` | If email | `resend`, `sendgrid`, `mailgun`, `smtp2go` |
| `resend_api_key` | If resend | Resend API key |
| `sendgrid_api_key` | If sendgrid | SendGrid API key |
| `mailgun_api_key` | If mailgun | Mailgun API key |
| `mailgun_domain` | If mailgun | Mailgun domain |
| `smtp2go_api_key` | If smtp2go | SMTP2GO API key |

### Topics Columns

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `topic` | ✅ | The blog topic/keyword | `Best Practices for Remote Work` |
| `status` | ✅ | `QUEUED`, `PROCESSING`, `DONE`, `FAILED` | `QUEUED` |
| `locked_at` | Auto | When processing started | (auto-filled) |
| `post_url` | Auto | Published URL | (auto-filled on success) |
| `error` | Auto | Error message | (auto-filled on failure) |
| `tags` | Optional | Comma-separated | `remote work,productivity` |
| `categories` | Optional | Comma-separated | `Technology,Lifestyle` |
| `created_at` | Optional | When added | `2024-01-19T00:00:00Z` |
| `updated_at` | Auto | Last update | (auto-updated) |

---

## Example Setup

### Your Spreadsheet Structure:

```
📊 Autoblogger - Site Registry
│
├── Tab 1: Site_Registry (gid=0)
│   └── Row 2: site_001, My Tech Blog, https://tech.com, jwt, ..., openai_api_key=sk-xxx
│   └── Row 3: site_002, Health Blog, https://health.com, basic, ..., openai_api_key=sk-yyy
│
├── Tab 2: Topics_TechBlog (gid=123456789)
│   └── Row 2: "Best AI Tools 2024", QUEUED, ...
│   └── Row 3: "Remote Work Tips", QUEUED, ...
│
└── Tab 3: Topics_HealthBlog (gid=987654321)
    └── Row 2: "Healthy Breakfast Ideas", QUEUED, ...
    └── Row 3: "Morning Yoga Routine", QUEUED, ...
```

### Manual Workflow Configuration:

After importing v3 workflows, replace these placeholders:

```
SITE_REGISTRY_SPREADSHEET_ID = 1ABC123XYZ... (from spreadsheet URL)
SITE_REGISTRY_GID = 0 (or whatever gid Site_Registry has)
PUBLISHER_WORKFLOW_ID = your Publisher workflow ID (from URL)
```

---

## Security Tips

Since API keys are now in Google Sheets:

1. **Don't share the sheet** with anyone who doesn't need access
2. **Use a dedicated Google account** for n8n integration
3. **Rotate API keys regularly** if you suspect exposure
4. **Monitor API usage** on respective platforms

---

## Finding the GID

The **gid** is the numeric identifier at the end of the Google Sheets URL:

```
https://docs.google.com/spreadsheets/d/1ABC123.../edit#gid=414510277
                                                        ^^^^^^^^^^^
                                                        This number is the gid
```

- First sheet is usually `gid=0`
- Each new sheet gets a random large number like `414510277`
- You MUST use this numeric value in the `topics_gid` column

---

## Quick Import Instructions

1. Open your Google Spreadsheet
2. Go to **File → Import**
3. Select **Upload** tab
4. Upload the CSV file
5. Choose **"Replace current sheet"** or **"Insert new sheet"**
6. Click **Import data**

Done! Now fill in your actual values and API keys.
