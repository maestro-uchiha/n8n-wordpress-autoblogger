# n8n WordPress Autoblogger v2.31

A powerful, fully automated blog publishing system using n8n workflows and WordPress REST API.

## ✨ Features

- **AI-Powered Content**: GPT-4o generates SEO-optimized articles with proper HTML structure
- **Multi-Site Support**: Manage multiple WordPress sites from a single Google Sheet
- **AI Image Generation**: OpenAI DALL-E, fal.ai Flux, or Pexels stock photos
- **Smart Linking**: Automatic internal and external link injection (paragraph-only, never in headings)
- **YouTube Embeds**: Auto-embed relevant videos from YouTube API
- **SEO Integration**: Native Yoast SEO and RankMath support
- **Auto-Categories**: Creates categories automatically if they don't exist
- **Notifications**: Telegram, Email (Resend/SendGrid/Mailgun/SMTP2GO), SpeedyIndex

## 🚀 Quick Start

1. **Import Workflows** into n8n Cloud or self-hosted n8n
2. **Install WordPress Plugin** on each site
3. **Configure Google Sheets** with sites and topics
4. **Set n8n Variables** with API keys
5. **Run Master Scheduler** - posts are created automatically!

## 📁 Repository Structure

```
├── Current/                      # Ready-to-import n8n workflows
│   ├── Master Scheduler (Multi-site).json
│   ├── Publisher (Autoblogging Engine).json
│   └── Cleanup (Stuck Locks).json
├── wordpress-plugin/
│   ├── n8n-image-upload.php      # WordPress plugin source
│   └── n8n-autoblogger-helper.zip # Ready to upload
├── docs/
│   ├── SETUP_GUIDE.md            # Step-by-step setup
│   ├── CONFIGURATION.md          # All configuration options
│   ├── TROUBLESHOOTING.md        # Common issues & fixes
│   └── TECHNICAL.md              # Architecture & internals
└── Context/                      # Reference documentation
```

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [Setup Guide](docs/SETUP_GUIDE.md) | Step-by-step installation for beginners |
| [Configuration](docs/CONFIGURATION.md) | All settings explained |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [Technical Reference](docs/TECHNICAL.md) | Architecture for developers |

## 🔧 Requirements

- **n8n**: Cloud or self-hosted (v1.0+)
- **WordPress**: 5.0+ with REST API enabled
- **PHP**: 7.4+ (for WordPress plugin)
- **APIs**: OpenAI (required), Google CSE, YouTube, fal.ai, Pexels (optional)

## 📊 System Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Google Sheets  │────▶│  n8n Workflows   │────▶│    WordPress    │
│  (Sites/Topics) │     │  (Orchestration) │     │  (Publishing)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
              ┌─────────┐ ┌────────┐ ┌─────────┐
              │ OpenAI  │ │ Images │ │ YouTube │
              │  GPT-4  │ │  APIs  │ │   API   │
              └─────────┘ └────────┘ └─────────┘
```

## 🔐 Security Notes

- Use **Application Passwords** or **JWT Auth** for WordPress
- Store API keys in n8n Variables (never in workflows)
- The WordPress plugin requires `edit_posts` capability
- All endpoints are authenticated

## 📝 License

MIT License - Use freely, attribution appreciated.

## 🤝 Contributing

Issues and PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Version**: 2.31 | **Last Updated**: January 2026
