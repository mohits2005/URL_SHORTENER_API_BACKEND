<<<<<<< HEAD
# URL-Shortener-Backend

🔗 URL Shortener & Authentication API

A production-style backend API built with FastAPI that allows users to shorten long URLs, securely authenticate (JWT + Google OAuth), and track link usage through click analytics.

🚀 Features

User registration & login (Email + Password)

JWT-based authentication & authorization

Google OAuth 2.0 login

Create short URLs for long links

Public redirection using short URLs

Click count tracking for each URL

User-specific data isolation

RESTful API design with Swagger documentation

🛠️ Tech Stack

Python 3

FastAPI

SQLAlchemy (ORM)

SQLite (development database)

JWT (OAuth2PasswordBearer)

Google OAuth 2.0

Uvicorn

Swagger UI (OpenAPI)

📂 Project Structure
URL_SHORTENER/
│
├── main.py                 # Application entry point
├── database.py             # Database configuration
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── crud.py                 # Database operations
│
├── routers/
│   ├── auth.py             # Authentication & Google OAuth
│   └── urls.py             # URL endpoints & redirect
│
└── url_shortener.db

🔐 Authentication Flow
Email & Password

User registers with email and password

Password is securely hashed

Login returns a JWT access token

Token is required for protected endpoints

Google OAuth

User initiates Google login

Google authenticates user

Backend exchanges authorization code for token

User info is fetched from Google

Backend issues its own JWT

🔗 API Endpoints (Overview)
Auth

POST /auth/register – Register a new user

POST /auth/login – Login and receive JWT

GET /auth/google/login – Login with Google

GET /auth/google/callback – Google OAuth callback

URLs

POST /urls – Create a short URL (Auth required)

GET /urls – List user’s URLs (Auth required)

GET /u/{short_code} – Redirect to original URL (Public)

🌍 Redirect Behavior

Short URL endpoint returns HTTP 307 redirect

Works correctly in browsers

Swagger UI cannot follow cross-origin redirects (expected behavior)

🧪 Running the Project Locally
1️⃣ Clone the repository
git clone https://github.com/your-username/url-shortener-api.git
cd url-shortener-api

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the server
uvicorn main:app --reload

5️⃣ Open API docs
http://127.0.0.1:8000/docs

🔑 Environment Variables

Create a .env file:

SECRET_KEY=your_jwt_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

🔒 Security Considerations

Passwords are hashed using bcrypt

JWT tokens include expiration

Protected routes require valid authentication

Google OAuth handled server-side only
=======
# URL_SHORTENER_API_BACKEND
>>>>>>> 0fdfab47d5bf56899601c31956cde2da3603d138
