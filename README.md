# Real Estate Triage Agent

A helpful real estate assistant that collects lead information from Buyers, Sellers, and Renters. Available as a **CLI** or **Web App** with a chat interface.

## Quick Start (Local)

### 1. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Set your API keys

```bash
export GOOGLE_API_KEY="your-google-api-key"   # For AI welcome message
```

### 3. (Optional) Google Sheets for leads

To save leads to Google Sheets instead of CSV:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **Google Sheets API**
3. **APIs & Services → Credentials** → Create **Service Account**
4. Create a key (JSON) and download it → save as `credentials.json`
5. Create a Google Sheet → Share it with the service account email (e.g. `xxx@project.iam.gserviceaccount.com`) with **Editor** access
6. Copy the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

```bash
export GOOGLE_SHEET_ID="your-sheet-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

If these are not set, leads are saved to `leads.csv` instead.

### 4. Run the web app

```bash
python3 app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### Or run the CLI

```bash
python3 agent.py
```

---

## Deploy to the Cloud

### Option A: Render (Free tier, recommended for beginners)

1. Push your code to **GitHub** (create a repo and push).
2. Go to [render.com](https://render.com) and sign up.
3. Click **New → Web Service**.
4. Connect your GitHub repo.
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Add Environment Variables:** `GOOGLE_API_KEY`, and for Sheets: `GOOGLE_SHEET_ID`, `GOOGLE_APPLICATION_CREDENTIALS` (path to your service account JSON; on Render, use Secret Files to upload it)
6. Click **Create Web Service**. Render will build and deploy. You'll get a URL like `https://yourapp.onrender.com`.

### Option B: Railway

1. Push your code to **GitHub**.
2. Go to [railway.app](https://railway.app) and sign up.
3. Click **New Project → Deploy from GitHub**.
4. Select your repo. Railway auto-detects Python.
5. Go to **Variables** and add `GOOGLE_API_KEY`.
6. Your app will be live at a generated URL.

### Option C: PythonAnywhere (Free tier)

1. Create an account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Open a Bash console and clone your repo (or upload files).
3. Create a virtualenv and install: `pip install -r requirements.txt`
4. In the **Web** tab, add a new web app (Flask), point it to your project.
5. Set `GOOGLE_API_KEY` in the Web app's environment variables.

---

## Project Structure

```
RealEstateAgent/
├── app.py           # Flask web application
├── agent.py         # CLI interface
├── agent_logic.py   # Core triage logic (shared)
├── requirements.txt
├── Procfile         # For deployment (Render, Heroku)
├── runtime.txt      # Python version for deployment
├── templates/
│   └── index.html   # Chat UI
├── static/
│   └── style.css
└── leads.csv        # Saved leads (created on first save)
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Your Google Gemini API key |
| `GOOGLE_SHEET_ID` | No | Google Sheet ID (for saving leads to Sheets) |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Path to service account JSON (for Sheets) |
| `PORT` | No | Server port (default: 5000) |
| `SECRET_KEY` | No | Flask secret (for production) |

---

## Lead Data

Completed leads are saved to **Google Sheets** (if configured) or **leads.csv** with columns:
`timestamp`, `type`, `budget`, `location`, `property_type`, `address`, `expected_price`, `urgency`, `monthly_budget`, `move_in_date`
