/**
 * AUTOBLOGGER PUBLISHER ENGINE v2.30
 * 
 * v2.30 Changes:
 * - SEO: New plugin endpoint /n8n/v1/update-seo-meta for direct meta updates
 * - SEO: Shows which SEO plugins are detected (Yoast/RankMath)
 * - SEO: Uses update_post_meta() directly (bypasses REST API schema restrictions)
 * 
 * v2.29 Changes:
 * - FIX: Removed JSON-LD script injection (WordPress blocks script tags)
 */

function parseInput(json) {
  let site = json.site_config || json.site || json.siteConfig || {};
  let topicRow = json.topicRow || json.topic_row || json.row || {};
  let globals = json.globals || {};
  if (!site.base_url && json.base_url) site = json;
  let topic = topicRow.topic || topicRow.keyword || json.topic || json.keyword || '';
  return { site, topicRow, globals, topic };
}

const input = $input.first().json;
const { site, topicRow, globals, topic } = parseInput(input);

const executionLog = [];
const debug = {
  serp_count: 0,
  youtube_candidates_count: 0,
  images_requested: 0,
  images_uploaded: 0,
  images_by_provider: {},
  internal_links_requested: 0,
  internal_links_inserted: 0,
  external_links_requested: 0,
  external_links_inserted: 0,
  youtube_embeds_requested: 0,
  youtube_embeds_inserted: 0,
  categories_requested: [],
  categories_found: [],
  notifications: { speedyindex: false, telegram: false, email: false },
  seo_meta_updated: false,
  seo_plugins: {},
  image_errors: [],
  wp_errors: []
};
let currentStep = '';

if (!topic) return [{ json: { ok: false, error: 'Missing topic', debug: { input } } }];
if (!site.base_url) return [{ json: { ok: false, error: 'Missing site base_url', debug: { site, input } } }];
if (!globals.OPENAI_API_KEY) return [{ json: { ok: false, error: 'CRITICAL: OPENAI_API_KEY is missing', site, topicRow } }];

// Helper to parse boolean from various formats
function parseBool(val, defaultVal = false) {
  if (val === undefined || val === null || val === '') return defaultVal;
  if (typeof val === 'boolean') return val;
  if (typeof val === 'string') {
    const lower = val.toLowerCase().trim();
    if (lower === 'true' || lower === 'yes' || lower === '1') return true;
    if (lower === 'false' || lower === 'no' || lower === '0') return false;
  }
  return defaultVal;
}

function detectEmailProvider(globals) {
  if (globals.EMAIL_PROVIDER) return globals.EMAIL_PROVIDER.toLowerCase();
  if (globals.RESEND_API_KEY) return 'resend';
  if (globals.SENDGRID_API_KEY) return 'sendgrid';
  if (globals.MAILGUN_API_KEY && globals.MAILGUN_DOMAIN) return 'mailgun';
  if (globals.SMTP2GO_API_KEY) return 'smtp2go';
  return null;
}

