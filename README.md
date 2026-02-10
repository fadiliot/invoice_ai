Invoice AI – Internal Deployment Guide
Overview
Invoice AI is an internal automation tool designed to:
- Extract invoice data using OCR
- Use AI fallback parsing when needed
- Route low-confidence invoices to manual review
- Sync approved invoices to QuickBooks
- Track processing status and failures
- Support up to 10,000 invoices per day

System Requirements
- Docker (v20+)
- Docker Compose
- 4 CPU cores recommended
- 8GB RAM recommended
- SSD storage recommended

Setup Instructions
1. Clone the repository:
   git clone <repo-url>
   cd invoice_ai

2. Create environment file:
   cp .env.example .env

3. Fill in required credentials in .env:
   - QuickBooks Client ID
   - QuickBooks Client Secret
   - QuickBooks Redirect URI
   - Gemini/OpenAI API Key

Start the System
Run:
   docker-compose up -d

This starts:
- FastAPI backend
- Redis queue
- Postgres database
- Background worker

Access the application at:
   http://<server-ip>:8000

Connecting QuickBooks
1. Open:
   http://<server-ip>:8000/api/auth/qb/login
2. Authorize the application.
3. Tokens will be stored automatically.

Restarting Services
   docker-compose restart
Stopping Services
   docker-compose down
Scaling Workers
To increase throughput:
   docker-compose up -d --scale worker=2

Recommended for 10k invoices/day.

Backup Strategy
Postgres data is stored in the 'postgres_data' volume.
It is recommended to:
- Snapshot the VM daily, OR
- Backup Postgres daily.

Health Check
   http://<server-ip>:8000/health

Returns:
   {"status": "ok"}

Failure Handling
- Failed invoices appear in the Failed section.
- Error messages are stored in the database.
- Retry functionality is available from the dashboard.

System Notes
- Uploaded files are stored in /uploads.
- Redis stores only job IDs (not file data).
- Designed for internal team use only.

