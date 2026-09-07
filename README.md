🔗 URL Shortener API

A full-stack URL shortener with JWT + Google OAuth authentication, Redis caching, rate limiting, and a Streamlit dashboard — built with FastAPI.

Python FastAPI SQLAlchemy Redis Streamlit License: MIT

Live API - {https://url-shortener-api-backend-5.onrender.com} · Live UI - {https://url-shortener-api-ui.onrender.com} · API Docs (Swagger)

</div>
Overview

This is a production-shaped URL shortener API — not just a POST /shorten toy endpoint. It has real user accounts (email/password + Google OAuth), JWT-secured routes, per-user link ownership, click analytics, a Redis cache-aside layer in front of the database, and Redis-backed rate limiting on the public redirect endpoint. A Streamlit dashboard sits on top for a usable frontend without hand-rolling a JS app.

It's deployed live on Render (API + Streamlit UI as separate services) and backed by Supabase Postgres in production.

Features
🔐 Email/password auth with bcrypt password hashing and JWT access tokens
🔑 Google OAuth 2.0 login flow
✂️ Short link creation with collision-checked random short codes
📊 Per-user link ownership — list only your own links
🖱️ Click tracking, incremented via a FastAPI BackgroundTask so redirects aren't slowed down by the write
⚡ Redis cache-aside in front of the DB for redirect lookups, including negative caching (NULL, 60s TTL) for unknown codes so repeated 404s don't keep hitting the database
🛡️ Redis-backed rate limiting (10 requests / 60s per client IP) on the public redirect endpoint
🖥️ Streamlit dashboard for login, link creation, and viewing your links
📄 Auto-generated OpenAPI/Swagger docs at /docs
Tech Stack
Layer	Technology
API framework	FastAPI + Uvicorn
ORM / DB	SQLAlchemy, Supabase (Postgres) in production
Auth	JWT (python-jose), bcrypt (passlib), Google OAuth 2.0
Caching / rate limiting	Redis (Upstash in production)
Frontend	Streamlit
Deployment	Render (API + UI as separate services)
Architecture
┌─────────────────┐        HTTPS         ┌──────────────────────┐
│ Streamlit UI     │ ───────────────────▶ │ FastAPI backend       │
│ (Render service)│ ◀─────────────────── │ (Render service)      │
└─────────────────┘                       └───────┬──────────────┘
                                                    │
                          ┌─────────────────────────┼─────────────────────────┐
                          ▼                          ▼                         ▼
                 ┌─────────────────┐        ┌─────────────────┐      ┌──────────────────┐
                 │ Supabase          │        │ Upstash Redis     │      │ Google OAuth       │
                 │ (Postgres)        │        │ cache + rate limit│      │ (identity)          │
                 └─────────────────┘        └─────────────────┘      └──────────────────┘

Redirect request flow (GET /u/{short_code}):

Check the per-IP rate limit in Redis (INCR + EXPIRE) — reject with 429 if exceeded.
Check Redis cache for the short code. Cache hit → skip the DB entirely.
Cache miss → query Postgres. Not found → cache a NULL sentinel for 60s and return 404. Found → cache the target URL for 1 hour.
Return an HTTP 307 redirect.
Increment the click counter after the response is sent, via a background task, so the redirect itself is never blocked on a DB write.
Project Structure
URL_SHORTENER_API/
├── main.py                    # FastAPI app entrypoint, router registration
├── frontend.py                 # Streamlit dashboard
├── auth.py                     # Password hashing, JWT create/verify, get_current_user
├── database.py                 # SQLAlchemy engine/session setup
├── models.py                   # User, URL ORM models
├── schemas.py                  # Pydantic request/response models
├── crud.py                     # DB access functions
├── deps.py                     # Shared FastAPI dependencies
├── core/
│   └── redis_client.py         # Fault-tolerant Redis wrapper (Upstash)
├── routers/
│   ├── authh.py                # /auth/* — register, login, Google OAuth
│   └── url.py                  # /urls, /u/{short_code}
└── services/
    ├── url_service.py          # Cache-aside redirect lookup, click increment
    └── rate_limiter.py         # Redis INCR/EXPIRE-based rate limiting
API Reference

Full interactive docs are always available at /docs (Swagger UI) and /redoc.

Auth — /auth
Method	Endpoint	Auth	Description
POST	/auth/register	–	Register with { email, password }
POST	/auth/login	–	Login with { email, password } → { access_token, token_type }
GET	/auth/google/login	–	Redirects to Google's OAuth consent screen
GET	/auth/google/callback	–	OAuth callback — issues a JWT and redirects to the frontend
URLs
Method	Endpoint	Auth	Description
POST	/urls	✅ Bearer token	Create a short link from { target_url }
GET	/urls	✅ Bearer token	List the current user's short links
GET	/u/{short_code}	–	Public redirect to the original URL (rate-limited)

Example: create a short link

bash
curl -X POST https://url-shortener-api-backend-5.onrender.com/urls \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{"target_url": "https://example.com/a/very/long/path"}'
json
{
  "id": 1,
  "short_code": "aB3xQ9",
  "target_url": "https://example.com/a/very/long/path",
  "clicks": 0
}
Getting Started (Local Development)
Prerequisites
Python 3.11+
A Postgres database (or point SUPABASE_DB_URL at a local SQLite file for quick testing)
A Redis instance (Upstash, or local redis-server) — optional, the app degrades gracefully to "no caching / no rate limiting" if Redis is unreachable
1. Clone the repo
bash
git clone https://github.com/mohits2005/URL_SHORTENER_API_BACKEND.git
cd URL_SHORTENER_API_BACKEND
2. Create a virtual environment
bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
3. Install dependencies
bash
pip install -r requirements.txt
4. Configure environment variables

Create a .env file in the project root:

env
SECRET_KEY=your_jwt_secret
SUPABASE_DB_URL=postgresql://user:password@host:port/dbname
UPSTASH_REDIS_REST_URL=https://your-upstash-url
UPSTASH_REDIS_REST_TOKEN=your_upstash_token
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback
FRONTEND_URL=http://localhost:8501
5. Run the backend
bash
uvicorn URL_SHORTENER_API.main:app --reload

API is now live at http://127.0.0.1:8000, docs at http://127.0.0.1:8000/docs.

6. Run the frontend
bash
streamlit run URL_SHORTENER_API/frontend.py