const config = {
  baseUrl: site.base_url.replace(/\/$/, ''),
  authMode: (site.auth_mode || 'jwt').toLowerCase(),
  wpUser: site.wp_user || site.jwt_user || '',
  wpPassword: site.wp_app_password || '',
  jwtUser: site.jwt_user || '',
  jwtPassword: site.jwt_password || '',
  jwtToken: site.jwt_token || '',
  jwtTokenEndpoint: site.jwt_token_endpoint || null,
  postStatus: site.post_status || 'draft',
  tone: site.tone || 'informative and engaging',
  minWords: parseInt(site.min_words) || 1500,
  maxWords: parseInt(site.max_words) || 2500,
  faqCount: parseInt(site.faq_count) || 5,
  imagesCount: (() => {
    // v2.33: Support images_min/images_max range (random) or single images_count
    const min = parseInt(site.images_min);
    const max = parseInt(site.images_max);
    if (!isNaN(min) && !isNaN(max) && min <= max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    return site.images_count !== undefined && site.images_count !== '' ? parseInt(site.images_count) : 0;
  })(),
  imageProvider: site.image_provider_priority 
    ? site.image_provider_priority.split(',').map(s => s.trim().toLowerCase()).filter(s => s) 
    : (globals.IMAGE_PROVIDER_PRIORITY_DEFAULT || 'fal,pexels,openai').split(',').map(s => s.trim().toLowerCase()).filter(s => s),
  internalLinksCount: (() => {
    const min = parseInt(site.internal_links_min);
    const max = parseInt(site.internal_links_max);
    if (!isNaN(min) && !isNaN(max) && min <= max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    return site.internal_links_count !== undefined ? parseInt(site.internal_links_count) : 3;
  })(),
  externalLinksCount: (() => {
    const min = parseInt(site.external_links_min);
    const max = parseInt(site.external_links_max);
    if (!isNaN(min) && !isNaN(max) && min <= max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    return site.external_links_count !== undefined ? parseInt(site.external_links_count) : 5;
  })(),
  youtubeCount: (() => {
    const min = parseInt(site.youtube_embeds_min);
    const max = parseInt(site.youtube_embeds_max);
    if (!isNaN(min) && !isNaN(max) && min <= max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    return site.youtube_embeds_count !== undefined && site.youtube_embeds_count !== '' ? parseInt(site.youtube_embeds_count) : 1;
  })(),
  defaultCategory: site.default_category || '',
  
  // Per-site notification controls (v2.8)
  speedyindexEnabled: parseBool(site.speedyindex_enabled, false),
  telegramEnabled: parseBool(site.telegram_enabled, true),
  emailEnabled: parseBool(site.email_enabled, false),
  
  openaiKey: globals.OPENAI_API_KEY,
  openaiModel: site.openai_model || globals.OPENAI_MODEL || 'gpt-4o-mini',
  openaiImageModel: site.openai_image_model || globals.OPENAI_IMAGE_MODEL || 'dall-e-2',
  falModel: site.fal_model || globals.FAL_MODEL || 'fal-ai/flux/schnell',
  googleCseKey: globals.GOOGLE_CSE_API_KEY || '',
  googleCseCx: globals.GOOGLE_CSE_CX || '',
  youtubeKey: globals.YOUTUBE_API_KEY || '',
  pexelsKey: globals.PEXELS_API_KEY || '',
  falKey: globals.FAL_API_KEY || '',
  speedyIndexKey: globals.SPEEDYINDEX_API_KEY || '',
  telegramToken: globals.TELEGRAM_BOT_TOKEN || '',
  telegramChatId: globals.TELEGRAM_CHAT_ID || '',
  notificationEmail: globals.NOTIFICATION_EMAIL || '',
  emailFrom: globals.EMAIL_FROM || 'noreply@autoblogger.local',
  emailProvider: detectEmailProvider(globals),
  resendApiKey: globals.RESEND_API_KEY || '',
  sendgridApiKey: globals.SENDGRID_API_KEY || '',
  mailgunApiKey: globals.MAILGUN_API_KEY || '',
  mailgunDomain: globals.MAILGUN_DOMAIN || '',
  smtp2goApiKey: globals.SMTP2GO_API_KEY || '',
  topic,
  tags: topicRow.tags || '',
  categories: topicRow.categories || topicRow.category || ''
};

debug.images_requested = config.imagesCount;
debug.internal_links_requested = config.internalLinksCount;
debug.external_links_requested = config.externalLinksCount;
debug.youtube_embeds_requested = config.youtubeCount;

async function httpRequest(options) {
  return await this.helpers.httpRequest(options);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

let cachedAuthHeaders = null;

async function getWpAuthHeaders() {
  if (cachedAuthHeaders) return cachedAuthHeaders;
  if (config.authMode === 'jwt') {
    if (config.jwtToken) {
      const valid = await validateJwtToken.call(this, config.jwtToken);
      if (valid) {
        cachedAuthHeaders = { Authorization: `Bearer ${config.jwtToken}` };
        return cachedAuthHeaders;
      }
    }
    const token = await getJwtToken.call(this);
    if (token) {
      cachedAuthHeaders = { Authorization: `Bearer ${token}` };
      return cachedAuthHeaders;
    }
    throw new Error('JWT authentication failed');
  } else {
    const creds = Buffer.from(`${config.wpUser}:${config.wpPassword}`).toString('base64');
    cachedAuthHeaders = { Authorization: `Basic ${creds}` };
    return cachedAuthHeaders;
  }
}

async function validateJwtToken(token) {
  try {
    const resp = await httpRequest.call(this, {
      method: 'POST',
      url: `${config.baseUrl}/wp-json/jwt-auth/v1/token/validate`,
      headers: { Authorization: `Bearer ${token}` }
    });
    return resp?.data?.status === 200 || resp?.code === 'jwt_auth_valid_token';
  } catch { return false; }
}

async function getJwtToken() {
  const endpoint = config.jwtTokenEndpoint || `${config.baseUrl}/wp-json/jwt-auth/v1/token`;
  try {
    const resp = await httpRequest.call(this, {
      method: 'POST',
      url: endpoint,
      body: { username: config.jwtUser, password: config.jwtPassword },
      headers: { 'Content-Type': 'application/json' }
    });
    return resp?.token || null;
  } catch (e) {
    throw new Error(`JWT token fetch failed: ${e.message}`);
  }
}

async function wpAuthSanityCheck() {
  const authHeaders = await getWpAuthHeaders.call(this);
  const resp = await httpRequest.call(this, {
    method: 'GET',
    url: `${config.baseUrl}/wp-json/wp/v2/users/me`,
    headers: authHeaders
  });
  if (!resp?.id) throw new Error('No user ID in response');
  return { ok: true, user: resp.name || resp.slug };
}

async function fetchSerpHints() {
  if (!config.googleCseKey || !config.googleCseCx) return [];
  try {
    const resp = await httpRequest.call(this, {
      method: 'GET',
      url: `https://www.googleapis.com/customsearch/v1?key=${config.googleCseKey}&cx=${config.googleCseCx}&q=${encodeURIComponent(config.topic)}&num=10`
    });
    const results = (resp?.items || []).map(item => ({ title: item.title, url: item.link, snippet: item.snippet }));
    debug.serp_count = results.length;
    return results;
  } catch (e) {
    debug.wp_errors.push({ step: 'SERP', error: e.message });
    return [];
  }
}

async function fetchYouTubeCandidates() {
  if (!config.youtubeKey || config.youtubeCount === 0) return [];
  try {
    const resp = await httpRequest.call(this, {
      method: 'GET',
      url: `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(config.topic)}&type=video&maxResults=5&key=${config.youtubeKey}`
    });
    const results = (resp?.items || []).map(item => ({
      videoId: item.id?.videoId,
      title: item.snippet?.title || 'Related Video',
      url: `https://www.youtube.com/watch?v=${item.id?.videoId}`
    }));
    debug.youtube_candidates_count = results.length;
    return results;
  } catch (e) {
    debug.wp_errors.push({ step: 'YOUTUBE', error: e.message });
    return [];
  }
}

async function generateContentJson() {
  const imagePlaceholderInstructions = config.imagesCount > 0 
    ? `\n\nIMAGE PLACEHOLDERS (REQUIRED):\nYou MUST include EXACTLY ${config.imagesCount} image placeholder(s) in the content_html.\nFormat: <!-- WPIMG alt="DESCRIPTIVE ALT TEXT HERE" -->\nPLACEMENT: Place each image where it would naturally enhance the reader's understanding - after explaining a concept, showing a process, or introducing a new section. Space them throughout the article.\nEach ALT text must be unique and descriptive of what the image should show.`
    : '';

  const youtubePlaceholderInstructions = config.youtubeCount > 0 
    ? `\n\nYOUTUBE PLACEHOLDERS (REQUIRED):\nYou MUST include EXACTLY ${config.youtubeCount} YouTube placeholder(s) in the content_html.\nFormat: <!-- YTVID context="DESCRIPTION OF WHAT VIDEO SHOULD COVER" -->\nPLACEMENT: Place each placeholder where a video tutorial, demonstration, or explanation would naturally fit - such as after introducing a technique, explaining a complex concept, or in a how-to section.\nEach context description should be unique and relate to the surrounding content.`
    : '';

  const systemPrompt = `You are an expert SEO content writer. You MUST respond with ONLY valid JSON, no other text.

Output JSON schema:
{
  "title": "SEO-optimized title",
  "slug": "url-friendly-slug",
  "meta_description": "150-160 char meta description",
  "focus_keyphrase": "main keyword/phrase to rank for",
  "tag_suggestions": ["tag1", "tag2"],
  "content_html": "<p>Full HTML content...</p>",
  "internal_anchor_phrases": ["phrase for internal links"],
  "external_anchor_phrases": ["phrase for external links"],
  "youtube_anchor_phrases": ["phrase near youtube embed spots"],
  "faq_items": [{"question": "FAQ question?", "answer": "Answer text"}]
}

CRITICAL RULES - MUST FOLLOW:
- ABSOLUTELY NO <a> tags or href attributes in content_html - links will be added programmatically later
- ABSOLUTELY NO URLs in content_html - no example.com, no placeholder links, no references
- ABSOLUTELY NO "Learn more", "Read more", "Click here" or similar link text
- NO citations, sources, or references sections
- Link anchor phrases must appear ONLY in paragraph text (<p>, <li>), NEVER in headings (<h2>, <h3>)

Content rules:
- Use proper HTML: h2, h3, p, ul, li, ol, strong, em, table, thead, tbody, tr, th, td
- INCLUDE AT LEAST ONE DATA TABLE (comparisons, specs, statistics, pros/cons)
- Tables should have proper thead with th headers and tbody with td cells
- Include ${config.faqCount} FAQs at the end (also return them in faq_items array for schema)
- Target ${config.minWords}-${config.maxWords} words
- Tone: ${config.tone}
- NO title in content_html (title goes in the title field)
- Anchor phrases MUST appear verbatim as plain text in PARAGRAPH content (NOT in headings)
- focus_keyphrase should appear naturally 3-5 times in the content${imagePlaceholderInstructions}${youtubePlaceholderInstructions}`;

  const userPrompt = `Write a comprehensive blog article about: "${config.topic}"

Provide:\n1. Engaging introduction\n2. 4-6 main sections with H2 headings\n3. Subsections with H3 where appropriate\n4. AT LEAST ONE HTML TABLE with data\n5. Practical tips and examples\n6. ${config.faqCount} FAQs at the end (also in faq_items array)\n7. ${Math.max(3, config.internalLinksCount)} internal_anchor_phrases (phrases that appear in PARAGRAPHS only)\n8. ${Math.max(3, config.externalLinksCount)} external_anchor_phrases (phrases that appear in PARAGRAPHS only)\n9. ${Math.max(2, config.youtubeCount)} youtube_anchor_phrases\n10. focus_keyphrase (main SEO keyword derived from topic)\n\nIMPORTANT: All anchor phrases must appear in <p> or <li> tags, NOT in headings.\n\nRespond with ONLY the JSON object.`;

  const resp = await httpRequest.call(this, {
    method: 'POST',
    url: 'https://api.openai.com/v1/chat/completions',
    headers: { 'Authorization': `Bearer ${config.openaiKey}`, 'Content-Type': 'application/json' },
    body: {
      model: config.openaiModel,
      messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userPrompt }],
      temperature: 0.7,
      max_tokens: 4500,
      response_format: { type: 'json_object' }
    }
  });

  const content = resp?.choices?.[0]?.message?.content;
  if (!content) throw new Error('Empty response from OpenAI');
  const parsed = JSON.parse(content);
  
  // Strip any hallucinated links from content_html (AI sometimes ignores instructions)
  if (parsed.content_html) {
    // Remove any <a> tags, keeping their inner text
    parsed.content_html = parsed.content_html.replace(/<a[^>]*>([^<]*)<\/a>/gi, '$1');
    // Remove any remaining href attributes (shouldn't happen but safety)
    parsed.content_html = parsed.content_html.replace(/href="[^"]*"/gi, '');
    // Remove placeholder URLs that might appear as text
    parsed.content_html = parsed.content_html.replace(/https?:\/\/example\.com[^\s<]*/gi, '');
    parsed.content_html = parsed.content_html.replace(/https?:\/\/www\.example\.com[^\s<]*/gi, '');
  }
  
  return parsed;
}

function validateContent(contentJson) {
  const errors = [];
  if (!contentJson.title) errors.push('Missing title');
  if (!contentJson.content_html) errors.push('Missing content_html');
  if (!contentJson.meta_description) errors.push('Missing meta_description');
  // v2.32: Image placeholder check is now a warning, not an error
  // AI sometimes doesn't include enough placeholders - we proceed with what we have
  if (config.imagesCount > 0) {
    const placeholderMatches = contentJson.content_html.match(/<!-- WPIMG alt="[^"]+" -->/g) || [];
    if (placeholderMatches.length < config.imagesCount) {
      debug.wp_errors.push({ step: 'VALIDATION_WARNING', message: `Image placeholders: wanted ${config.imagesCount}, got ${placeholderMatches.length}` });
    }
  }
  return errors;
}

async function generateImage(prompt) {
  for (const provider of config.imageProvider) {
    try {
      let img = null;
      if (provider === 'openai' && config.openaiKey) {
        img = await generateImageOpenAI.call(this, prompt);
      } else if (provider === 'fal' && config.falKey) {
        img = await generateImageFal.call(this, prompt);
      } else if (provider === 'pexels' && config.pexelsKey) {
        img = await fetchImagePexels.call(this, prompt);
      }
      if (img) {
        debug.images_by_provider[provider] = (debug.images_by_provider[provider] || 0) + 1;
        return { ...img, provider };
      }
    } catch (e) {
      debug.image_errors.push({ provider, prompt: prompt.substring(0, 50), error: e.message });
    }
  }
  return null;
}

// v2.23: OpenAI - use 512x512 to avoid memory issues on n8n Cloud
async function generateImageOpenAI(prompt) {
  // DALL-E 2 supports: 256x256, 512x512, 1024x1024
  // DALL-E 3 only supports: 1024x1024, 1024x1792, 1792x1024
  const isDalle3 = config.openaiImageModel === 'dall-e-3';
  const imageSize = isDalle3 ? '1024x1024' : '512x512'; // Smaller for DALL-E 2
  
  const resp = await httpRequest.call(this, {
    method: 'POST',
    url: 'https://api.openai.com/v1/images/generations',
    headers: { 'Authorization': `Bearer ${config.openaiKey}`, 'Content-Type': 'application/json' },
    body: {
      model: config.openaiImageModel,
      prompt: `Professional blog image: ${prompt}`,
      n: 1,
      size: imageSize,
      response_format: 'b64_json'
    },
    timeout: 60000
  });
  const b64 = resp?.data?.[0]?.b64_json;
  if (b64) return { base64: b64, mimeType: 'image/png', provider: 'openai' };
  return null;
}

// fal.ai - model configurable per-site: fal-ai/flux/schnell, fal-ai/flux/dev, fal-ai/fast-sdxl
async function generateImageFal(prompt) {
  const resp = await httpRequest.call(this, {
    method: 'POST',
    url: `https://fal.run/${config.falModel}`,
    headers: { 
      'Authorization': `Key ${config.falKey}`, 
      'Content-Type': 'application/json' 
    },
    body: {
      prompt: `Professional blog image: ${prompt}`,
      image_size: 'landscape_16_9',
      num_images: 1
    },
    timeout: 60000
  });
  const imageUrl = resp?.images?.[0]?.url;
  if (imageUrl) return { url: imageUrl };
  return null;
}

async function fetchImagePexels(query) {
  const resp = await httpRequest.call(this, {
    method: 'GET',
    url: `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=5`,
    headers: { 'Authorization': config.pexelsKey }
  });
  const photos = resp?.photos || [];
  if (photos.length > 0) {
    const photo = photos[Math.floor(Math.random() * photos.length)];
    return { url: photo.src?.large || photo.src?.original };
  }
  return null;
}

async function uploadImageToWp(imageData, filename, altText) {
  const authHeaders = await getWpAuthHeaders.call(this);
  
  // v2.27: Use custom n8n-image-upload plugin endpoints
  // These accept JSON (not binary) so Cloudflare won't block them
  
  const ext = (imageData.mimeType || 'image/png').includes('png') ? 'png' : 
              (imageData.mimeType || '').includes('webp') ? 'webp' : 'jpg';
  const fname = `${filename}.${ext}`;
  
  // For base64 images (OpenAI) - use /n8n/v1/upload-image
  if (imageData.base64) {
    const magicBytes = Buffer.from(imageData.base64, 'base64').slice(0, 4).toString('hex');
    debug.image_errors.push({ 
      step: 'TRYING_N8N_PLUGIN_BASE64', 
      filename: fname,
      magic_bytes: magicBytes,
      base64_length: imageData.base64.length
    });
    
    try {
      const uploadResp = await httpRequest.call(this, {
        method: 'POST',
        url: `${config.baseUrl}/wp-json/n8n/v1/upload-image`,
        headers: {
          ...authHeaders,
          'Content-Type': 'application/json'
        },
        body: {
          base64: imageData.base64,
          filename: fname,
          mime_type: imageData.mimeType || 'image/png',
          alt_text: altText || filename,
          title: altText || filename
        },
        timeout: 45000
      });
      
      if (uploadResp?.id || uploadResp?.success) {
        debug.image_errors.push({ step: 'N8N_PLUGIN_SUCCESS', id: uploadResp.id, url: uploadResp.url });
        return { id: uploadResp.id, url: uploadResp.url || uploadResp.source_url };
      }
      debug.image_errors.push({ step: 'N8N_PLUGIN_NO_ID', response: JSON.stringify(uploadResp || {}).substring(0, 300) });
    } catch (e) {
      const errMsg = e.message || '';
      debug.image_errors.push({ step: 'N8N_PLUGIN_FAILED', error: errMsg.substring(0, 200) });
      
      // If plugin not installed, fall back to standard upload
      if (errMsg.includes('rest_no_route') || errMsg.includes('404')) {
        debug.image_errors.push({ step: 'PLUGIN_NOT_INSTALLED', hint: 'Install n8n-image-upload.php plugin' });
      }
    }
  }
  
  // For URL images (fal, pexels) - use /n8n/v1/sideload-image
  if (imageData.url) {
    debug.image_errors.push({ step: 'TRYING_N8N_PLUGIN_SIDELOAD', url: imageData.url?.substring(0, 80) });
    
    try {
      const sideloadResp = await httpRequest.call(this, {
        method: 'POST',
        url: `${config.baseUrl}/wp-json/n8n/v1/sideload-image`,
        headers: {
          ...authHeaders,
          'Content-Type': 'application/json'
        },
        body: {
          url: imageData.url,
          filename: fname,
          alt_text: altText || filename,
          title: altText || filename
        },
        timeout: 45000
      });
      
      if (sideloadResp?.id || sideloadResp?.success) {
        debug.image_errors.push({ step: 'SIDELOAD_SUCCESS', id: sideloadResp.id, url: sideloadResp.url });
        return { id: sideloadResp.id, url: sideloadResp.url || sideloadResp.source_url };
      }
      debug.image_errors.push({ step: 'SIDELOAD_NO_ID', response: JSON.stringify(sideloadResp || {}).substring(0, 200) });
    } catch (e) {
      const errMsg = e.message || '';
      debug.image_errors.push({ step: 'SIDELOAD_FAILED', error: errMsg.substring(0, 200) });
      
      // Plugin not installed - use external URL as fallback
      if (errMsg.includes('rest_no_route') || errMsg.includes('404')) {
        debug.image_errors.push({ step: 'PLUGIN_NOT_INSTALLED_SIDELOAD' });
      }
    }
    
    // Fallback: Use external URL directly
    debug.image_errors.push({ step: 'USING_EXTERNAL_URL', url: imageData.url?.substring(0, 80) });
    return { id: null, url: imageData.url, external: true };
  }
  
  return null;
}

async function processImagePlaceholders(contentHtml, titleSlug) {
  const placeholderRegex = /<!-- WPIMG alt="([^"]+)" -->/g;
  const matches = [...contentHtml.matchAll(placeholderRegex)];
  let featuredImageId = null;
  let processedHtml = contentHtml;
  const domain = config.baseUrl.replace(/https?:\/\//, '').replace(/\/$/, '');
  
  for (let i = 0; i < Math.min(matches.length, config.imagesCount); i++) {
    const match = matches[i];
    const altText = match[1];
    const img = await generateImage.call(this, altText);
    if (img) {
      const uploaded = await uploadImageToWp.call(this, img, `${titleSlug}-${i + 1}`, altText);
      if (uploaded) {
        debug.images_uploaded++;
        // v2.13: Handle both WP-uploaded and external URLs
        const imgUrl = uploaded.url;
        const imgHtml = uploaded.external 
          ? `<figure class="wp-block-image"><img src="${imgUrl}" alt="${altText}" loading="lazy" /></figure>`
          : `<figure class="wp-block-image"><img src="${imgUrl}" alt="${altText} | ${domain}" loading="lazy" /></figure>`;
        processedHtml = processedHtml.replace(match[0], imgHtml);
        // Only set featured image if actually uploaded to WP
        if (i === 0 && uploaded.id) featuredImageId = uploaded.id;
        if (uploaded.external) {
          debug.image_errors.push({ step: 'USING_EXTERNAL_URL', url: imgUrl.substring(0, 80) });
        }
      } else {
        processedHtml = processedHtml.replace(match[0], '');
      }
    } else {
      processedHtml = processedHtml.replace(match[0], '');
    }
  }
  processedHtml = processedHtml.replace(placeholderRegex, '');
  return { html: processedHtml, featuredImageId };
}

// v2.28: Helper to check if a phrase is inside a heading tag
function isInsideHeading(content, phrase) {
  const escapedPhrase = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // Check if phrase appears inside any h1-h6 tag
  const headingRegex = new RegExp(`<h[1-6][^>]*>[^<]*${escapedPhrase}[^<]*</h[1-6]>`, 'i');
  return headingRegex.test(content);
}

// v2.28: Only match phrases inside paragraph or list content (not headings)
function findSafeLinkPosition(content, phrase) {
  const escapedPhrase = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // Match phrase only when inside <p>, <li>, <td> tags (NOT in headings)
  const safeContextRegex = new RegExp(
    `(<(?:p|li|td)[^>]*>[^<]*?)(\\b${escapedPhrase}\\b)([^<]*?</(?:p|li|td)>)`,
    'i'
  );
  return safeContextRegex.test(content) ? safeContextRegex : null;
}

async function injectInternalLinks(content, anchorPhrases) {
  if (config.internalLinksCount === 0 || !anchorPhrases?.length) return content;
  const authHeaders = await getWpAuthHeaders.call(this);
  let modifiedContent = content;
  let inserted = 0;
  const shuffled = [...anchorPhrases].sort(() => Math.random() - 0.5);
  
  for (const phrase of shuffled) {
    if (inserted >= config.internalLinksCount) break;
    // v2.28: Skip if phrase is inside a heading
    if (isInsideHeading(modifiedContent, phrase)) continue;
    
    const escapedPhrase = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const inLinkRegex = new RegExp(`<a[^>]*>[^<]*${escapedPhrase}[^<]*</a>`, 'i');
    // v2.28: Only match inside p, li, td tags
    const safeRegex = new RegExp(
      `(<(?:p|li|td)[^>]*>[^<]*?)(\\b${escapedPhrase}\\b)([^<]*?</(?:p|li|td)>)`,
      'i'
    );
    if (!safeRegex.test(modifiedContent) || inLinkRegex.test(modifiedContent)) continue;
    try {
      const searchResp = await httpRequest.call(this, {
        method: 'GET',
        url: `${config.baseUrl}/wp-json/wp/v2/posts?search=${encodeURIComponent(phrase)}&per_page=5&status=publish`,
        headers: authHeaders
      });
      if (searchResp?.length > 0) {
        const post = searchResp[0];
        modifiedContent = modifiedContent.replace(safeRegex, `$1<a href="${post.link}">$2</a>$3`);
        inserted++;
      }
    } catch (e) {}
  }
  debug.internal_links_inserted = inserted;
  return modifiedContent;
}

function injectExternalLinks(content, anchorPhrases, serpResults) {
  if (config.externalLinksCount === 0 || !serpResults?.length) return content;
  let modifiedContent = content;
  let inserted = 0;
  const usedUrls = new Set();
  const shuffledPhrases = [...(anchorPhrases || [])].sort(() => Math.random() - 0.5);
  const shuffledSerp = [...serpResults].sort(() => Math.random() - 0.5);
  
  for (const phrase of shuffledPhrases) {
    if (inserted >= config.externalLinksCount) break;
    // v2.28: Skip if phrase is inside a heading
    if (isInsideHeading(modifiedContent, phrase)) continue;
    
    const escapedPhrase = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const inLinkRegex = new RegExp(`<a[^>]*>[^<]*${escapedPhrase}[^<]*</a>`, 'i');
    // v2.28: Only match inside p, li, td tags
    const safeRegex = new RegExp(
      `(<(?:p|li|td)[^>]*>[^<]*?)(\\b${escapedPhrase}\\b)([^<]*?</(?:p|li|td)>)`,
      'i'
    );
    if (!safeRegex.test(modifiedContent) || inLinkRegex.test(modifiedContent)) continue;
    const serpItem = shuffledSerp.find(s => !usedUrls.has(s.url));
    if (serpItem) {
      modifiedContent = modifiedContent.replace(safeRegex, `$1<a href="${serpItem.url}" target="_blank" rel="noopener">$2</a>$3`);
      usedUrls.add(serpItem.url);
      inserted++;
    }
  }
  
  // Contextual fallback: find phrases from SERP results that naturally appear in content
  // v2.12: Try 2-3 word phrases first, then fall back to single words
  if (inserted < config.externalLinksCount) {
    const availableSerp = shuffledSerp.filter(s => !usedUrls.has(s.url));
    const skipWords = ['about', 'their', 'there', 'these', 'those', 'which', 'would', 'could', 'should', 'being', 'after', 'before', 'between', 'through', 'during', 'without', 'within', 'learn', 'click', 'here', 'best', 'guide', 'review', 'ultimate'];
    
    // Helper to extract n-grams from title
    function extractNgrams(title, n) {
      const words = title.split(/[^a-zA-Z0-9]+/).filter(w => w.length >= 3);
      const ngrams = [];
      for (let i = 0; i <= words.length - n; i++) {
        const phrase = words.slice(i, i + n).join(' ');
        // Skip if any word is a stop word
        const phraseWords = phrase.toLowerCase().split(' ');
        if (!phraseWords.some(w => skipWords.includes(w))) {
          ngrams.push(phrase);
        }
      }
      return ngrams;
    }
    
    for (const serpItem of availableSerp) {
      if (inserted >= config.externalLinksCount) break;
      let matched = false;
      
      // Try 3-word phrases first
      const trigrams = extractNgrams(serpItem.title, 3);
      for (const phrase of trigrams) {
        // v2.28: Skip if in heading
        if (isInsideHeading(modifiedContent, phrase)) continue;
        
        const escaped = phrase.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
        const inLinkRegex = new RegExp(`<a[^>]*>[^<]*${escaped}[^<]*</a>`, 'i');
        const safeRegex = new RegExp(
          `(<(?:p|li|td)[^>]*>[^<]*?)(\\b${escaped}\\b)([^<]*?</(?:p|li|td)>)`,
          'i'
        );
        if (safeRegex.test(modifiedContent) && !inLinkRegex.test(modifiedContent)) {
          modifiedContent = modifiedContent.replace(safeRegex, `$1<a href="${serpItem.url}" target="_blank" rel="noopener">$2</a>$3`);
          usedUrls.add(serpItem.url);
          inserted++;
          matched = true;
          break;
        }
      }
      if (matched) continue;
      
      // Try 2-word phrases
      const bigrams = extractNgrams(serpItem.title, 2);
      for (const phrase of bigrams) {
        if (isInsideHeading(modifiedContent, phrase)) continue;
        
        const escaped = phrase.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
        const inLinkRegex = new RegExp(`<a[^>]*>[^<]*${escaped}[^<]*</a>`, 'i');
        const safeRegex = new RegExp(
          `(<(?:p|li|td)[^>]*>[^<]*?)(\\b${escaped}\\b)([^<]*?</(?:p|li|td)>)`,
          'i'
        );
        if (safeRegex.test(modifiedContent) && !inLinkRegex.test(modifiedContent)) {
          modifiedContent = modifiedContent.replace(safeRegex, `$1<a href="${serpItem.url}" target="_blank" rel="noopener">$2</a>$3`);
          usedUrls.add(serpItem.url);
          inserted++;
          matched = true;
          break;
        }
      }
      if (matched) continue;
      
      // Fall back to single words (5+ chars)
      const singleWords = serpItem.title.split(/[^a-zA-Z0-9]+/).filter(w => w.length >= 5 && !skipWords.includes(w.toLowerCase()));
      for (const keyword of singleWords) {
        if (isInsideHeading(modifiedContent, keyword)) continue;
        
        const inLinkRegex = new RegExp(`<a[^>]*>[^<]*${keyword}[^<]*</a>`, 'i');
        const safeRegex = new RegExp(
          `(<(?:p|li|td)[^>]*>[^<]*?)(\\b${keyword}\\b)([^<]*?</(?:p|li|td)>)`,
          'i'
        );
        if (safeRegex.test(modifiedContent) && !inLinkRegex.test(modifiedContent)) {
          modifiedContent = modifiedContent.replace(safeRegex, `$1<a href="${serpItem.url}" target="_blank" rel="noopener">$2</a>$3`);
          usedUrls.add(serpItem.url);
          inserted++;
          break;
        }
      }
    }
  }
  debug.external_links_inserted = inserted;
  return modifiedContent;
}

// v2.36: YouTube embeds placed by AI using <!-- YTVID context="..." --> placeholders
function injectYouTubeEmbeds(content, anchorPhrases, youtubeCandidates) {
  if (config.youtubeCount === 0 || !youtubeCandidates?.length) return content;
  let modifiedContent = content;
  let inserted = 0;
  const usedVideos = new Set();
  const shuffledVideos = [...youtubeCandidates].sort(() => Math.random() - 0.5);
  
  // Find AI-placed YouTube placeholders
  const placeholderRegex = /<!-- YTVID context="([^"]+)" -->/g;
  const matches = [...content.matchAll(placeholderRegex)];
  
  // Replace placeholders with actual YouTube embeds
  for (let i = 0; i < Math.min(matches.length, config.youtubeCount); i++) {
    const match = matches[i];
    const video = shuffledVideos.find(v => !usedVideos.has(v.videoId));
    if (!video) break;
    
    const embedBlock = `<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=${video.videoId}
</div><figcaption>${video.title}</figcaption></figure>`;
    
    modifiedContent = modifiedContent.replace(match[0], embedBlock);
    usedVideos.add(video.videoId);
    inserted++;
  }
  
  // Clean up any remaining placeholders
  modifiedContent = modifiedContent.replace(/<!-- YTVID context="[^"]+" -->/g, '');
  
  // Fallback: if AI didn't place placeholders, use H2 distribution
  if (inserted === 0 && matches.length === 0) {
    debug.wp_errors.push({ step: 'YOUTUBE_PLACEHOLDERS', message: 'No AI placeholders found, using fallback distribution' });
    const h2Matches = [...modifiedContent.matchAll(/<\/h2>/gi)];
    const totalSections = h2Matches.length;
    
    if (totalSections > 0) {
      const embedCount = Math.min(config.youtubeCount, shuffledVideos.length, totalSections - 1);
      const positions = [];
      
      if (embedCount === 1) {
        positions.push(Math.floor(totalSections / 2));
      } else {
        const step = Math.floor((totalSections - 1) / (embedCount + 1));
        for (let i = 1; i <= embedCount; i++) {
          const pos = Math.min(i * step, totalSections - 1);
          if (!positions.includes(pos)) positions.push(pos);
        }
      }
      
      positions.sort((a, b) => b - a);
      
      for (const sectionIndex of positions) {
        if (inserted >= config.youtubeCount) break;
        const video = shuffledVideos.find(v => !usedVideos.has(v.videoId));
        if (!video) break;
        
        const h2Match = h2Matches[sectionIndex];
        if (!h2Match) continue;
        
        const embedBlock = `

<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=${video.videoId}
</div><figcaption>${video.title}</figcaption></figure>

`;
        
        const pos = h2Match.index + 5;
        modifiedContent = modifiedContent.slice(0, pos) + embedBlock + modifiedContent.slice(pos);
        usedVideos.add(video.videoId);
        inserted++;
      }
    }
  }
  
  debug.youtube_embeds_inserted = inserted;
  return modifiedContent;
}

