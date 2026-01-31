# NIMIS - Smart Address Intelligence Hackathon Project

A comprehensive solution for normalizing, geocoding, and analyzing unstructured addresses in India using rule-based NLP and landmark matching.

##  Tech Stack

- **Frontend:** React 18, Vite, TailwindCSS, Radix UI
- **Backend:** Python 3, Flask, SQLAlchemy, Psycopg
- **Database:** PostgreSQL (Supabase recommended)
- **Key Libraries:** RapidFuzz (String matching), React-Leaflet (Maps)

---

##  Prerequisites

Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) & [Bun](https://bun.sh/) (or npm)
- [Python 3.8+](https://www.python.org/)
- A [Supabase](https://supabase.com/) project (or any PostgreSQL database)

---

##  Setup Instructions

### 1. Backend Setup

The backend handles address parsing and geocoding logic.

#### **Step A: Navigate to backend**
```bash
cd backend
```

#### **Step B: Create Virtual Environment**

**🐧 Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**🪟 Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

#### **Step C: Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **Step D: Configure Environment Variables**
Create a new file named `.env` inside the `backend/` folder and paste the following:

```env
# Database Connection (Required)
SUPABASE_DATABASE_URL=postgresql://postgres.your-ref:password@aws-0-region.pooler.supabase.com:6543/postgres

# App Settings
FLASK_DEBUG=True
SECRET_KEY=change_this_to_something_secure
DEFAULT_CITY=Indore
```
> **Note:** Replace `SUPABASE_DATABASE_URL` with your actual connection string from Supabase (Transaction Pooler connection recommended).

#### **Step E: Initialize Database**
Run these commands to create tables and add sample data:
```bash
flask init-db
flask seed-db
```

#### **Step F: Run the Server**
```bash
python app.py
```
 The backend will start at `http://localhost:5000`

---

### 2. Frontend Setup

The frontend provides the user interface for inputting addresses.

Open a **new terminal** and navigate to the project root (if you are in `backend`, go back one level).

#### **Step A: Install Dependencies**
We recommend using `bun` for faster installation, but `npm` works too.

```bash
# Using Bun (Recommended)
bun install

# OR using npm
npm install
```

#### **Step B: Run Development Server**
```bash
# Using Bun
bun run dev

# OR using npm
npm run dev
```

 The frontend will start at `http://localhost:5173` (or similar port).

---

## ✨ How to Use

1. Open your browser and go to the frontend URL (e.g., `http://localhost:5173`).
2. You will see a map and an input form.
3. Enter an unstructured address (e.g., *"Near Apollo Hospital, Vijay Nagar, Indore"*).
4. Click **Analyze**.
5. The system will:
   - Normalize the address text.
   - Identify landmarks.
   - Plot the estimated location on the map.
   - Provide a confidence score for the prediction.

##  Project Structure

```
NIMIS-HACKATHON/
├── backend/               # Flask Application
│   ├── app.py             # Entry point
│   ├── routes/            # API Endpoints
│   ├── services/          # Core Logic (Geocoding, Normalization)
│   └── database/          # DB Models
├── geospatial_nlp/        # ML/NLP Research Notebooks & Scripts
├── src/                   # React Frontend Source (in root)
├── public/                # Static assets
└── README.md              # This file
```
