# MatchMD — AI-Powered Residency Match Advisor

Full-stack AI application helping USMLE graduates find best-match residency programs using RAG, intent classification, and a trained ML model.

## Architecture

User query → Intent Classifier (BART) → Route to handler → RAG retrieval (pgvector) → LLM (Llama 3.3) → Response + ML probability score

## Key Features

- **RAG pipeline** — 1,062 real NRMP 2026 programs embedded with sentence-transformers, stored in PostgreSQL/pgvector, retrieved at query time to ground LLM responses in real match data
- **Intent classifier** — zero-shot BART model routes queries across 6 categories (match finder, program search, visa, strategy, observerships, general)
- **XGBoost match predictor** — supervised ML model (ROC-AUC: 0.96) predicting match probability from applicant features, tracked with MLflow
- **NRMP scraper** — automated PDF parser extracting real 2026 match data across all 50 states and all ACGME specialties

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| AI/LLM | Groq API, Llama 3.3 70B |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | PostgreSQL + pgvector (Supabase) |
| ML Model | XGBoost, scikit-learn, MLflow |
| Intent | facebook/bart-large-mnli |

## Model Performance

| Metric | Score |
|---|---|
| Accuracy | 91.5% |
| ROC AUC | 0.960 |
| CV AUC (5-fold) | 0.961 ± 0.001 |
| Eval pass rate | 10/10 (100%) |

## Running Locally

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Environment variables — create `backend/.env`:**
## API Endpoints

- `POST /match` — profile-based program matching with ML probability score
- `POST /chat` — intent-classified conversational advisor
- `POST /predict` — standalone match probability prediction
- `GET /health` — health check

## Project Structure
matchmd/
├── backend/
│   ├── main.py              # FastAPI app — all endpoints
│   ├── train_model.py       # XGBoost training + MLflow tracking
│   ├── scrape_nrmp.py       # NRMP PDF scraper + embeddings
│   ├── seed_programs.py     # Manual program seeder
│   ├── match_predictor.json # Trained XGBoost model
│   └── mlruns/              # MLflow experiment logs
└── frontend/
└── app/page.tsx         # Next.js UI

