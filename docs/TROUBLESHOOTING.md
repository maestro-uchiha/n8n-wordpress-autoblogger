# Troubleshooting Guide

Solutions to common issues with the n8n WordPress Autoblogger.

---

## Table of Contents

1. [Authentication Errors](#authentication-errors)
2. [Image Upload Issues](#image-upload-issues)
3. [Content Generation Problems](#content-generation-problems)
4. [Category/Tag Issues](#categorytag-issues)
5. [SEO Meta Not Saving](#seo-meta-not-saving)
6. [Workflow Not Running](#workflow-not-running)
7. [Google Sheets Errors](#google-sheets-errors)
8. [Debug Output Reference](#debug-output-reference)

---

## Authentication Errors

### "JWT authentication failed"

**Symptoms**: Workflow fails at WP_AUTH_CHECK step

**Solutions**:

1. **Check JWT Plugin Installation**
   - Ensure "JWT Authentication for WP REST API" is installed and activated
   - Visit `https://yoursite.com/wp-json/jwt-auth/v1/token` - should return method info

2. **Verify wp-config.php**
   ```php
   define('JWT_AUTH_SECRET_KEY', 'your-unique-secret-key');
   define('JWT_AUTH_CORS_ENABLE', true);
   ```

3. **Check .htaccess (Apache)**
   ```apache
   RewriteEngine on
   RewriteCond %{HTTP:Authorization} ^(.*)
   RewriteRule ^(.*) - [E=HTTP_AUTHORIZATION:%1]
   SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1
   ```

4. **For Nginx**, add to server block:
   ```nginx
   location / {
       try_files $uri $uri/ /index.php?$args;
   }
   fastcgi_param HTTP_AUTHORIZATION $http_authorization;
   ```

### "401 Unauthorized" with Basic Auth

**Solutions**:

1. Verify Application Password is correct (include spaces)
2. Check username is exact (case-sensitive)
3. Ensure user has `edit_posts` capability
4. Try regenerating the Application Password

### "403 Forbidden"

**Causes**:
- Security plugin blocking REST API
- Cloudflare/WAF blocking requests
- WordPress permissions issue

**Solutions**:

1. Whitelist n8n IPs in security plugins
2. Add Cloudflare bypass rule for `/wp-json/n8n/v1/*`
3. Check user role has required capabilities

---

## Image Upload Issues

### "Request failed with status code 500"

**Cause**: Large image files timeout or memory issues

**Solutions**:

1. Use `dall-e-2` instead of `dall-e-3` (smaller images)
2. Increase PHP memory limit:
   ```php
   // wp-config.php
   define('WP_MEMORY_LIMIT', '256M');
   ```
3. Use `fal,pexels` as first providers (URL-based, not base64)

### "rest_no_route" or 404 on image upload

**Cause**: n8n Autoblogger Helper plugin not installed

**Solution**: Install the WordPress plugin from `wordpress-plugin/n8n-autoblogger-helper.zip`

### Images Upload but Show Broken

**Causes**:
- MIME type mismatch
- Corrupted during transfer

**Solutions**:

1. Check the image URL in WordPress Media Library
2. Verify file exists on server
3. Check `debug.image_errors` in output for details

### Cloudflare Blocking Uploads

**Symptoms**: 413 or 524 errors on large images

**Solutions**:

1. Use sideload (URL) method instead of base64
2. Set `image_provider_priority: fal,pexels` (these use URLs)
3. Add Cloudflare page rule to bypass for `/wp-json/*`

---

## Content Generation Problems

### "Empty response from OpenAI"

**Solutions**:

1. Check API key is valid
2. Verify account has credits
3. Try a simpler topic
4. Check OpenAI status page

### Content Missing Images

**Cause**: AI didn't include image placeholders

**Note**: This is self-correcting - the system removes unfilled placeholders. If you consistently need images:

1. Reduce `images_count` to 1-2
2. Use a more capable model (`gpt-4o`)

### Links Appearing in Headings

**This was fixed in v2.28**. If still happening:

1. Re-import the latest Publisher workflow
2. Verify you're on v2.28 or later (check `versionId`)

### Tables Not Generated

**Solutions**:

1. The AI prompt explicitly requests tables
2. More technical topics tend to include tables
3. Try adding "comparison" or "vs" to your topic

---

## Category/Tag Issues

### "403" on Category Creation

**Cause**: WordPress REST API blocks category creation for some user roles

**Solution**: 
1. Ensure WordPress plugin v1.2+ is installed
2. The plugin provides `/n8n/v1/create-category` endpoint that bypasses this

### Categories Not Being Assigned

**Check**:

1. Category names in Topics sheet are spelled correctly
2. Look at `debug.categories_found` in output
3. System does fuzzy matching, but exact names work best

### Auto-Created Categories Have Wrong Slug

The system auto-generates slugs from category names. To control slugs:

1. Create the category manually in WordPress first
2. The system will find and use the existing category

---

## SEO Meta Not Saving

### Yoast/RankMath Fields Empty

**Cause**: WordPress REST API doesn't allow unregistered meta fields

**Solution**: 
1. Install WordPress plugin v1.1+ (has `/n8n/v1/update-seo-meta`)
2. Check `debug.seo_meta_updated` shows `true` values
3. Check `debug.seo_plugins` shows your plugin detected

### Focus Keyphrase Not Showing

**Verify**:

1. RankMath or Yoast is active
2. Check post meta in database:
   - RankMath: `rank_math_focus_keyword`
   - Yoast: `_yoast_wpseo_focuskw`

---

## Workflow Not Running

### Master Scheduler Not Triggering

**Check**:

1. Workflow is **Active** (toggle is ON)
2. Schedule trigger is configured correctly
3. n8n instance is running

### Topics Stuck in PROCESSING

**Cause**: Previous execution crashed

**Solution**: Run the **Cleanup (Stuck Locks)** workflow to reset stuck topics

### No PENDING Topics Found

**Check**:

1. Topics sheet has correct columns
2. Status column contains exactly `PENDING` (not "pending" or "Pending")
3. Sheet GID in Sites config matches actual sheet

---

## Google Sheets Errors

### "Requested entity was not found"

**Causes**:
- Wrong Spreadsheet ID
- Wrong Sheet GID
- Sheet was deleted

**Solutions**:

1. Double-check the Spreadsheet ID from URL
2. Verify GID from URL (`#gid=123456`)
3. Ensure n8n has access to the spreadsheet

### "The caller does not have permission"

**Solutions**:

1. Share the spreadsheet with the n8n Google account
2. Or use a Service Account with proper permissions
3. Re-authenticate Google Sheets in n8n credentials

---

## Debug Output Reference

The `debug` object in workflow output contains valuable troubleshooting info:

```json
{
  "debug": {
    "serp_count": 10,              // External links available
    "youtube_candidates_count": 5, // Videos found
    "images_requested": 1,         // How many images wanted
    "images_uploaded": 1,          // How many succeeded
    "images_by_provider": {        // Which provider worked
      "fal": 1
    },
    "internal_links_requested": 3,
    "internal_links_inserted": 2,  // Actually inserted
    "external_links_requested": 3,
    "external_links_inserted": 3,
    "youtube_embeds_requested": 1,
    "youtube_embeds_inserted": 1,
    "categories_requested": ["Tech"],
    "categories_found": [          // Match results
      { "requested": "Tech", "matched": "Technology", "id": 5 }
    ],
    "seo_meta_updated": {          // SEO success
      "rankmath_focus_keyword": true,
      "rankmath_description": true
    },
    "seo_plugins": {               // Detected plugins
      "yoast": false,
      "rankmath": true
    },
    "image_errors": [],            // Image issues
    "wp_errors": []                // WordPress API errors
  }
}
```

### Common Debug Patterns

**Images failed**:
```json
"image_errors": [
  { "provider": "openai", "error": "Request failed with status code 500" },
  { "step": "TRYING_N8N_PLUGIN_SIDELOAD", "url": "https://..." },
  { "step": "SIDELOAD_SUCCESS", "id": 123 }
]
```
↑ OpenAI failed, but fal.ai sideload worked

**No internal links inserted**:
```json
"internal_links_requested": 3,
"internal_links_inserted": 0
```
↑ No matching published posts found on the site

**Category created**:
```json
"categories_found": [
  { "requested": "New Category", "created": true, "id": 42 }
]
```

---

## Getting Help

If you're still stuck:

1. **Check the execution log** in n8n for detailed step-by-step info
2. **Review `debug` and `wp_errors`** in the output
3. **Test components individually**:
   - Test WordPress auth: `GET /wp-json/wp/v2/users/me`
   - Test plugin: `POST /wp-json/n8n/v1/create-category`
4. **Open a GitHub issue** with:
   - Error message
   - Debug output (redact sensitive data)
   - WordPress/n8n versions
