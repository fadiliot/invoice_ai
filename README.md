# Invoice AI — Internal Deployment Guide

A compact, easy-to-scan guide for deploying and operating Invoice AI — an internal automation pipeline that extracts invoice data, routes low-confidence cases to review, and syncs approved invoices to QuickBooks.

---

## Highlights
- ✅ OCR-first extraction with AI fallback parsing
- 🔁 Manual review workflow for low-confidence invoices
- 🔗 QuickBooks sync for approved invoices
- 📈 Designed for up to 10,000 invoices/day

---

## System Requirements
| Component | Recommended |
|---|---|
| Docker | v20+ |
| Orchestration | Docker Compose |
| CPU | 4 cores |
| RAM | 8 GB |
| Storage | SSD |

---

## Quick Start

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd invoice_ai
   ```

2. Create and edit environment file:
   ```bash
   cp .env.example .env
   # Edit .env with required credentials
   ```

3. Start services:
   ```bash
   docker-compose up -d
   ```

Access the app: http://<server-ip>:8000

Services started:
- FastAPI backend
- Redis queue
- Postgres database
- Background worker(s)

---

## Environment Variables (minimum)
Fill these in `.env`:
- QUICKBOOKS_CLIENT_ID
- QUICKBOOKS_CLIENT_SECRET
- QUICKBOOKS_REDIRECT_URI
- GEMINI_OR_OPENAI_API_KEY (or whichever AI provider key you use)

---

## QuickBooks Connection
1. Open:
   ```
   http://<server-ip>:8000/api/auth/qb/login
   ```
2. Authorize the app.
3. Tokens are stored automatically.

---

## Operations

- Restart services:
  ```bash
  docker-compose restart
  ```

- Stop services:
  ```bash
  docker-compose down
  ```

- Scale workers (increase throughput):
  ```bash
  docker-compose up -d --scale worker=2
  ```
  Recommended for ~10k invoices/day (adjust worker count to match CPU/memory limits).

---

## Health Check
GET:
```
http://<server-ip>:8000/health
```
Response:
```json
{"status":"ok"}
```

---

## Storage & Backups
- Uploaded files: `/uploads`
- Postgres data: Docker volume `postgres_data`

Recommended backup strategies:
- Snapshot VM daily, OR
- Daily Postgres backups (pg_dump or scheduled backups)

---

## Failure Handling & Monitoring
- Failed invoices: visible in the "Failed" section of the dashboard
- Error messages are persisted in the database
- Manual retry functionality available from the UI
- Redis holds job IDs only (file data stored on disk)

---

## Scaling Notes
- Increase worker instances to boost throughput
- Monitor CPU, RAM, I/O — SSD recommended for upload performance
- Consider sharding or more powerful DB host for very high loads

---

## Security & Usage
- Intended for internal team use only
- Protect `.env` and QuickBooks/API credentials
- Run behind an internal firewall or VPN when possible

---

## Troubleshooting Tips
- Backend not reachable: confirm Docker Compose started, check container logs (`docker-compose logs -f`)
- QuickBooks token errors: re-run the OAuth flow via `/api/auth/qb/login`
- Worker failures: inspect worker logs and DB `errors` table

---

## Contact
For deployment questions, contact the maintainer/team.

---
