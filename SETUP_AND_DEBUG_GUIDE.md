# n8n Autoblogging Platform - Setup & Debugging Guide

## 🎯 Quick Diagnostic Checklist

Before troubleshooting, verify these essentials:

### ✅ 1. n8n Variables Configuration
Go to **Settings → Variables** in n8n and ensure these are set:

#### Required (MUST have values):
- `SITE_REGISTRY_SPREADSHEET_ID` - Your Google Sheet ID (from the URL)
- `SITE_REGISTRY_SHEET_ID` - The exact tab name (e.g., "Site_Registry")
- `OPENAI_API_KEY` - Your OpenAI API key

#### Recommended (with defaults):
- `OPENAI_MODEL_DEFAULT` = `gpt-4o-mini` or `gpt-4o`
- `OPENAI_IMAGE_MODEL_DEFAULT` = `dall-e-3` (NOT `gpt-image-1-mini`)
- `IMAGE_PROVIDER_PRIORITY_DEFAULT` = `openai,fal,pexels`
- `PROCESSING_STUCK_THRESHOLD_MINUTES` = `60`

#### Optional (for enhanced features):
- `GOOGLE_CSE_API_KEY` - For SERP research
- `GOOGLE_CSE_CX` - Custom Search Engine ID
- `YOUTUBE_API_KEY` - For video embeds
- `FAL_API_KEY` - For image generation fallback
- `FAL_FLUX_ENDPOINT_DEFAULT` = `https://queue.fal.run/fal-ai/flux/dev`
- `PEXELS_API_KEY` - For stock image fallback
- `SPEEDYINDEX_API_KEY` - For indexing
- `SPEEDYINDEX_ENDPOINT_URL` - SpeedyIndex API endpoint
- `TELEGRAM_BOT_TOKEN` - For notifications
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

#### Critical Variable for Workflow Communication:
- `PUBLISHER_ID` - The workflow ID of "Publisher (Autoblogging Engine)"
  - To get this: Open Publisher workflow → Copy the ID from the URL

---

### ✅ 2. Google Sheets Setup

#### A) Site Registry Sheet
Create a Google Sheet with tab named **exactly** `Site_Registry` (case-sensitive).

**Required Columns (minimum):**
```
site_name | base_url | wp_user | wp_app_password | topics_sheet_id | topics_sheet_tab_id | schedule_mode | interval | post_status
```

**Example Row:**
```
My Blog | https://example.com | admin | xxxx xxxx xxxx xxxx | 1a2b3c4d5e6f7g8h | Topics | minutes | 30 | draft
```

**Full Column List:**
- `site_name` - Friendly name for your site
- `base_url` - Full URL with https:// (NO trailing slash)
- `wp_user` - WordPress admin username
- `wp_app_password` - WordPress Application Password (NOT regular password)
- `auth_mode` - Optional: `basic` (default) or `jwt`
- `topics_sheet_id` - Google Sheet ID for this site's topics
- `topics_sheet_tab_id` - Tab name in topics sheet (e.g., "Topics")

**Scheduling:**
- `schedule_mode` - `minutes`, `hours`, `daily`, or `weekly`
- `interval` - Number (for minutes/hours mode)
- `daily_time` - HH:mm format (e.g., "09:00")
- `weekly_day` - Mon, Tue, Wed, Thu, Fri, Sat, Sun
- `window_start` - Optional: HH:mm (e.g., "08:00")
- `window_end` - Optional: HH:mm (e.g., "18:00")
- `timezone` - Optional: e.g., "America/New_York" (default: Africa/Douala)
- `last_posted_at` - Auto-filled by system

**Content Controls:**
- `tone` - e.g., "professional", "casual", "technical"
- `min_words` - e.g., 800
- `max_words` - e.g., 1600
- `faq_count` - Number of FAQ items to include
- `tables_mode` - `auto` (only if useful)
- `charts_mode` - `auto` (only if necessary)

**Feature Counts (0 = disabled):**
- `images_count` - Number of images per post
- `internal_links_count` - Number of internal links
- `external_links_count` - Number of external links
- `youtube_embeds_count` - Number of YouTube embeds

**Image Settings:**
- `image_source` - Primary: `openai`, `fal`, or `pexels` (DEPRECATED - use priority below)
- `image_provider_priority` - e.g., "openai,fal,pexels" (tries in order per image)
- `openai_model` - Optional: override default text model
- `openai_image_model` - Optional: override default image model

