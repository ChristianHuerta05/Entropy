# Entropy

**AI-Powered Security Auditor** — Paste a URL, watch an AI agent navigate your site, get a vulnerability report.

---

## Features

- **Zero Configuration** — Just enter a URL and click scan
- **Visual AI Agent** — Watch the browser navigate in real-time
- **Live Terminal Logs** — live streaming output via Firebase
- **Structured Reports** — JSON-based vulnerability reports with risk levels
- **XSS & SQLi Testing** — Automated payload injection and analysis

---

## Tech Stack

| Layer        | Technology                                                                  |
| ------------ | --------------------------------------------------------------------------- |
| **Frontend** | React 19, Vite, Tailwind CSS v4                                             |
| **Backend**  | Python, FastAPI, Uvicorn                                                    |
| **AI Agent** | [browser-use](https://github.com/browser-use/browser-use), Gemini 2.5 Flash |
| **Database** | Firebase Firestore (live logs)                                              |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud GeminiAPI Key
- Firebase Project

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your GOOGLE_API_KEY to .env

# Add Firebase service account
# Place your service-account.json in the backend/ directory

# Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS="./service-account.json"

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Environment Variables

### Backend (`.env`)

```
GOOGLE_API_KEY=your_gemini_api_key
```

### Firebase

Place your `service-account.json` in the `backend/` directory.

Update `frontend/src/firebase.js` with your Firebase web config.

---

## 🎯 How It Works

1. **User submits a URL** via the React frontend
2. **Backend spawns an AI agent** using browser-use + Gemini
3. **Agent navigates the site** in a visible Chrome window
4. **Real-time logs stream** to Firestore → React UI
5. **Agent tests for vulnerabilities** (XSS, SQLi, info disclosure)
6. **Structured report generated** and displayed in the UI

---

## 📊 Report Format

```json
{
  "target": "https://example.com",
  "risk_level": "MEDIUM",
  "vulnerabilities": [
    {
      "type": "XSS",
      "location": "search bar",
      "severity": "HIGH",
      "description": "Reflected XSS via script tag"
    }
  ],
  "inputs_tested": [...],
  "pages_visited": [...],
  "recommendations": [...]
}
```

---

## Disclaimer

This tool is for **educational and authorized security testing only**. Only scan websites you own or have explicit permission to test. Unauthorized scanning may violate laws and terms of service.

---

## Hackathon

Built at CruzHacks 2026

---

## License

MIT
