# ⚠️ Critical Fixes & Known Issues

## 🔴 CRITICAL: Must-Fix Before Running

### 1. OpenAI Image Model Name
**Issue:** Invalid default image model in Publisher workflow
**Current:** `gpt-image-1-mini` (DOES NOT EXIST)
**Fix:** Change to `dall-e-3` or `dall-e-2`

**Location:** n8n Variables
- Variable: `OPENAI_IMAGE_MODEL_DEFAULT`
- Change to: `dall-e-3`

**Alternative:** Use fal.ai or Pexels as primary image provider:
- Set `IMAGE_PROVIDER_PRIORITY_DEFAULT` to `fal,pexels,openai`

---

### 2. Sheet Column Name Consistency
**Issue:** Master Scheduler uses both `topics_sheet_tab_id` and `topics_tab_name`

**Your Google Sheets MUST have:**
- Column named: `topics_sheet_tab_id` (this is what the workflow uses)
- NOT `topics_tab_name` (this is deprecated)

**Workflow expects:**
```javascript
{{ $json.site_config.topics_sheet_tab_id }}
```

**Fix:** Rename your column header in Site Registry from `topics_tab_name` to `topics_sheet_tab_id`

---

### 3. Missing PUBLISHER_ID Variable
**Issue:** Master Scheduler can't call Publisher workflow
**Error:** "Workflow with ID ... not found"

**Fix:**
1. Open "Publisher (Autoblogging Engine)" workflow
2. Copy the workflow ID from the URL: `https://app.n8n.cloud/workflow/COPY_THIS_ID`
3. Go to Settings → Variables
4. Add new variable:
   - Name: `PUBLISHER_ID`
   - Value: `COPY_THIS_ID`

---

### 4. SITE_REGISTRY_SHEET_ID vs SITE_REGISTRY_SHEET_NAME
**Issue:** Variable name mismatch in workflows

**Master Scheduler expects:**
```javascript
{{ $vars.SITE_REGISTRY_SHEET_ID }}
```

**BUT your README says:**
```
SITE_REGISTRY_SHEET_NAME
```

**Fix:** In n8n Variables, create:
- Name: `SITE_REGISTRY_SHEET_ID`
- Value: `Site_Registry` (the exact tab name in your Google Sheet)

**NOT:** `SITE_REGISTRY_SHEET_NAME`

---

## 🟡 Important: Recommended Fixes

### 5. Google Sheets Schema Mismatch
**Issue:** Publisher expects certain fields that might not exist in your sheet