async function getOrCreateTags(tagString, tagSuggestions) {
  const authHeaders = await getWpAuthHeaders.call(this);
  let termNames = [];
  if (tagString) {
    termNames = tagString.split(/[,|]/).map(t => t.trim()).filter(t => t);
  } else if (tagSuggestions?.length) {
    termNames = tagSuggestions.slice(0, 5);
  }
  if (termNames.length === 0) return [];
  const ids = [];
  for (const name of termNames) {
    try {
      const searchResp = await httpRequest.call(this, {
        method: 'GET',
        url: `${config.baseUrl}/wp-json/wp/v2/tags?search=${encodeURIComponent(name)}`,
        headers: authHeaders
      });
      const existing = (searchResp || []).find(t => t.name.toLowerCase() === name.toLowerCase());
      if (existing) {
        ids.push(existing.id);
      } else {
        const createResp = await httpRequest.call(this, {
          method: 'POST',
          url: `${config.baseUrl}/wp-json/wp/v2/tags`,
          headers: { ...authHeaders, 'Content-Type': 'application/json' },
          body: { name }
        });
        if (createResp?.id) ids.push(createResp.id);
      }
    } catch (e) {
      debug.wp_errors.push({ step: 'CREATE_TAG', name, error: e.message });
    }
  }
  return ids;
}

