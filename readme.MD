# 🎙️ Vani — AI Communication Coach for First-Gen Learners

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4.0-06B6D4)](https://tailwindcss.com/)

> *“Every AI interview tool is built for the employer. Vani is built for Priya — the first-gen learner who needs to practice 50 times in Kannada before she's ready to speak once in English.”*

---

# 📌 Overview

**Vani** is an AI-powered communication coach designed specifically for first-generation learners in India.

Most communication and interview tools assume users already know professional English. Vani takes a different approach — users begin practicing in their **native language** and gradually transition into confident English communication.

The platform provides:

* 🎙️ AI speech feedback
* 💬 Real-life conversation practice
* 📝 Mock interviews
* 👥 Peer tutoring
* 🏆 Verifiable blockchain credentials
* 📱 WhatsApp-first accessibility

---

# 🎯 Problem Statement

### PS 3.2 — Job Readiness & Entrepreneurial Skills

Helping learners build communication confidence and workplace readiness.

### PS 3.3 — Skills Assessment & Proficiency Signaling

Providing measurable communication assessments and tamper-proof credentials.

---

# ✨ Features

| Feature                   | Description                                                         |
| ------------------------- | ------------------------------------------------------------------- |
| 🎙️ AI Speech Practice    | Real-time pronunciation, grammar, and fluency feedback              |
| 💬 Daily Conversations    | Practice real-world conversations with an AI coach                  |
| 📝 Interview Preparation  | 500+ interview questions with AI evaluation                         |
| 👥 Peer Tutors            | Connect with college students for live practice                     |
| 🏆 Blockchain Credentials | Skill certificates minted on Solana                                 |
| 🌐 Multilingual Support   | Kannada, Hindi, Tamil, Telugu, Malayalam, Bengali, Marathi, English |
| 📱 WhatsApp Integration   | Practice without installing any app                                 |
| 📊 Progress Tracking      | Track confidence, fluency, and consistency                          |
| ⚡ Real-Time Feedback      | Low-latency AI feedback powered by Groq                             |

---

# 🧠 Why Vani?

India has millions of talented students who understand concepts but struggle with spoken English confidence.

Existing interview tools are designed for already-fluent candidates.

Vani focuses on:

* Native-language-first learning
* Psychological safety during practice
* Repetition-based confidence building
* Affordable accessibility
* Mobile-first and low-bandwidth support

---

# 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            VANI ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📱 FRONTEND               ☁️ BACKEND                    💾 STORAGE          │
│  ┌──────────────┐         ┌──────────────┐             ┌─────────────┐      │
│  │ React PWA   │ ─────▶ │ FastAPI      │ ─────────▶ │ Supabase PG │      │
│  │ TailwindCSS │         │ Python 3.11  │             │ PostgreSQL  │      │
│  │ Vite         │         └──────────────┘             └─────────────┘      │
│  └──────────────┘                  │                                        │
│                                    │                                        │
│                         ┌──────────┴──────────┐                             │
│                         │                     │                             │
│                   ┌─────▼─────┐       ┌──────▼──────┐                       │
│                   │  Groq AI  │       │    Redis    │                       │
│                   │ Llama 3.3 │       │    Cache    │                       │
│                   │ Whisper   │       └─────────────┘                       │
│                   └───────────┘                                             │
│                                    │                                        │
│                                    ▼                                        │
│                     WhatsApp Business API                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 🛠️ Tech Stack

| Layer            | Technology                     | Purpose                  |
| ---------------- | ------------------------------ | ------------------------ |
| Frontend         | React 18 + Vite + Tailwind CSS | Progressive Web App      |
| Backend          | FastAPI (Python 3.11)          | API Server               |
| Database         | Supabase PostgreSQL            | User data & analytics    |
| AI/LLM           | Groq Llama 3.3 + Whisper       | Feedback & transcription |
| State Management | Zustand                        | Frontend state           |
| Cache            | Redis                          | Sessions & performance   |
| Storage          | Cloudflare R2                  | Audio recordings         |
| Messaging        | Meta WhatsApp API              | OTP & notifications      |
| Blockchain       | Solana Devnet                  | Credential verification  |

---

# 📁 Project Structure

```bash
vani/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models/
│   │   ├── utils/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── websocket_manager.py
│   │
│   ├── migrations/
│   ├── requirements.txt
│   ├── .env
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── store/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env
│
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

* Python 3.11+
* Node.js 18+
* npm or yarn
* Supabase account
* Groq API key

---

# ⚙️ Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/vani.git

# Navigate to backend
cd vani/backend

# Create virtual environment
python -m venv venv

# Activate environment
# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

# 💻 Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start frontend
npm run dev
```

---

# 🔐 Environment Variables

## Backend `.env`

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_role_key

# JWT
JWT_SECRET_KEY=your_secret_key

# Groq AI
GROQ_API_KEY=your_groq_api_key

# App Config
APP_ENV=development
APP_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## Frontend `.env`

```env
VITE_API_URL=http://localhost:8000
```

---

# 📡 API Endpoints

| Category     | Endpoints                                                           |
| ------------ | ------------------------------------------------------------------- |
| Auth         | `/auth/otp/send`, `/auth/otp/verify`, `/auth/me`                    |
| Speech       | `/speech/transcribe`, `/speech/feedback`, `/speech/analyze-fluency` |
| Conversation | `/conversation/start`, `/conversation/respond`                      |
| Interview    | `/interview/questions`, `/interview/respond`                        |
| Tutors       | `/tutors/search`, `/tutor/session/book`                             |
| Progress     | `/progress/dashboard`, `/progress/skills`                           |
| Credentials  | `/credential/generate`, `/credential/verify`                        |

### Swagger Docs

```bash
http://localhost:8000/docs
```

---
# 🗄️ Database Setup (Supabase PostgreSQL)

Vani uses **Supabase PostgreSQL** as its primary database for storing:

* User profiles
* Conversation history
* Interview evaluations
* Tutor sessions
* Progress analytics
* Blockchain credentials

---

# 🚀 Setting Up Supabase

## 1. Create a Supabase Project

* Go to https://supabase.com
* Create a new project
* Copy:

  * `SUPABASE_URL`
  * `SUPABASE_SERVICE_KEY`

---

# 🔐 Backend Environment Variables

Add these to your backend `.env`:

```env id="ym6u9m"
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_service_role_key
```

---

# 🧱 Database Schema

Run the following SQL inside the **Supabase SQL Editor**.

## Open:

```text id="f7ng6z"
Supabase Dashboard → SQL Editor → New Query
```

Then paste the schema below and click **Run**.

---

# 📜 SQL Schema

```sql id="bme85w"
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(100),
    preferred_language VARCHAR(10) DEFAULT 'kn',
    district VARCHAR(100),
    is_tutor BOOLEAN DEFAULT FALSE,
    tutor_verified BOOLEAN DEFAULT FALSE,
    coins_balance INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW()
);

-- =========================
-- CONVERSATIONS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    feedback JSONB,
    fluency_score FLOAT,
    pronunciation_score FLOAT,
    grammar_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- INTERVIEWS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    ai_feedback JSONB,
    question_category VARCHAR(50),
    difficulty_level INT DEFAULT 1,
    score FLOAT,
    strengths JSONB,
    improvements JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- TUTORS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS tutors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    languages TEXT[] NOT NULL,
    hourly_rate INT NOT NULL,
    rating FLOAT DEFAULT 0,
    total_sessions INT DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    bio TEXT,
    availability JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- TUTOR SESSIONS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS tutor_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tutor_id UUID REFERENCES tutors(id) ON DELETE CASCADE,
    learner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'scheduled',
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_minutes INT,
    amount_paid INT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- PROGRESS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill VARCHAR(50) NOT NULL,
    score FLOAT DEFAULT 0,
    trend FLOAT DEFAULT 0,
    history JSONB DEFAULT '[]',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- CREDENTIALS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    certificate_id VARCHAR(50) UNIQUE NOT NULL,
    blockchain_tx_hash VARCHAR(100),
    level VARCHAR(20),
    skills JSONB,
    issued_at TIMESTAMP DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE
);

-- =========================
-- INDEXES
-- =========================
CREATE INDEX IF NOT EXISTS idx_users_phone
ON users(phone);

CREATE INDEX IF NOT EXISTS idx_conversations_user
ON conversations(user_id);

CREATE INDEX IF NOT EXISTS idx_interviews_user
ON interviews(user_id);

CREATE INDEX IF NOT EXISTS idx_progress_user
ON progress(user_id);
```

---

# 🔒 Recommended Supabase Features

## Enable Row Level Security (RLS)

For production deployment:

```sql id="6mv9x3"
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutors ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE credentials ENABLE ROW LEVEL SECURITY;
```

---

# 📦 Suggested Storage Buckets

Inside Supabase Storage, create:

| Bucket Name        | Purpose                        |
| ------------------ | ------------------------------ |
| `audio-recordings` | User speech recordings         |
| `profile-images`   | Tutor & learner profile photos |
| `certificates`     | Generated certificates         |

---

# 📊 Future Database Improvements

* Conversation embeddings for semantic search
* Analytics event tracking
* AI confidence scoring tables
* Tutor reputation system
* Gamification leaderboard tables
* Regional language datasets

---

# ✅ Database Ready

Once the schema is executed:

* Backend APIs can connect immediately
* Supabase auto-generates REST APIs
* Tables become available in dashboard
* Authentication can be integrated later

---

# 🧪 Demo Flow

## 1. Start Backend

```bash
cd backend
uvicorn main:app --reload
```

## 2. Start Frontend

```bash
cd frontend
npm run dev
```

## 3. Open Application

```bash
http://localhost:5173
```

## 4. Login

Use demo number:

```text
9876543210
```

Check backend terminal for OTP.

---

# 🔮 Future Scope

* 🎧 Emotion-aware speech analysis
* 🧑‍🏫 Live AI interview avatars
* 📶 Offline-first rural mode
* 🏢 Recruiter skill dashboards
* 🎓 College integration portal
* 🪪 Government skill verification
* 🌍 Support for 10+ Indian languages

---

# 👩‍💻 Team

| Role                   | Name          |
| ---------------------- | ------------- |
| Backend & Architecture | Fiona Dsouza  |
| AI & ML                | Smriti Dawane |
| Frontend & UI/UX       | Sneha         |

---

# 📚 Research & Inspiration

* ASER 2024 Education Reports
* IJERE 2021 Language Confidence Studies
* Rural employability studies in India


---

# 📜 License

MIT License

This project is open-source and free for academic and commercial use.

---

# ⭐ Support the Project

If you like this project:

* ⭐ Star the repository
* 🍴 Fork the project
* 🧠 Contribute features
* 🐛 Report issues

Together, we can make communication confidence accessible to everyone.