**Required columns in Topics sheet:**
- `topic` ✅
- `status` ✅
- `locked_at` ✅
- `post_url` ✅
- `error` ✅
- `created_at` ✅
- `updated_at` ✅
- `categories` ⚠️ (Add this - it's in the blueprint)
- `tags` ⚠️ (Add this - it's in the blueprint)
- `skip` ⚠️ (Add this - allows skipping topics)

**Optional but useful:**
- `site` (for multi-tenant Topics sheets)

---

### 6. WordPress Application Password Format
**Issue:** Spaces in application password might cause issues

**WordPress generates:** `AbCd EfGh IjKl MnOp` (with spaces)
**Can cause:** Parsing errors in some scenarios

**Fix:** Keep the spaces as-is, BUT test your auth with this PowerShell script:

```powershell
# Test WordPress Auth
$username = "your_wp_user"
$appPassword = "AbCd EfGh IjKl MnOp"  # WITH spaces
$baseUrl = "https://yoursite.com"

$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${username}:${appPassword}"))
$headers = @{
    Authorization = "Basic $base64"
    "User-Agent" = "n8n-test/1.0"
}

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/wp-json/wp/v2/users/me" -Headers $headers -Method Get
    Write-Host "✅ Auth Success! User ID: $($response.id)" -ForegroundColor Green
} catch {
    Write-Host "❌ Auth Failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

### 7. Schedule Gate Timezone Handling
**Issue:** Default timezone is `Africa/Douala` (might not be yours)

**Fix:** In Site Registry, add `timezone` column and set to your timezone:
- Examples: `America/New_York`, `Europe/London`, `Asia/Tokyo`
- Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

**Or:** Update default in Schedule Gate code (line ~70):
```javascript
const tz = normStr(site.timezone) || 'YOUR_TIMEZONE_HERE';
```

---

### 8. Image Alt Text Domain Suffix
**Issue:** Hard-coded domain extraction might fail on complex URLs

**Current behavior:**
- Extracts domain from `base_url`
- Appends to alt text: `"Original Alt | domain.com"`

**Potential issue:** If `base_url` has ports or subdomains
- Example: `https://blog.example.com:8080` → `blog.example.com`

**Fix:** Verify your `base_url` is clean:
- ✅ `https://example.com`
- ✅ `https://blog.example.com`
- ❌ `https://example.com/` (remove trailing slash)
- ❌ `http://example.com` (use HTTPS)

---

## 🟢 Optional: Performance Optimizations

### 9. Reduce OpenAI Costs
**Current:** Uses OpenAI for text + images
**Cost:** ~$0.10-0.30 per post with images

**Optimization:**
1. Use fal.ai for images (faster + cheaper)
   - Set `FAL_API_KEY` in Variables
   - Set `IMAGE_PROVIDER_PRIORITY_DEFAULT` to `fal,pexels,openai`

2. Use cheaper text model:
   - Change `OPENAI_MODEL_DEFAULT` from `gpt-4o-mini` to `gpt-3.5-turbo`
   - Trade-off: Lower quality content

---

### 10. Parallel Processing
**Current:** Master Scheduler processes sites sequentially
**Issue:** If you have 10 sites, each waits for the previous

**Optimization (Advanced):**
- Modify Master Scheduler to use parallel execution
- Add multiple "Execute Publisher Workflow" nodes
- Use Switch/Router to distribute load

**OR:** Run multiple instances of Master Scheduler with different site filters

---

## 🔧 Quick Fix Script for Google Sheets

### Update Column Names in Site Registry
If you have old column names, use this Google Apps Script:

```javascript
function fixColumnNames() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Site_Registry');
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  var fixes = {
    'topics_tab_name': 'topics_sheet_tab_id',
    'google_cse_api_key': '', // Remove (use n8n Variables)
    'google_cse_cx': '', // Remove
    'youtube_api_key': '', // Remove
    'speedyindex_api_key': '', // Remove
  };
  
  for (var i = 0; i < headers.length; i++) {
    if (fixes[headers[i]]) {
      if (fixes[headers[i]] === '') {
        // Delete column
        sheet.deleteColumn(i + 1);
        Logger.log('Deleted column: ' + headers[i]);
      } else {
        // Rename column
        sheet.getRange(1, i + 1).setValue(fixes[headers[i]]);
        Logger.log('Renamed: ' + headers[i] + ' -> ' + fixes[headers[i]]);
      }
    }
  }
}
```

Run this in Google Sheets: Extensions → Apps Script → Paste → Run

---

## 🧪 Test Suite Before Going Live

### Pre-Flight Checklist

Run this in order:

1. **Test n8n Variables:**
```javascript
// In a Code node, test variable access
return [{
  json: {
    spreadsheet_id: $vars.SITE_REGISTRY_SPREADSHEET_ID,
    sheet_id: $vars.SITE_REGISTRY_SHEET_ID,
    publisher_id: $vars.PUBLISHER_ID,
    openai_key_set: !!$vars.OPENAI_API_KEY,
    openai_model: $vars.OPENAI_MODEL_DEFAULT,
    image_model: $vars.OPENAI_IMAGE_MODEL_DEFAULT,
  }
}];
```
Expected output: All fields filled, `openai_key_set: true`

2. **Test Google Sheets Read:**
- Manually trigger "Read Site Registry" node
- Should return rows from your sheet
- Verify column names match exactly

3. **Test WordPress Auth:**
- Use PowerShell script above
- Should return user object, not 401/403 error

4. **Test Publisher with Mock Data:**
- Open Publisher workflow
- Click "Execute Workflow"
- Manually input test JSON (see SETUP_AND_DEBUG_GUIDE.md)
- Should create draft post in WordPress

5. **Test Full Flow (Draft Mode):**
- Set `post_status` to `draft` in Site Registry
- Create 1 topic with `status = QUEUED`
- Clear `last_posted_at` in Site Registry
- Manually run Master Scheduler
- Check WordPress for draft post

6. **Verify Cleanup:**
- Manually set a topic to `status = PROCESSING` with old `locked_at`
- Run Cleanup workflow
- Should reset to FAILED or QUEUED

---

## 🚨 Emergency Rollback

If things go wrong:

### Stop All Workflows
1. Master Scheduler → Disable
2. Cleanup → Disable
3. Publisher → Leave enabled (doesn't auto-run)

### Reset Topics Sheet
```sql
-- In Google Sheets, use Filter/Query to reset all PROCESSING to QUEUED
=ARRAYFORMULA(IF(B2:B="PROCESSING", "QUEUED", B2:B))
```

### Clear Locks
```sql
-- Clear all locked_at timestamps
=ARRAYFORMULA(IF(C2:C<>"", "", C2:C))
```

### Reset Site Registry
```sql
-- Clear last_posted_at to force immediate re-run
=ARRAYFORMULA("")
```

---

## 📞 Support Resources

### n8n Community Forum
https://community.n8n.io/

### WordPress REST API Docs
https://developer.wordpress.org/rest-api/

### OpenAI API Docs
https://platform.openai.com/docs/api-reference

### Google Sheets API
https://developers.google.com/sheets/api

---

## ✅ Verification After Fixes

After applying all critical fixes, you should see:

1. **n8n Variables** (Settings → Variables):
   - ✅ All required variables present
   - ✅ No typos in variable names
   - ✅ `PUBLISHER_ID` points to correct workflow

2. **Google Sheets**:
   - ✅ Site Registry has `topics_sheet_tab_id` column
   - ✅ Topics sheet has `categories` and `tags` columns
   - ✅ At least one site row filled out
   - ✅ At least one topic with `status = QUEUED`

3. **WordPress**:
   - ✅ Application Password generated
   - ✅ REST API accessible (test with PowerShell)
   - ✅ Permalinks NOT set to "Plain"

4. **Test Run**:
   - ✅ Publisher creates draft post successfully
   - ✅ Master Scheduler finds due sites
   - ✅ Post appears in WordPress with images
   - ✅ Topics sheet updates to DONE
   - ✅ Site Registry `last_posted_at` updated

---

## 🎯 Most Common Fix Needed

Based on the blueprint and your current setup, the #1 issue is likely:

### ❌ Wrong: `SITE_REGISTRY_SHEET_NAME`
### ✅ Right: `SITE_REGISTRY_SHEET_ID`

Change this ONE variable and 80% of issues will be resolved.

---

Good luck! 🚀