async function getCategories(categoryString) {
  const authHeaders = await getWpAuthHeaders.call(this);
  let termNames = [];
  if (categoryString) {
    termNames = categoryString.split(/[,|]/).map(t => t.trim()).filter(t => t);
  }
  if (termNames.length === 0 && config.defaultCategory) {
    termNames = [config.defaultCategory];
  }
  debug.categories_requested = termNames;
  if (termNames.length === 0) return [];
  const ids = [];
  let allCategories = [];
  try {
    const catResp = await httpRequest.call(this, {
      method: 'GET',
      url: `${config.baseUrl}/wp-json/wp/v2/categories?per_page=100`,
      headers: authHeaders
    });
    allCategories = catResp || [];
  } catch (e) {
    debug.wp_errors.push({ step: 'FETCH_CATEGORIES', error: e.message });
    return [];
  }
  for (const name of termNames) {
    const nameLower = name.toLowerCase();
    const nameSlug = nameLower.replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    let found = allCategories.find(c => c.name.toLowerCase() === nameLower);
    if (!found) found = allCategories.find(c => c.slug === nameSlug);
    if (!found) found = allCategories.find(c => c.name.toLowerCase().includes(nameLower) || nameLower.includes(c.name.toLowerCase()));
    if (found) {
      ids.push(found.id);
      debug.categories_found.push({ requested: name, matched: found.name, id: found.id });
    } else {
      // v2.31: Auto-create category via plugin endpoint (bypasses REST API 403)
      try {
        const createResp = await httpRequest.call(this, {
          method: 'POST',
          url: `${config.baseUrl}/wp-json/n8n/v1/create-category`,
          headers: { ...authHeaders, 'Content-Type': 'application/json' },
          body: { name: name, slug: nameSlug }
        });
        if (createResp?.id) {
          ids.push(createResp.id);
          debug.categories_found.push({ requested: name, created: createResp.created !== false, id: createResp.id });
        }
      } catch (createErr) {
        debug.wp_errors.push({ step: 'CREATE_CATEGORY', requested: name, error: createErr.message });
      }
    }
  }
  return ids;
}