**Publishing:**
- `post_status` - `draft` or `publish`

#### B) Topics Sheet (per site)
Each site needs its own Google Sheet with a tab (e.g., "Topics").

**Required Columns:**
```
topic | status | locked_at | post_url | error | created_at | updated_at | categories | tags | skip
```

**User Input (minimum):**
- `topic` - The blog post topic/title idea
- `status` - Must be `QUEUED` for new posts
- `categories` - Optional: Comma-separated category names or IDs
- `tags` - Optional: Comma-separated tag names

**Auto-Managed by System:**
- `locked_at` - Timestamp when processing started
- `post_url` - URL of published post
- `error` - Error message if failed
- `created_at` - When row was added
- `updated_at` - Last update timestamp
- `skip` - Set to any value to skip this topic

**Example Row:**
```
How to Start a Blog in 2026 | QUEUED | | | | 2026-01-18 10:00:00 | | Blogging,WordPress | tutorial,beginners |
```

---

### ✅ 3. WordPress Setup

#### Generate Application Password:
1. WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Name: "n8n Autoblogger"
4. Click "Add New Application Password"
5. **COPY THE PASSWORD** (format: `xxxx xxxx xxxx xxxx`)
6. Use this in `wp_app_password` column (keep the spaces)

#### Required WordPress Plugins:
- **None required for Basic Auth**

#### Optional (for JWT Auth):
- **JWT Authentication for WP REST API** plugin
  - Only if using `auth_mode = jwt` in Site Registry

#### WordPress REST API Test:
Run this in PowerShell to test:
```powershell
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("YOUR_USERNAME:YOUR_APP_PASSWORD"))
$headers = @{
    Authorization = "Basic $base64"
}
Invoke-RestMethod -Uri "https://yoursite.com/wp-json/wp/v2/users/me" -Headers $headers
```

Should return your user info (not an error).

---

## 🔧 Common Issues & Fixes

### Issue 1: "Missing OpenAI API key"
**Cause:** `OPENAI_API_KEY` not set in n8n Variables
**Fix:** Settings → Variables → Add `OPENAI_API_KEY` with your key

### Issue 2: "WP auth sanity check failed"
**Causes:**
- Incorrect `wp_user` or `wp_app_password`
- Application Password not generated correctly
- WordPress REST API disabled
- SSL certificate issues

**Fix:**
1. Regenerate WordPress Application Password
2. Test with PowerShell command above
3. Ensure `base_url` uses `https://` (not `http://`)
4. Check WordPress → Settings → Permalinks (must NOT be "Plain")

### Issue 3: "topics_sheet_id" not found / Invalid sheet
**Cause:** Column name mismatch in Site Registry
**Fix:** 
- Ensure column is named exactly `topics_sheet_id` (NOT `topics_sheet_ID` or `topic_sheet_id`)
- Check that the value is the Google Sheet ID (long alphanumeric string)

### Issue 4: "Expected X image placeholders; found Y"
**Cause:** OpenAI didn't generate correct number of image placeholders
**Fix:**
- Verify `images_count` in Site Registry
- Check OpenAI model (`gpt-4o-mini` works better than older models)
- Ensure sufficient OpenAI credits
- May need to regenerate (system is strict to prevent partial posts)

### Issue 5: "Invalid image model" or image generation fails
**Cause:** `OPENAI_IMAGE_MODEL_DEFAULT` set to non-existent model
**Fix:**
- Change to `dall-e-3` or `dall-e-2`
- Remove the variable to use fallback providers (fal.ai, Pexels)

### Issue 6: Posts not being scheduled
**Causes:**
- `schedule_mode` not set correctly
- `last_posted_at` blocking re-runs
- No topics with `status = QUEUED`

**Fix:**
1. Check Site Registry `schedule_mode` = `minutes`, `hours`, `daily`, or `weekly`
2. Set appropriate `interval` value
3. Clear `last_posted_at` to test immediately
4. Verify Topics sheet has rows with `status = QUEUED`

### Issue 7: "Execute Publisher Workflow" fails
**Cause:** `PUBLISHER_ID` variable not set or incorrect
**Fix:**
1. Open "Publisher (Autoblogging Engine)" workflow
2. Copy workflow ID from URL (after `/workflow/`)
3. Settings → Variables → Set `PUBLISHER_ID` to that value

### Issue 8: Images not showing in WordPress
**Causes:**
- Image upload failed silently
- WordPress media permissions issue
- Featured image not set

