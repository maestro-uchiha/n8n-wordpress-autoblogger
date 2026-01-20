# Google Sheets Setup Guide

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

5. **Or manually create columns (Row 1):**
   ```
   A: site_id
   B: site_name
   C: base_url
   D: auth_mode
   E: jwt_user
   F: jwt_password
   G: jwt_token
   H: wp_user
   I: wp_app_password
   J: topics_gid
   K: post_interval_minutes
   L: last_posted_at
   M: enabled
   N: post_status
   O: tone
   P: min_words
   Q: max_words
   R: faq_count
   S: images_count
   T: internal_links_count
   U: external_links_count
   V: youtube_embeds_count
   W: image_provider_priority
   ```

### 3. Create Topics Sheets (One Per Site)

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

5. **Or manually create columns (Row 1):**
   ```
   A: topic
   B: status
   C: locked_at
   D: post_url
   E: error
   F: tags
   G: categories
   H: created_at
   I: updated_at
   ```

6. **Put the gid number** in the `topics_gid` column of Site_Registry

### 4. Repeat for Each Site

For each WordPress site you want to automate:
1. Create a new Topics sheet tab
2. Get its gid
3. Add a row in Site_Registry with all the config

---

## Column Reference

### Site_Registry Columns

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `site_id` | ✅ | Unique identifier | `site_001` |
| `site_name` | ✅ | Display name | `My Tech Blog` |
| `base_url` | ✅ | WordPress URL (no trailing /) | `https://myblog.com` |
| `auth_mode` | ✅ | `jwt` or `basic` | `jwt` |
| `jwt_user` | If jwt | JWT username | `admin` |
| `jwt_password` | If jwt | JWT password | `secretpass123` |
| `jwt_token` | Optional | Cached JWT token | (auto-managed) |
| `wp_user` | If basic | WordPress username | `editor` |
| `wp_app_password` | If basic | Application password | `xxxx xxxx xxxx xxxx` |
| `topics_gid` | ✅ | **Numeric gid** of topics sheet | `414510277` |
| `post_interval_minutes` | ✅ | Minutes between posts | `120` |
| `last_posted_at` | Auto | Last post timestamp | (auto-updated) |
| `enabled` | ✅ | `TRUE` or `FALSE` | `TRUE` |
| `post_status` | ✅ | `publish` or `draft` | `publish` |
| `tone` | Optional | Writing style | `informative and engaging` |
| `min_words` | Optional | Min article length | `1500` |
| `max_words` | Optional | Max article length | `2500` |
| `faq_count` | Optional | Number of FAQs | `5` |
| `images_count` | Optional | Images to generate | `2` |
| `internal_links_count` | Optional | Internal links to add | `3` |
| `external_links_count` | Optional | External links (CSE) | `5` |
| `youtube_embeds_count` | Optional | YouTube videos | `1` |
| `image_provider_priority` | Optional | Fallback order | `openai,fal,pexels` |

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
| `created_at` | Optional | When added | `2026-01-19T00:00:00Z` |
| `updated_at` | Auto | Last update | (auto-updated) |

---

## Example Setup

### Your Spreadsheet Structure:

```
📊 Autoblogger - Site Registry
│
├── Tab 1: Site_Registry (gid=0)
│   └── Row 2: site_001, My Tech Blog, https://tech.com, jwt, ..., topics_gid=123456789
│   └── Row 3: site_002, Health Blog, https://health.com, basic, ..., topics_gid=987654321
│
├── Tab 2: Topics_TechBlog (gid=123456789)
│   └── Row 2: "Best AI Tools 2026", QUEUED, ...
│   └── Row 3: "Remote Work Tips", QUEUED, ...
│
└── Tab 3: Topics_HealthBlog (gid=987654321)
    └── Row 2: "Healthy Breakfast Ideas", QUEUED, ...
    └── Row 3: "Morning Yoga Routine", QUEUED, ...
```

### n8n Variables to Set:

```
SITE_REGISTRY_SPREADSHEET_ID = 1ABC123XYZ... (from spreadsheet URL)
SITE_REGISTRY_GID = 0 (or whatever gid Site_Registry has)
```

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

Done! Now fill in your actual values.