// v2.29: Schema is handled by Yoast/RankMath plugins (WP blocks script tags in post content)
// The faq_items are still generated for potential future use or plugin integration

// v2.30: Update Yoast/RankMath SEO meta via custom plugin endpoint
async function updateSeoMeta(postId, contentJson) {
  const authHeaders = await getWpAuthHeaders.call(this);
  const focusKeyphrase = contentJson.focus_keyphrase || config.topic;
  
  // Try our custom n8n plugin endpoint first (uses update_post_meta directly)
  try {
    const seoResp = await httpRequest.call(this, {
      method: 'POST',
      url: `${config.baseUrl}/wp-json/n8n/v1/update-seo-meta`,
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: {
        post_id: postId,
        focus_keyphrase: focusKeyphrase,
        meta_description: contentJson.meta_description,
        seo_title: contentJson.title
      }
    });
    debug.seo_meta_updated = seoResp?.updated || true;
    debug.seo_plugins = seoResp?.seo_plugins || {};
    return;
  } catch (e) {
    // Plugin endpoint not available, try REST API fallback
    debug.seo_meta_updated = `plugin_not_found: ${e.message?.substring(0, 50)}`;
  }
  
  // Fallback: Try standard REST API (may not work without registered meta)
  try {
    await httpRequest.call(this, {
      method: 'POST',
      url: `${config.baseUrl}/wp-json/wp/v2/posts/${postId}`,
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: {
        meta: {
          _yoast_wpseo_focuskw: focusKeyphrase,
          _yoast_wpseo_metadesc: contentJson.meta_description,
          rank_math_focus_keyword: focusKeyphrase,
          rank_math_description: contentJson.meta_description
        }
      }
    });
    debug.seo_meta_updated = 'rest_api_fallback';
  } catch (e) {
    debug.seo_meta_updated = `failed: ${e.message?.substring(0, 50)}`;
  }
}

