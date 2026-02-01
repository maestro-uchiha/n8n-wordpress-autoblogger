# n8n WordPress Autoblogger v3 (No Global Variables)

**Version:** v3.0-no-globals  
**Compatible with:** n8n Free Tier (no Starter plan required)

## 🎯 What's Different in v3?

This version is designed for users who **cannot or don't want to use n8n's global variables** feature (requires Starter plan at $20+/month).

**Key Difference:** All API keys are stored directly in your Site_Registry Google Sheet instead of n8n global variables.

| Feature | v2 (Standard) | v3 (No Globals) |
|---------|---------------|-----------------|
| n8n Plan Required | Starter ($20+/mo) | Free |
| API Key Storage | n8n Global Variables | Site_Registry Sheet |
| Multi-site Support | ✅ | ✅ |
| Per-site API Keys | ❌ (shared globally) | ✅ (per-site) |
| Setup Complexity | Lower | Slightly Higher |

## 📦 Files in This Version

```
v3/
├── 1_Master_Scheduler.json    # Scheduler workflow (no $vars)
├── 2_Publisher.json           # Publisher workflow (reads keys from site_config)
├── 3_Cleanup.json             # Cleanup workflow (hardcoded thresholds)
├── README.md                  # This file
└── templates/
    ├── Site_Registry.csv      # Template with API key columns
    ├── Topics_Template.csv    # Topics sheet template
    └── SHEETS_SETUP_GUIDE.md  # Setup instructions
```

## 🚀 Quick Start

### Step 1: Create Your Google Sheet

1. Create a new Google Sheet for your Site Registry
2. Copy the headers from `templates/Site_Registry.csv`
3. Fill in your site details AND API keys in the appropriate columns

### Step 2: Import Workflows

1. In n8n, go to **Workflows** → **Import from File**
2. Import these files in order:
   - `2_Publisher.json` (import first, note the workflow ID)
   - `1_Master_Scheduler.json`
   - `3_Cleanup.json`

### Step 3: Configure Master Scheduler

After importing `1_Master_Scheduler.json`:

1. Open the **Read Site Registry** node
2. Replace `SITE_REGISTRY_SPREADSHEET_ID` with your Google Sheet ID
3. Replace `SITE_REGISTRY_GID` with your sheet's GID (usually `0`)
4. Connect your Google Sheets OAuth credentials

### Step 4: Configure Cleanup Workflow

Same process for `3_Cleanup.json`:

1. Open the **Read Site Registry** node
2. Replace the placeholder IDs with your actual values
3. Connect Google Sheets credentials

### Step 5: Set Publisher Workflow ID

In the Master Scheduler's **Prepare Site Data** code node, replace:
```javascript
publisher_workflow_id: 'PUBLISHER_WORKFLOW_ID'
```

With your actual Publisher workflow ID (visible in the URL when editing the Publisher workflow).

## 📊 Site_Registry Columns

### Core Columns (Required)
| Column | Description | Example |
|--------|-------------|---------|
| `site_id` | Unique identifier | `site_001` |
| `site_name` | Display name | `My Tech Blog` |
| `base_url` | WordPress URL | `https://myblog.com` |
| `enabled` | Active status | `true` / `false` |

### Authentication
| Column | Description |
|--------|-------------|
| `auth_mode` | `jwt` or `basic` |
| `jwt_user` | JWT username |
| `jwt_password` | JWT password |
| `jwt_token` | Cached JWT token |
| `jwt_token_endpoint` | Custom JWT endpoint URL (optional) |
| `wp_user` | WordPress username (for basic auth) |
| `wp_app_password` | Application password |

### Content Settings
| Column | Description | Default |
|--------|-------------|---------|
| `post_status` | `draft` or `publish` | `draft` |
| `default_category` | Default category if none specified | - |
| `tone` | Writing style | `informative and engaging` |
| `min_words` | Minimum word count | `1500` |
| `max_words` | Maximum word count | `2500` |
| `faq_count` | Number of FAQs | `5` |
| `images_count` | Number of images | `2` |
| `images_min` / `images_max` | Random range for images | - |

### API Keys (v3 Specific) ⭐

These columns store your API keys **per-site**:

| Column | Service | Required |
|--------|---------|----------|
| `openai_api_key` | OpenAI (content generation) | ✅ **Yes** |
| `google_cse_api_key` | Google Custom Search | Optional |
| `google_cse_cx` | Google CSE ID | Optional |
| `youtube_api_key` | YouTube Data API | Optional |
| `fal_api_key` | fal.ai image generation | Optional |
| `pexels_api_key` | Pexels stock photos | Optional |
| `serper_api_key` | Serper.dev (SERP fallback) | Optional |
| `speedyindex_api_key` | SpeedyIndex | Optional |
| `fastindex_api_key` | FastIndex.eu | Optional |
| `telegram_bot_token` | Telegram notifications | Optional |
| `telegram_chat_id` | Telegram chat ID | Optional |
| `notification_email` | Email recipient | Optional |
| `email_from` | Email sender address | Optional |
| `email_provider` | `resend`, `sendgrid`, `mailgun`, `smtp2go` | Optional |
| `resend_api_key` | Resend API key | Optional |
| `sendgrid_api_key` | SendGrid API key | Optional |
| `mailgun_api_key` | Mailgun API key | Optional |
| `mailgun_domain` | Mailgun domain | Optional |
| `smtp2go_api_key` | SMTP2GO API key | Optional |

### Model Configuration
| Column | Description | Default |
|--------|-------------|---------|
| `openai_model` | Chat model | `gpt-4o-mini` |
| `openai_image_model` | Image model | `dall-e-2` |
| `fal_model` | fal.ai model | `fal-ai/flux/schnell` |
| `image_provider_priority` | Provider order | `fal,pexels,openai` |

## 🔒 Security Considerations

Since API keys are stored in Google Sheets:

1. **Restrict Sheet Access**: Only share with accounts that need it
2. **Use Service Account**: For production, use a dedicated service account
3. **Regular Rotation**: Rotate API keys periodically
4. **Audit Access**: Monitor who has access to the sheet

## 🔄 Migrating from v2

If you're migrating from v2:

1. **Export your global variables** (Settings → Variables)
2. **Add the new columns** to your Site_Registry sheet
3. **Copy API keys** from globals to the sheet columns
4. **Import v3 workflows** (don't overwrite v2 if you want to keep it)
5. **Test thoroughly** before activating

### Quick Migration Checklist

- [ ] Added `openai_api_key` column with your key
- [ ] Added `google_cse_api_key` and `google_cse_cx` if using Google CSE
- [ ] Added `youtube_api_key` if using YouTube embeds
- [ ] Added `fal_api_key` if using fal.ai images
- [ ] Added `pexels_api_key` if using Pexels
- [ ] Added `telegram_bot_token` and `telegram_chat_id` for notifications
- [ ] Updated Master Scheduler with correct Spreadsheet ID and GID
- [ ] Updated Cleanup workflow with correct Spreadsheet ID and GID
- [ ] Set correct Publisher workflow ID in Master Scheduler

## 🐛 Troubleshooting

### "openai_api_key is missing from Site_Registry"

The Publisher workflow requires an OpenAI API key. Make sure:
1. You have an `openai_api_key` column in your Site_Registry
2. The column has your API key value (not empty)

### "SITE_REGISTRY_SPREADSHEET_ID" appears in errors

You forgot to replace the placeholder. Edit the workflow and replace:
- `SITE_REGISTRY_SPREADSHEET_ID` → Your actual Google Sheet ID
- `SITE_REGISTRY_GID` → Your sheet's GID (usually `0`)

### Images not generating

Check that your image provider API keys are set:
- `fal_api_key` for fal.ai
- `pexels_api_key` for Pexels
- OpenAI key (already required) for DALL-E

### YouTube embeds not appearing

Add `youtube_api_key` column with a valid YouTube Data API v3 key.

## 📝 Version History

### v3.0 (2024)
- Initial no-globals version
- All API keys moved to Site_Registry columns
- Compatible with n8n Free tier
- Based on v2.49 Publisher engine (humanized prompts, anti-AI detection)

## 🤝 Support

For issues specific to v3:
- Open an issue with `[v3]` prefix
- Include whether you're using n8n Cloud or self-hosted
- Include relevant error messages (redact API keys!)

## 📄 License

MIT License - see main repository LICENSE file.
