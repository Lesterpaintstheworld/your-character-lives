# ID Management Documentation

> **IMPORTANT**: This file is for documentation purposes only. Never commit actual ID values to version control!

## Purpose
This document provides a centralized reference for tracking and managing various IDs used throughout the CK3 AI Assistant project. It includes placeholders for sensitive information and best practices for ID management.

## Current IDs

### API Keys
| ID Name | ID Value | Description | Date Added | Last Updated |
|---------|----------|-------------|------------|--------------|
| OPENAI_API_KEY | `<OPENAI_KEY>` | OpenAI API authentication for GPT and Whisper | 2024-01-01 | 2024-01-15 |
| N8N_API_KEY | `<N8N_KEY>` | n8n workflow authentication | 2024-01-01 | 2024-01-15 |
| XATA_API_KEY | `<XATA_KEY>` | Xata database access | 2024-01-01 | 2024-01-15 |

### User IDs
| ID Name | ID Value | Description | Date Added | Last Updated |
|---------|----------|-------------|------------|--------------|
| ADMIN_USER | `<ADMIN_ID>` | Administrator account identifier | 2024-01-01 | 2024-01-15 |
| SERVICE_USER | `<SERVICE_ID>` | Service account for background tasks | 2024-01-01 | 2024-01-15 |

### Database IDs
| ID Name | ID Value | Description | Date Added | Last Updated |
|---------|----------|-------------|------------|--------------|
| MAIN_DB | `<DB_ID>` | Primary database identifier | 2024-01-01 | 2024-01-15 |
| BACKUP_DB | `<BACKUP_DB_ID>` | Backup database identifier | 2024-01-01 | 2024-01-15 |

## ID of the Day
🎲 **Featured ID**: OPENAI_API_KEY
> Fun Fact: This key enables our AI characters to process over 1000 unique medieval scenarios daily, helping them make historically accurate decisions in CK3!

## ID Management Best Practices

### Security
- Never commit actual ID values to version control
- Use environment variables for sensitive IDs
- Implement key rotation schedules
- Monitor ID usage patterns
- Log access attempts

### Organization
- Document all new IDs in this file
- Keep the "Last Updated" field current
- Remove deprecated IDs promptly
- Use consistent naming conventions
- Include clear descriptions

### Rotation Schedule
- API Keys: Every 90 days
- User IDs: Review quarterly
- Database IDs: Review annually
- Emergency rotation procedure in place

## Version History

### v1.0.0 (2024-01-15)
- Initial documentation structure
- Added API keys section
- Added User IDs section
- Added Database IDs section

### v0.9.0 (2024-01-01)
- Draft version
- Basic structure outlined