async function publishPost(postData) {
  const authHeaders = await getWpAuthHeaders.call(this);
  try {
    const resp = await httpRequest.call(this, {
      method: 'POST',
      url: `${config.baseUrl}/wp-json/wp/v2/posts`,
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: postData
    });
    return resp;
  } catch (e) {
    debug.wp_errors.push({ step: 'PUBLISH', error: e.message, statusCode: e.response?.status, response: e.response?.data });
    throw new Error(`WP POST failed: ${e.message}`);
  }
}

// v2.8: Per-site SpeedyIndex control
async function pingSpeedyIndex(postUrl) {
  if (!config.speedyindexEnabled) {
    debug.notifications.speedyindex = 'disabled_for_site';
    return false;
  }
  if (!config.speedyIndexKey) {
    debug.notifications.speedyindex = 'no_api_key';
    return false;
  }
  if (config.postStatus !== 'publish') {
    debug.notifications.speedyindex = 'post_not_published';
    return false;
  }
  try {
    await httpRequest.call(this, {
      method: 'POST',
      url: 'https://api.speedyindex.com/v1/index',
      headers: { 'Authorization': `Bearer ${config.speedyIndexKey}`, 'Content-Type': 'application/json' },
      body: { url: postUrl }
    });
    debug.notifications.speedyindex = true;
    return true;
  } catch (e) {
    debug.wp_errors.push({ step: 'SPEEDYINDEX', error: e.message });
    debug.notifications.speedyindex = `error: ${e.message}`;
    return false;
  }
}

