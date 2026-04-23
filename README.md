# MatchMD — AI-Powered Residency Match Advisor

An end-to-end AI application that helps USMLE graduates find their best-match residency programs.

## Tech Stack
- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, Uvicorn
- AI: Groq API (Llama 3)

## Running Locally

Backend:
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  uvicorn main:app --reload

Frontend:
  cd frontend
  npm install
  npm run dev

## Environment Variables
Create backend/.env with:
  GROQ_API_KEY=your-groq-api-key

## Roadmap
- RAG pipeline with real NRMP match data
- Evals framework
- User profiles and application tracker
- Streaming AI responses