**Fix:**
1. Check debug output in workflow execution
2. Verify WordPress uploads folder is writable
3. Test manual image upload via WordPress admin
4. Check `debug.images_uploaded` count in execution output

### Issue 9: Categories/Tags not being applied
**Cause:** Not an error - this is optional behavior
**Fix:**
- Add `categories` and `tags` columns to Topics sheet
- Fill with comma-separated values
- System will create categories/tags if they don't exist
- Can use category IDs (numeric) or names (text)

### Issue 10: Internal links not working
**Cause:** No existing published posts on the site
**Fix:**
- System needs existing posts to link to
- Publish at least 5-10 posts first
- Then internal linking will work automatically

---

## 🧪 Testing Your Setup

### Step-by-Step First Run:

1. **Test Master Scheduler manually:**
   - Open "Master Scheduler (Multi-site)" workflow
   - Click "Execute Workflow" button
   - Check execution log for errors

2. **Verify Schedule Gate:**
   - Should output only "due" sites
   - If empty, check `schedule_mode` and `last_posted_at`

3. **Test Publisher directly:**
   - Open "Publisher (Autoblogging Engine)" workflow
   - Manually inject test data:
```json
{
  "site_config": {
    "base_url": "https://yoursite.com",
    "wp_user": "admin",
    "wp_app_password": "xxxx xxxx xxxx xxxx",
    "tone": "professional",
    "min_words": 800,
    "max_words": 1200,
    "faq_count": 5,
    "images_count": 2,
    "internal_links_count": 2,
    "external_links_count": 2,
    "youtube_embeds_count": 0,
    "post_status": "draft"
  },
  "topicRow": {
    "topic": "The Benefits of Test-Driven Development"
  }
}
```
   - Click "Execute Workflow"
   - Check output for `ok: true` and `post_url`

4. **Verify WordPress post:**
   - Log into WordPress admin
   - Go to Posts → All Posts
   - Find your test post
   - Verify images, links, content quality

---

## 📊 Google Sheets Templates

### Site Registry Template
Download and fill: **Site_Registry_Template.xlsx**

Minimum columns needed:
```csv
site_name,base_url,wp_user,wp_app_password,topics_sheet_id,topics_sheet_tab_id,schedule_mode,interval,images_count,post_status
"My Blog","https://myblog.com","admin","xxxx xxxx xxxx xxxx","1a2b3c4d5e6f","Topics","minutes","30","2","draft"
```

### Topics Template
Download and fill: **Topics_Template.xlsx**

Minimum columns needed:
```csv
topic,status,locked_at,post_url,error,created_at,updated_at,categories,tags
"How to Start a Blog","QUEUED","","","","2026-01-18 10:00:00","","Blogging","tutorial,beginners"
```

---

## 🚀 Production Deployment Checklist

- [ ] All n8n Variables set correctly
- [ ] Google Sheets created with exact column names
- [ ] WordPress Application Passwords generated
- [ ] REST API test successful for each site
- [ ] Test run of Publisher workflow (draft mode)
- [ ] Verify post created in WordPress
- [ ] Images uploaded correctly
- [ ] Links working (internal/external)
- [ ] Categories and tags applied
- [ ] Schedule tested (set interval to 1-2 minutes for testing)
- [ ] Cleanup workflow tested (should reset stuck locks)
- [ ] Change `post_status` to `publish` when ready
- [ ] Set production schedule intervals
- [ ] Set up monitoring/notifications (Telegram/email)

---

## 🔍 Debug Output Analysis

Each successful Publisher execution returns:
```json
{
  "ok": true,
  "post_url": "https://...",
  "post_id": 123,
  "debug": {
    "serp_count": 10,
    "youtube_candidates_count": 5,
    "images_requested": 2,
    "images_uploaded": 2,
    "image_provider_breakdown": {
      "openai": 2,
      "fal": 0,
      "pexels": 0
    },
    "internal_links_inserted": 2,
    "external_links_inserted": 2,
    "youtube_embeds_inserted": 0
  }
}
```

**What to check:**
- `ok: true` - Success
- `images_uploaded` should equal `images_requested`
- `image_provider_breakdown` shows which provider was used
- Link counts show how many were actually inserted

---

## 🆘 Still Having Issues?

### Enable n8n Execution Logging:
1. Settings → Log Streaming → Enable
2. Run workflow
3. Check detailed logs for exact error messages

