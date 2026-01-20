# Google Sheets Templates for n8n Autoblogger

## 📊 Site Registry Template

### How to Use:
1. Create a new Google Sheet
2. Name one tab: **Site_Registry** (exact name, case-sensitive)
3. Copy these column headers into Row 1
4. Fill in your site data starting from Row 2

### Column Headers (Row 1):
```
site_name | base_url | wp_user | wp_app_password | topics_sheet_id | topics_sheet_tab_id | schedule_mode | interval | daily_time | weekly_day | window_start | window_end | timezone | last_posted_at | tone | min_words | max_words | faq_count | tables_mode | charts_mode | images_count | internal_links_count | external_links_count | youtube_embeds_count | image_provider_priority | openai_model | openai_image_model | post_status | auth_mode
```

### Example Data (Row 2):
```
Tech Blog | https://techblog.com | admin | AbCd EfGh IjKl MnOp | 1A2B3C4D5E6F7G8H | Topics | hours | 6 | 09:00 | | 08:00 | 18:00 | America/New_York | | professional and informative | 1000 | 1800 | 6 | auto | auto | 3 | 3 | 2 | 1 | fal,openai,pexels | gpt-4o-mini | dall-e-3 | draft | basic
```

### Minimal Example (Row 2):
```
My Blog | https://myblog.com | admin | AbCd EfGh IjKl MnOp | 1A2B3C4D5E6F7G8H | Topics | minutes | 30 | | | | | | | | | | | | | 2 | 0 | 0 | 0 | | | | draft |
```

---

## 📋 Topics Sheet Template

### How to Use:
1. Create a new Google Sheet (separate from Site Registry)
2. Name one tab: **Topics** (or whatever you set in `topics_sheet_tab_id`)
3. Copy these column headers into Row 1
4. Fill in your topics starting from Row 2

### Column Headers (Row 1):
```
topic | status | locked_at | post_url | error | created_at | updated_at | categories | tags | skip
```

### Example Data (Row 2):
```
How to Start a Blog in 2026 | QUEUED | | | | 2026-01-18 10:00:00 | | Blogging,WordPress | tutorial,beginners,guide |
```

### Minimal Example (Row 2):
```
The Ultimate Guide to SEO | QUEUED | | | | | | | |
```

### Multiple Topics (Rows 2-6):
```
How AI is Changing Healthcare | QUEUED | | | | 2026-01-18 09:00:00 | | AI,Healthcare | artificial-intelligence,medical |
Top 10 Programming Languages | QUEUED | | | | 2026-01-18 09:15:00 | | Programming | coding,development |
Benefits of Cloud Computing | QUEUED | | | | 2026-01-18 09:30:00 | | Technology | cloud,infrastructure |
Digital Marketing Trends 2026 | QUEUED | | | | 2026-01-18 09:45:00 | | Marketing | digital-marketing,trends |
Best Practices for Remote Work | QUEUED | | | | 2026-01-18 10:00:00 | | Business | remote-work,productivity |
```

---

## 🎨 Google Sheets Formatting Tips

### Site Registry Sheet:
1. **Freeze Row 1:** View → Freeze → 1 row
2. **Color-code columns:**
   - Required (A-F): Light blue background
   - Scheduling (G-N): Light green background
   - Content (O-T): Light yellow background
   - Features (U-X): Light orange background
   - Advanced (Y-AB): Light gray background
3. **Data Validation:**
   - `schedule_mode`: Dropdown → minutes, hours, daily, weekly
   - `post_status`: Dropdown → draft, publish
   - `auth_mode`: Dropdown → basic, jwt

### Topics Sheet:
1. **Freeze Row 1:** View → Freeze → 1 row
2. **Color-code status:**
   - QUEUED: White background
   - PROCESSING: Yellow background
   - DONE: Green background
   - FAILED: Red background
3. **Conditional Formatting:**
   - Rule: `=B2="PROCESSING"` → Yellow
   - Rule: `=B2="DONE"` → Light green
   - Rule: `=B2="FAILED"` → Light red
   - Rule: `=B2="QUEUED"` → White

