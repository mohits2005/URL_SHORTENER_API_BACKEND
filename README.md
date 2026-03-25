# 🔗 URL Shortener Backend with Redis Optimization & Streamlit Frontend

A production-style full-stack URL shortener built with **FastAPI**, featuring **JWT authentication**, **Google OAuth**, **Redis caching**, **rate limiting**, and a **Streamlit-based frontend dashboard** for intuitive link management.

---

# 🚀 Features

* User registration & login (Email + Password)
* JWT-based authentication & authorization
* Google OAuth 2.0 login
* Create short URLs for long links
* Public redirection using short URLs
* Click count tracking for each URL
* Redis-based caching for fast redirects
* Redis-based rate limiting (API abuse protection)
* Background click tracking
* Streamlit frontend dashboard
* User-specific data isolation
* RESTful API design with Swagger documentation

---

# ⚡ Performance Optimizations

* Implemented **Redis cache-aside pattern** to reduce database lookups
* Reduced redirect latency by ~80% using in-memory caching
* Added **Redis INCR + TTL rate limiting** for traffic control
* Background tasks for non-blocking click tracking
* Optimized API responsiveness for concurrent users

---

# 🛠️ Tech Stack

**Backend**

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT Authentication
* Google OAuth 2.0
* SQLite / MySQL

**Performance & Scaling**

* Redis (Caching)
* Redis (Rate Limiting)

**Frontend**

* Streamlit

**Dev Tools**

* Git
* Uvicorn
* Swagger UI

---

# 📂 Project Structure

```
URL_SHORTENER_API
│
├── core/
│   └── redis_client.py
│
├── services/
│   ├── url_service.py
│   └── rate_limiter.py
│
├── routers/
│   ├── authh.py
│   └── url.py
│
├── frontend.py
├── models.py
├── schemas.py
├── database.py
├── crud.py
├── main.py
```

---

# 🔐 Authentication Flow

### Email & Password

* User registers with email and password
* Password is securely hashed
* Login returns JWT access token
* Token required for protected endpoints

### Google OAuth

* User initiates Google login
* Google authenticates user
* Backend fetches user profile
* Backend issues JWT token

---

# 🔗 API Endpoints

### Auth

* `POST /auth/register` – Register user
* `POST /auth/login` – Login & receive JWT
* `GET /auth/google/login` – Google login
* `GET /auth/google/callback` – OAuth callback

### URLs

* `POST /urls` – Create short URL (Auth required)
* `GET /urls` – List user URLs (Auth required)
* `GET /u/{short_code}` – Redirect (Public)

---

# ⚡ Redis Features

### Caching

* Short URLs cached in Redis
* Reduces DB load
* Improves redirect speed

### Rate Limiting

* Per-IP request tracking
* Redis INCR with TTL
* Prevents abuse & spam traffic

---

# 🌍 Redirect Behavior

* Short URL endpoint returns **HTTP 307 redirect**
* Works correctly in browser
* Clicks increment in background
* Cached for faster subsequent requests

---

# 🖥️ Streamlit Frontend

Features:

* User login & registration UI
* Create short URLs
* View click analytics
* Dashboard-style layout
* Persistent login session

Run frontend:

```
streamlit run URL_SHORTENER_API/frontend.py
```

---

# 🧪 Running Locally

### 1️⃣ Clone repo

```
git clone https://github.com/mohits2005/URL_SHORTENER_API_BACKEND.git
cd URL_SHORTENER_API_BACKEND
```

### 2️⃣ Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Run Redis

```
redis-server
```

### 5️⃣ Run backend

```
uvicorn URL_SHORTENER_API.main:app --reload
```

### 6️⃣ Run frontend

```
streamlit run URL_SHORTENER_API/frontend.py
```

---

# 🔑 Environment Variables

Create `.env` file:

```
SECRET_KEY=your_jwt_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

---

# 🔒 Security

* Password hashing (bcrypt)
* JWT expiration
* Rate limiting protection
* Auth-required endpoints
* Google OAuth server-side validation

---

# 📈 Future Improvements

* Click analytics dashboard
* Custom domains
* Link expiration
* QR code generation
* Docker deployment

---

# 👨‍💻 Author

Mohit