// v2.8: Per-site Telegram control
async function sendTelegramNotification(message) {
  if (!config.telegramEnabled) {
    debug.notifications.telegram = 'disabled_for_site';
    return false;
  }
  if (!config.telegramToken || !config.telegramChatId) {
    debug.notifications.telegram = 'no_credentials';
    return false;
  }
  try {
    await httpRequest.call(this, {
      method: 'POST',
      url: `https://api.telegram.org/bot${config.telegramToken}/sendMessage`,
      headers: { 'Content-Type': 'application/json' },
      body: { chat_id: config.telegramChatId, text: message, parse_mode: 'HTML' }
    });
    debug.notifications.telegram = true;
    return true;
  } catch (e) {
    debug.wp_errors.push({ step: 'TELEGRAM', error: e.message });
    debug.notifications.telegram = `error: ${e.message}`;
    return false;
  }
}

// v2.8: Per-site Email control
async function sendEmailNotification(subject, htmlBody) {
  if (!config.emailEnabled) {
    debug.notifications.email = 'disabled_for_site';
    return false;
  }
  if (!config.notificationEmail) {
    debug.notifications.email = 'no_recipient';
    return false;
  }
  if (!config.emailProvider) {
    debug.notifications.email = 'no_provider';
    return false;
  }
  try {
    switch (config.emailProvider) {
      case 'resend':
        if (!config.resendApiKey) { debug.notifications.email = 'no_resend_key'; return false; }
        await httpRequest.call(this, {
          method: 'POST', url: 'https://api.resend.com/emails',
          headers: { 'Authorization': `Bearer ${config.resendApiKey}`, 'Content-Type': 'application/json' },
          body: { from: config.emailFrom, to: config.notificationEmail, subject, html: htmlBody }
        });
        break;
      case 'sendgrid':
        if (!config.sendgridApiKey) { debug.notifications.email = 'no_sendgrid_key'; return false; }
        await httpRequest.call(this, {
          method: 'POST', url: 'https://api.sendgrid.com/v3/mail/send',
          headers: { 'Authorization': `Bearer ${config.sendgridApiKey}`, 'Content-Type': 'application/json' },
          body: { personalizations: [{ to: [{ email: config.notificationEmail }] }], from: { email: config.emailFrom }, subject, content: [{ type: 'text/html', value: htmlBody }] }
        });
        break;
      case 'mailgun':
        if (!config.mailgunApiKey || !config.mailgunDomain) { debug.notifications.email = 'no_mailgun_config'; return false; }
        const formData = new URLSearchParams();
        formData.append('from', config.emailFrom);
        formData.append('to', config.notificationEmail);
        formData.append('subject', subject);
        formData.append('html', htmlBody);
        await httpRequest.call(this, {
          method: 'POST', url: `https://api.mailgun.net/v3/${config.mailgunDomain}/messages`,
          headers: { 'Authorization': `Basic ${Buffer.from(`api:${config.mailgunApiKey}`).toString('base64')}`, 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData.toString()
        });
        break;
      case 'smtp2go':
        if (!config.smtp2goApiKey) { debug.notifications.email = 'no_smtp2go_key'; return false; }
        await httpRequest.call(this, {
          method: 'POST', url: 'https://api.smtp2go.com/v3/email/send',
          headers: { 'Content-Type': 'application/json' },
          body: { api_key: config.smtp2goApiKey, sender: config.emailFrom, to: [config.notificationEmail], subject, html_body: htmlBody }
        });
        break;
      default:
        debug.notifications.email = `unknown_provider: ${config.emailProvider}`;
        return false;
    }
    debug.notifications.email = true;
    return true;
  } catch (e) {
    debug.wp_errors.push({ step: 'EMAIL', provider: config.emailProvider, error: e.message });
    debug.notifications.email = `error: ${e.message}`;
    return false;
  }
}

try {
  currentStep = 'WP_AUTH_CHECK';
  executionLog.push({ step: currentStep, status: 'started', time: new Date().toISOString() });
  const authCheck = await wpAuthSanityCheck.call(this);
  executionLog.push({ step: currentStep, status: 'completed', user: authCheck.user });
  
  currentStep = 'FETCH_HINTS';
  executionLog.push({ step: currentStep, status: 'started' });
  const [serpResults, youtubeCandidates] = await Promise.all([fetchSerpHints.call(this), fetchYouTubeCandidates.call(this)]);
  executionLog.push({ step: currentStep, status: 'completed', serp: serpResults.length, youtube: youtubeCandidates.length });
  
  currentStep = 'GENERATE_CONTENT';
  executionLog.push({ step: currentStep, status: 'started' });
  const contentJson = await generateContentJson.call(this);
  const validationErrors = validateContent(contentJson);
  if (validationErrors.length > 0) throw new Error(`Content validation failed: ${validationErrors.join(', ')}`);
  executionLog.push({ step: currentStep, status: 'completed', title: contentJson.title?.substring(0, 50) });
  
  currentStep = 'PROCESS_IMAGES';
  let processedHtml = contentJson.content_html;
  let featuredImageId = null;
  if (config.imagesCount > 0) {
    executionLog.push({ step: currentStep, status: 'started', count: config.imagesCount });
    const titleSlug = contentJson.slug || contentJson.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').substring(0, 50);
    const imgResult = await processImagePlaceholders.call(this, processedHtml, titleSlug);
    processedHtml = imgResult.html;
    featuredImageId = imgResult.featuredImageId;
    executionLog.push({ step: currentStep, status: 'completed', uploaded: debug.images_uploaded, featuredId: featuredImageId });
  } else {
    executionLog.push({ step: currentStep, status: 'skipped', reason: 'images_count=0' });
  }
  
  currentStep = 'INTERNAL_LINKS';
  if (config.internalLinksCount > 0) {
    executionLog.push({ step: currentStep, status: 'started' });
    processedHtml = await injectInternalLinks.call(this, processedHtml, contentJson.internal_anchor_phrases);
    executionLog.push({ step: currentStep, status: 'completed', inserted: debug.internal_links_inserted });
  } else {
    executionLog.push({ step: currentStep, status: 'skipped' });
  }
  
  currentStep = 'EXTERNAL_LINKS';
  if (config.externalLinksCount > 0 && serpResults.length > 0) {
    executionLog.push({ step: currentStep, status: 'started' });
    processedHtml = injectExternalLinks(processedHtml, contentJson.external_anchor_phrases, serpResults);
    executionLog.push({ step: currentStep, status: 'completed', inserted: debug.external_links_inserted });
  } else {
    executionLog.push({ step: currentStep, status: 'skipped', reason: serpResults.length === 0 ? 'no SERP results' : 'disabled' });
  }
  
  currentStep = 'YOUTUBE_EMBEDS';
  if (config.youtubeCount > 0 && youtubeCandidates.length > 0) {
    executionLog.push({ step: currentStep, status: 'started' });
    processedHtml = injectYouTubeEmbeds(processedHtml, contentJson.youtube_anchor_phrases, youtubeCandidates);
    executionLog.push({ step: currentStep, status: 'completed', inserted: debug.youtube_embeds_inserted });
  } else {
    executionLog.push({ step: currentStep, status: 'skipped' });
  }
  
  currentStep = 'TERMS';
  const [tagIds, categoryIds] = await Promise.all([getOrCreateTags.call(this, config.tags, contentJson.tag_suggestions), getCategories.call(this, config.categories)]);
  executionLog.push({ step: currentStep, status: 'completed', tags: tagIds.length, categories: categoryIds.length, categoryDetails: debug.categories_found });
  
  currentStep = 'PUBLISH_POST';
  executionLog.push({ step: currentStep, status: 'started' });
  
  // v2.29: Schema handled by Yoast/RankMath (WP blocks script tags in content)
  const postData = {
    title: contentJson.title,
    slug: contentJson.slug,
    content: processedHtml,
    excerpt: contentJson.meta_description,
    status: config.postStatus,
    comment_status: 'open',
    ping_status: 'open'
  };
  if (featuredImageId) postData.featured_media = featuredImageId;
  if (tagIds.length > 0) postData.tags = tagIds;
  if (categoryIds.length > 0) postData.categories = categoryIds;
  const postResp = await publishPost.call(this, postData);
  if (!postResp?.id) throw new Error('Failed to create WordPress post - no ID returned');
  executionLog.push({ step: currentStep, status: 'completed', postId: postResp.id });
  
  currentStep = 'POST_PROCESSING';
  
  // v2.28: Update Yoast/RankMath SEO meta fields
  await updateSeoMeta.call(this, postResp.id, contentJson);
  
  // SpeedyIndex (only for published posts, respects per-site setting)
  await pingSpeedyIndex.call(this, postResp.link);
  
  // Telegram (respects per-site setting)
  const notifyMessage = `✅ <b>New Post Published</b>\n\n📝 ${contentJson.title}\n🌐 ${site.site_name || config.baseUrl}\n🔗 ${postResp.link || 'Draft'}\n📊 Images: ${debug.images_uploaded}/${debug.images_requested}\n🔗 Internal: ${debug.internal_links_inserted}/${debug.internal_links_requested}\n🌐 External: ${debug.external_links_inserted}/${debug.external_links_requested}\n📺 YouTube: ${debug.youtube_embeds_inserted}/${debug.youtube_embeds_requested}\n🏷️ Categories: ${categoryIds.length}`;
  await sendTelegramNotification.call(this, notifyMessage);
  
  // Email (respects per-site setting)
  const emailHtml = `<h2>✅ New Post Published</h2><p><strong>Site:</strong> ${site.site_name || config.baseUrl}</p><p><strong>Title:</strong> ${contentJson.title}</p><p><strong>URL:</strong> <a href="${postResp.link}">${postResp.link || 'Draft'}</a></p><p><strong>Images:</strong> ${debug.images_uploaded}/${debug.images_requested}</p><p><strong>Internal Links:</strong> ${debug.internal_links_inserted}/${debug.internal_links_requested}</p><p><strong>External Links:</strong> ${debug.external_links_inserted}/${debug.external_links_requested}</p><p><strong>YouTube:</strong> ${debug.youtube_embeds_inserted}/${debug.youtube_embeds_requested}</p><p><strong>Categories:</strong> ${categoryIds.length}</p>`;
  await sendEmailNotification.call(this, `New Post: ${contentJson.title}`, emailHtml);
  
  executionLog.push({ step: currentStep, status: 'completed', notifications: debug.notifications });
  
  return [{ json: { ok: true, post_id: postResp.id, post_url: postResp.link, title: contentJson.title, slug: contentJson.slug, focus_keyphrase: contentJson.focus_keyphrase, status: postResp.status, featured_image_id: featuredImageId, debug, execution_log: executionLog, site, topicRow } }];
} catch (error) {
  executionLog.push({ step: currentStep, status: 'FAILED', error: error.message });
  
  // Send failure notifications (still respects per-site settings)
  const failMsg = `❌ <b>Post Failed</b>\n\n📝 ${config.topic}\n🌐 ${site.site_name || config.baseUrl}\n🚫 Step: ${currentStep}\n⚠️ ${error.message}`;
  await sendTelegramNotification.call(this, failMsg).catch(() => {});
  
  const failEmailHtml = `<h2>❌ Post Failed</h2><p><strong>Site:</strong> ${site.site_name || config.baseUrl}</p><p><strong>Topic:</strong> ${config.topic}</p><p><strong>Step:</strong> ${currentStep}</p><p><strong>Error:</strong> ${error.message}</p>`;
  await sendEmailNotification.call(this, `FAILED: ${config.topic}`, failEmailHtml).catch(() => {});
  
  return [{ json: { ok: false, error: error.message, failed_at_step: currentStep, debug, execution_log: executionLog, stack: error.stack, site, topicRow } }];
}

