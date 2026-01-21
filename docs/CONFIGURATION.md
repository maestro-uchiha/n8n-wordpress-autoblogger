# Configuration Reference

Complete reference for all configuration options in the n8n WordPress Autoblogger.

---

## Table of Contents

1. [Sites Sheet Columns](#sites-sheet-columns)
2. [Topics Sheet Columns](#topics-sheet-columns)
3. [n8n Variables](#n8n-variables)
4. [Per-Site Overrides](#per-site-overrides)
5. [Image Providers](#image-providers)
6. [Notification Setup](#notification-setup)

---

## Sites Sheet Columns

### Core Settings

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `site_id` | String | ✅ | Unique identifier (e.g., site_001) |
| `site_name` | String | | Display name for notifications |
| `base_url` | String | ✅ | WordPress site URL (no trailing slash) |
| `enabled` | Boolean | | TRUE/FALSE - process this site |

### Authentication

| Column | Type | Description |
|--------|------|-------------|
| `auth_mode` | String | `jwt` or `basic` |
| `jwt_user` | String | WordPress username for JWT |
| `jwt_password` | String | WordPress password for JWT |
| `jwt_token` | String | Cached JWT token (auto-filled) |
| `wp_user` | String | Username for Basic auth |
| `wp_app_password` | String | Application password for Basic auth |

### Topics Configuration

| Column | Type | Description |
|--------|------|-------------|
| `topics_spreadsheet_id` | String | Google Sheets ID containing topics |
| `topics_gid` | Number | Sheet GID for topics tab |
| `post_interval_minutes` | Number | Minimum minutes between posts |
| `last_posted_at` | DateTime | Last post timestamp (auto-filled) |

### Content Settings

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `post_status` | String | draft | `draft` or `publish` |
| `tone` | String | informative | Writing style/tone |
| `min_words` | Number | 1500 | Minimum word count |
| `max_words` | Number | 2500 | Maximum word count |
| `faq_count` | Number | 5 | Number of FAQ items |
| `default_category` | String | | Fallback category if none specified |

### Enrichment Settings

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `images_count` | Number | 0 | Number of AI images (0 = disabled) |
| `internal_links_count` | Number | 3 | Internal links to inject |
| `external_links_count` | Number | 5 | External links from SERP |
| `youtube_embeds_count` | Number | 1 | YouTube videos to embed |

### Image Configuration

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `image_provider_priority` | String | fal,openai,pexels | Comma-separated priority list |
| `openai_image_model` | String | dall-e-3 | `dall-e-2` or `dall-e-3` |
| `fal_model` | String | fal-ai/flux/schnell | fal.ai model identifier |

### AI Model Settings

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `openai_model` | String | gpt-4o-mini | GPT model for content |

### Notification Toggles

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `indexing_enabled` | Boolean | FALSE | Submit to FastIndex/SpeedyIndex |
| `telegram_enabled` | Boolean | TRUE | Send Telegram alerts |
| `email_enabled` | Boolean | FALSE | Send email notifications |

---

## Topics Sheet Columns

| Column | Type | Description |
|--------|------|-------------|
| `topic` | String | The blog post topic/title (required) |
| `status` | String | PENDING, PROCESSING, DONE, ERROR |
| `locked_at` | DateTime | When processing started (auto-filled) |
| `post_url` | String | Published post URL (auto-filled) |
| `error` | String | Error message if failed (auto-filled) |
| `tags` | String | Comma or pipe separated tags |
| `categories` | String | Comma or pipe separated categories |

### Status Values

| Status | Meaning |
|--------|---------|
| `PENDING` | Ready to be processed |
| `PROCESSING` | Currently being processed |
| `DONE` | Successfully published |
| `ERROR` | Failed (check error column) |
| `SKIP` | Skip this topic |

---

## n8n Variables

Set these in **Settings → Variables**:

### Required

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |

### Content Generation

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_MODEL` | gpt-4o-mini | Default GPT model |
| `OPENAI_IMAGE_MODEL` | dall-e-2 | Default image model |

### External APIs

| Variable | Description |
|----------|-------------|
| `GOOGLE_CSE_API_KEY` | Google Custom Search API key |
| `GOOGLE_CSE_CX` | Google Custom Search Engine ID |
| `SERPER_API_KEY` | Serper.dev API key (fallback for Google CSE) |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key |

### Image Providers

| Variable | Description |
|----------|-------------|
| `FAL_API_KEY` | fal.ai API key |
| `FAL_MODEL` | Default fal.ai model |
| `PEXELS_API_KEY` | Pexels API key |
| `IMAGE_PROVIDER_PRIORITY_DEFAULT` | Default priority (fal,pexels,openai) |

### Notifications

| Variable | Description |
|----------|-------------|
| `FASTINDEX_API_KEY` | FastIndex.eu API key (recommended) |
| `SPEEDYINDEX_API_KEY` | SpeedyIndex API key (legacy) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat/group ID |
| `NOTIFICATION_EMAIL` | Email recipient |
| `EMAIL_FROM` | Sender email address |

### Cleanup Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PROCESSING_STUCK_THRESHOLD_MINUTES` | 30 | Minutes before resetting stuck PROCESSING posts |

### Email Providers (choose one)

| Variable | Provider |
|----------|----------|
| `RESEND_API_KEY` | Resend.com |
| `SENDGRID_API_KEY` | SendGrid |
| `MAILGUN_API_KEY` + `MAILGUN_DOMAIN` | Mailgun |
| `SMTP2GO_API_KEY` | SMTP2GO |

---

## Per-Site Overrides

These settings in the Sites sheet override global n8n variables:

| Site Column | Overrides Variable |
|-------------|-------------------|
| `openai_model` | OPENAI_MODEL |
| `openai_image_model` | OPENAI_IMAGE_MODEL |
| `fal_model` | FAL_MODEL |
| `image_provider_priority` | IMAGE_PROVIDER_PRIORITY_DEFAULT |

This allows different sites to use different models or image providers.

---

## Image Providers

### Provider Priority

The `image_provider_priority` setting determines the order in which providers are tried:

```
fal,openai,pexels
```

If the first provider fails, the next is tried automatically.

### Provider Comparison

| Provider | Type | Speed | Quality | Cost |
|----------|------|-------|---------|------|
| fal.ai | AI Generated | Fast | High | $0.01-0.05/image |
| OpenAI | AI Generated | Medium | Very High | $0.04-0.08/image |
| Pexels | Stock Photo | Instant | Varies | Free |

### fal.ai Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `fal-ai/flux/schnell` | Fastest | Good | High volume |
| `fal-ai/flux/dev` | Medium | Better | Quality content |
| `fal-ai/fast-sdxl` | Fast | Good | General use |

### OpenAI Models

| Model | Resolution | Quality | Cost |
|-------|------------|---------|------|
| `dall-e-2` | 512x512 | Good | $0.018/image |
| `dall-e-3` | 1024x1024 | Excellent | $0.04/image |

---

## Notification Setup

### Telegram

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get the token (e.g., `123456:ABC-xyz`)
3. Add bot to your channel/group
4. Get chat ID (use [@userinfobot](https://t.me/userinfobot) or API)
5. Set variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### Email (Resend)

1. Sign up at [resend.com](https://resend.com)
2. Verify your domain
3. Create API key
4. Set variables:
   - `RESEND_API_KEY`
   - `EMAIL_FROM` (must be from verified domain)
   - `NOTIFICATION_EMAIL`

### Instant Indexing (FastIndex or SpeedyIndex)

**FastIndex.eu (Recommended)**:
1. Sign up at [fastindex.eu](https://fastindex.eu)
2. Get API key
3. Set `FASTINDEX_API_KEY`
4. Set `indexing_enabled` to TRUE per site

**SpeedyIndex (Legacy)**:
1. Sign up at [speedyindex.com](https://speedyindex.com)
2. Get API key
3. Set `SPEEDYINDEX_API_KEY`
4. Set `indexing_enabled` to TRUE per site

---

## Example Configurations

### Minimal Setup (Text Only)

```
images_count: 0
internal_links_count: 0
external_links_count: 0
youtube_embeds_count: 0
```

### Full Featured

```
images_count: 2
internal_links_count: 3
external_links_count: 5
youtube_embeds_count: 1
image_provider_priority: fal,openai,pexels
indexing_enabled: TRUE
telegram_enabled: TRUE
```

### Budget Conscious

```
images_count: 1
image_provider_priority: pexels,fal
openai_model: gpt-4o-mini
openai_image_model: dall-e-2
```

### High Quality

```
images_count: 3
image_provider_priority: openai,fal
openai_model: gpt-4o
openai_image_model: dall-e-3
min_words: 2500
max_words: 4000
```
