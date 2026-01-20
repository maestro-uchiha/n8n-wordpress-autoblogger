# Multi-site WordPress Autoblogging (n8n v2.3.5)

This bundle contains **3 importable n8n workflows** + **Google Sheets templates** implementing your multi-site set-and-forget autoblogger.

## What changed in this update
- **Secrets stored in n8n Variables** (Option 1)
- **Per-site model control** via `openai_model` and `openai_image_model`
- **Image provider fallback chain per-image:** **OpenAI → fal.ai → Pexels**

---

## 1) Create n8n Variables (global)
In **n8n Cloud → Settings → Variables**, add:

Required:
- `SITE_REGISTRY_SPREADSHEET_ID`
- `SITE_REGISTRY_SHEET_NAME` (e.g. `Site_Registry`)
- `OPENAI_API_KEY`

Recommended defaults:
- `OPENAI_MODEL_DEFAULT` = `gpt-4o-mini`
- `OPENAI_IMAGE_MODEL_DEFAULT` = `gpt-image-1-mini`
- `IMAGE_PROVIDER_PRIORITY_DEFAULT` = `openai,fal,pexels`
- `PROCESSING_STUCK_THRESHOLD_MINUTES` = `60`

Search/embeds:
- `GOOGLE_CSE_API_KEY`
- `GOOGLE_CSE_CX`
- `YOUTUBE_API_KEY`

Image fallbacks:
- `FAL_API_KEY`
- `PEXELS_API_KEY`

Optional:
- `SPEEDYINDEX_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- SMTP vars if you wire email nodes

---

## 2) Google Sheets
### A) Global registry spreadsheet
Use `Site_Registry_Template.xlsx` to create your registry.
Only **non-secret** fields need to be filled per site. API key columns can be left blank (env vars are used).

### B) Per-site topics spreadsheet
Use `Topics_Template.xlsx` for each site. Minimum input: `topic` + `QUEUED`.

---

## 3) Import workflows
Import these JSON files:
- `workflow_1_master_scheduler.json`
- `workflow_2_publisher.json`
- `workflow_3_cleanup.json`

After import, set **Google Sheets credential** on the Google Sheets nodes.

---

## 4) Activate order
1) Activate **Publisher**
2) Activate **Cleanup**
3) Activate **Master Scheduler**

---

## Image fallback behavior
For each image placeholder ALT:
1) Try **OpenAI Images** (uses `OPENAI_API_KEY` + per-site `openai_image_model` or `OPENAI_IMAGE_MODEL_DEFAULT`)
2) If that fails, try **fal.ai** (uses `FAL_API_KEY`)
3) If that fails, try **Pexels** (uses `PEXELS_API_KEY`)

Per site you can override provider order by setting `image_provider_priority` (comma-separated), e.g. `openai,fal,pexels`.

---

## Notes
- No RankMath meta writing.
- No fact checking.
- No citations / Sources section.
- Contextual injection for internal/external/youtube to avoid patterns.
