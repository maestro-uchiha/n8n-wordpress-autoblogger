# Contributing to n8n WordPress Autoblogger

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Create a new issue with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Debug output (redact sensitive data)
   - n8n and WordPress versions

### Suggesting Features

1. Open a feature request issue
2. Describe the use case
3. Explain why it would benefit others
4. If possible, suggest implementation approach

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Development Guidelines

### Workflow Changes

- Update version ID: `"versionId": "v2.XX-description"`
- Test with both JWT and Basic auth
- Test with multiple sites if applicable
- Update documentation if adding features

### Plugin Changes

- Update version in plugin header
- Maintain backward compatibility
- Test with Yoast and RankMath
- Test with various WordPress versions (5.0+)

### Documentation

- Keep language clear and beginner-friendly
- Include examples where helpful
- Update relevant docs when changing features

## Code Style

### JavaScript (n8n Code Nodes)

- Use `async/await` for HTTP requests
- Include error handling with try/catch
- Log to `debug` object for troubleshooting
- Use meaningful variable names

### PHP (WordPress Plugin)

- Follow WordPress coding standards
- Sanitize all inputs
- Use `WP_Error` for error responses
- Include PHPDoc comments

## Testing Checklist

Before submitting:

- [ ] Tested with draft and publish post status
- [ ] Tested with 0 images and 1+ images
- [ ] Tested internal and external links
- [ ] Tested category creation
- [ ] Tested SEO meta updates
- [ ] No sensitive data in commits
- [ ] Documentation updated

## Questions?

Open a discussion or issue - we're happy to help!