---

## 📥 CSV Import Format

### Site Registry CSV:
```csv
site_name,base_url,wp_user,wp_app_password,topics_sheet_id,topics_sheet_tab_id,schedule_mode,interval,images_count,post_status
"Tech Blog","https://techblog.com","admin","AbCd EfGh IjKl MnOp","1A2B3C4D5E6F","Topics","hours","6","3","draft"
"Marketing Hub","https://marketinghub.com","admin","XyZ1 2345 6789 0aBc","2B3C4D5E6F7G","Topics","daily","1","2","draft"
```

### Topics CSV:
```csv
topic,status,locked_at,post_url,error,created_at,updated_at,categories,tags,skip
"How to Start a Blog in 2026","QUEUED","","","","2026-01-18 10:00:00","","Blogging,WordPress","tutorial,beginners",""
"Top 10 SEO Tools","QUEUED","","","","2026-01-18 10:15:00","","SEO","tools,optimization",""
```

---

## 🔗 Getting Google Sheet IDs

### For SITE_REGISTRY_SPREADSHEET_ID:
1. Open your Site Registry Google Sheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit`
3. Copy the long alphanumeric string
4. Example: `1A2B3C4D5E6F7G8H9I0JK1L2M3N4O5P6Q7R8S9T0`

### For topics_sheet_id (per site):
1. Open the Topics Google Sheet for that site
2. Copy the ID from the URL (same method as above)
3. Paste into Site Registry under `topics_sheet_id` column

### For topics_sheet_tab_id:
1. This is NOT an ID - it's the **tab name**
2. Look at the bottom of your Google Sheet
3. Default is usually "Sheet1"
4. Rename to "Topics" for clarity
5. Put "Topics" in the `topics_sheet_tab_id` column

---

## 🧮 Google Sheets Formulas (Helper Columns)

### Auto-Generate Timestamps:
Add this formula to `created_at` column (if empty):
```
=IF(A2<>"", IF(F2="", NOW(), F2), "")
```

### Auto-Update `updated_at`:
```
=IF(A2<>"", NOW(), "")
```

### Count Queued Topics:
```
=COUNTIF(B:B, "QUEUED")
```

### Count Failed Topics:
```
=COUNTIF(B:B, "FAILED")
```

### Posts Published Today:
```
=COUNTIFS(B:B, "DONE", G:G, ">="&TODAY())
```

---

## 🎯 Quick Setup Guide

### Step 1: Create Site Registry
1. New Google Sheet → Name it "n8n Autoblogger - Registry"
2. Rename "Sheet1" tab to "Site_Registry"
3. Copy column headers from template above
4. Add your first site row
5. Copy the spreadsheet ID from URL

### Step 2: Create Topics Sheet(s)
1. New Google Sheet → Name it "Topics - [Your Site Name]"
2. Rename "Sheet1" tab to "Topics"
3. Copy column headers from template above
4. Add 5-10 topic rows with `status = QUEUED`
5. Copy the spreadsheet ID from URL

### Step 3: Link Them
1. In Site Registry, paste Topics spreadsheet ID into `topics_sheet_id`
2. In Site Registry, put "Topics" in `topics_sheet_tab_id`

### Step 4: Share with n8n
1. Both sheets → Share → Add email
2. Use your Google account connected to n8n
3. Give "Editor" permissions

---

## 📊 Advanced: Multi-Site Setup

### Option 1: One Topics Sheet Per Site (Recommended)
- **Pro:** Clean separation, easier management
- **Con:** More sheets to manage
- **Setup:**
  - Create separate Topics sheet for each site
  - Each Site Registry row points to different `topics_sheet_id`

### Option 2: One Topics Sheet for All Sites
- **Pro:** Single sheet to manage
- **Con:** Need to filter by site
- **Setup:**
  - Add `site` column to Topics sheet
  - Filter by site name when reading
  - Update Master Scheduler to filter topics by site

Example multi-site Topics sheet:
```csv
site,topic,status,locked_at,post_url,error,created_at,updated_at,categories,tags
"techblog.com","AI in Healthcare","QUEUED","","","","2026-01-18","","AI,Health","ai,healthcare"
"marketinghub.com","SEO Trends 2026","QUEUED","","","","2026-01-18","","SEO","seo,trends"
```

---

## 🛡️ Data Validation Rules

### In Site Registry:

**schedule_mode** (Column G):
- Data validation → List from a range
- Items: `minutes,hours,daily,weekly`

**interval** (Column H):
- Data validation → Number
- Min: 1, Max: 1440

**post_status** (Column AB):
- Data validation → List from a range
- Items: `draft,publish`

**images_count** (Column U):
- Data validation → Number
- Min: 0, Max: 10

### In Topics Sheet:

**status** (Column B):
- Data validation → List from a range
- Items: `QUEUED,PROCESSING,DONE,FAILED`

**skip** (Column J):
- Data validation → Checkbox

---

## 📱 Mobile-Friendly View

For managing on mobile:
1. Google Sheets app → Open your sheet
2. Freeze first row and first column
3. Hide columns you don't need to edit:
   - `locked_at`, `post_url`, `error`, `updated_at`
4. Focus on: `topic`, `status`, `categories`, `tags`

---

## 💾 Backup Strategy

### Auto-Backup with Google Sheets:
1. Tools → Version History → See version history
2. Name important versions before major changes

### Export Backups:
1. File → Download → CSV
2. Save weekly backups locally
3. Name format: `site_registry_2026-01-18.csv`

### Duplicate Before Bulk Changes:
1. Right-click sheet tab → Duplicate
2. Rename to "Site_Registry_BACKUP"
3. Hide the backup tab

---

## 🚀 Ready-to-Use Templates

### 1. Personal Blog (1 site)
**Site Registry:**
```
site_name,base_url,wp_user,wp_app_password,topics_sheet_id,topics_sheet_tab_id,schedule_mode,interval,images_count,post_status
"Personal Blog","https://myblog.com","admin","YOUR_APP_PASSWORD","YOUR_TOPICS_SHEET_ID","Topics","daily","1","2","draft"
```

**Topics:**
```
topic,status
"My Journey into Web Development","QUEUED"
"Top 5 Productivity Apps I Use","QUEUED"
"How I Built My First Website","QUEUED"
```

### 2. Multi-Niche Network (5 sites)
**Site Registry:**
```
site_name,base_url,topics_sheet_id,schedule_mode,interval
"Tech Blog","https://techblog.com","ID1","hours","6"
"Health Blog","https://healthblog.com","ID2","hours","8"
"Finance Blog","https://financeblog.com","ID3","daily","1"
"Travel Blog","https://travelblog.com","ID4","hours","12"
"Food Blog","https://foodblog.com","ID5","daily","1"
```

### 3. Authority Site (1 site, heavy content)
**Site Registry:**
```
site_name,base_url,min_words,max_words,images_count,internal_links_count,external_links_count,youtube_embeds_count,schedule_mode,interval
"Authority Tech","https://authoritytech.com","2000","3000","5","5","3","2","weekly","1"
```

---

## ✅ Verification Checklist

Before running your workflows, verify:

- [ ] Site Registry tab named exactly "Site_Registry"
- [ ] Topics tab named exactly "Topics" (or match `topics_sheet_tab_id`)
- [ ] All required columns present (no typos)
- [ ] At least one site row filled completely
- [ ] At least one topic with `status = QUEUED`
- [ ] Google Sheet shared with your n8n Google account
- [ ] `topics_sheet_id` is valid Google Sheet ID (not URL)
- [ ] `base_url` includes `https://` (no trailing slash)
- [ ] `wp_app_password` copied from WordPress (with spaces)
- [ ] Spreadsheet ID copied to n8n Variables

---

Happy blogging! 📝