### Common Error Messages Decoded:

| Error Message | Meaning | Fix |
|--------------|---------|-----|
| "Missing topic" | topicRow.topic is empty | Check Topics sheet has `topic` column filled |
| "Missing site.base_url" | Site Registry missing URL | Add `base_url` column with https:// URL |
| "Basic auth requires wp_user and wp_app_password" | Credentials missing | Fill in WordPress auth columns |
| "OpenAI returned invalid JSON" | AI model issue | Try different model or check OpenAI credits |
| "WP media upload failed (RAW)" | WordPress upload issue | Check WP uploads folder permissions |

### Get More Help:
1. Check n8n workflow execution logs
2. Review Google Sheets for typos in column names
3. Test WordPress REST API manually
4. Verify all API keys are valid and funded

---

## 💡 Pro Tips

### Optimize Image Generation:
- Set `image_provider_priority` to "fal,openai,pexels" to save OpenAI costs
- Ensure FAL_API_KEY is set for faster image generation
- Use Pexels as final fallback (free stock photos)

### Speed Up Content Creation:
- Use `gpt-4o-mini` for cost-effective content
- Set `images_count` to 0 for text-only posts (faster)
- Disable external link research if not needed (set counts to 0)

### Multi-Site Management:
- Create one Topics sheet per site for organization
- Use different schedules per site (stagger posts)
- Group similar sites in separate Site Registry rows

### Error Recovery:
- Cleanup workflow runs hourly to reset stuck posts
- Failed posts stay marked as FAILED (won't retry automatically)
- Change status back to QUEUED to retry

---

## 📝 Example Working Configuration

**Site Registry (one row):**
```
site_name: Tech Blog
base_url: https://techblog.com
wp_user: admin
wp_app_password: AbCd EfGh IjKl MnOp
topics_sheet_id: 1A2B3C4D5E6F7G8H9I0J
topics_sheet_tab_id: Topics
schedule_mode: hours
interval: 6
timezone: America/New_York
tone: professional and informative
min_words: 1000
max_words: 1800
faq_count: 6
tables_mode: auto
charts_mode: auto
images_count: 3
internal_links_count: 3
external_links_count: 2
youtube_embeds_count: 1
image_provider_priority: fal,openai,pexels
post_status: draft
```

**Topics Sheet (example rows):**
```
topic: "How AI is Transforming Healthcare in 2026"
status: QUEUED
categories: AI,Healthcare
tags: artificial-intelligence,medical-tech,future

topic: "Top 10 Programming Languages to Learn"
status: QUEUED
categories: Programming
tags: coding,development,career
```

**n8n Variables:**
```
SITE_REGISTRY_SPREADSHEET_ID: 1A2B3C4D5E6F7G8H9I0J
SITE_REGISTRY_SHEET_ID: Site_Registry
PUBLISHER_ID: AbCdEfGh (your Publisher workflow ID)
OPENAI_API_KEY: sk-proj-...
OPENAI_MODEL_DEFAULT: gpt-4o-mini
OPENAI_IMAGE_MODEL_DEFAULT: dall-e-3
FAL_API_KEY: your-fal-key
PEXELS_API_KEY: your-pexels-key
IMAGE_PROVIDER_PRIORITY_DEFAULT: fal,openai,pexels
GOOGLE_CSE_API_KEY: your-cse-key
GOOGLE_CSE_CX: your-cx-id
YOUTUBE_API_KEY: your-youtube-key
PROCESSING_STUCK_THRESHOLD_MINUTES: 60
```

**Expected Result:**
- Every 6 hours (during working hours if window set)
- One post created as draft in WordPress
- 3 images from fal.ai (or fallback to OpenAI/Pexels)
- 3 internal links to existing posts
- 2 external links to authority sites
- 1 YouTube video embedded
- All contextually placed (no patterns)
- Topic marked DONE in Google Sheet
- Site Registry `last_posted_at` updated

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Master Scheduler runs every 10 minutes without errors
- ✅ Sites marked as "due" get processed
- ✅ Topics change from QUEUED → PROCESSING → DONE
- ✅ WordPress posts appear with complete content
- ✅ Images are uploaded and featured image is set
- ✅ Links are contextually placed in content
- ✅ No duplicate posts created
- ✅ Failed posts are marked FAILED with error details
- ✅ Stuck locks get cleaned up hourly

Happy autoblogging! 🚀
