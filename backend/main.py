from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from supabase import create_client
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import xgboost as xgb
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
encoder = SentenceTransformer("all-MiniLM-L6-v2")
match_model = xgb.XGBClassifier()
match_model.load_model("match_predictor.json")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

INTENTS = [
    "match programs to applicant profile",
    "search programs by location or state",
    "ask about application strategy or tips",
    "ask about visa sponsorship",
    "ask about observerships or clinical experience",
    "general residency question"
]

def classify_intent(message: str) -> str:
    result = classifier(message, INTENTS)
    return result["labels"][0]

def retrieve_programs(query: str, specialty: str = "", limit: int = 6):
    embedding = encoder.encode(query).tolist()
    if specialty:
        result = supabase.rpc("match_programs_by_specialty", {
            "query_embedding": embedding,
            "match_count": limit * 2,
            "filter_specialty": specialty
        }).execute()
        if result.data:
            # Deduplicate by name
            seen = set()
            unique = []
            for p in result.data:
                if p["name"] not in seen:
                    seen.add(p["name"])
                    unique.append(p)
            return unique[:limit]
    result = supabase.rpc("match_programs", {
        "query_embedding": embedding,
        "match_count": limit * 2
    }).execute()
    seen = set()
    unique = []
    for p in result.data:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
    return unique[:limit]

def format_programs(programs):
    return "\n".join([
        f"- {p['name']} ({p['location']}): "
        f"IMG friendly={p['img_friendly']}, "
        f"IMG match rate={p['match_rate_img']}, "
        f"visa={p['visa_sponsorship']}, "
        f"description: {p['description']}"
        for p in programs
    ])

def llm(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

class Profile(BaseModel):
    step2_score: int
    specialty: str
    grad_type: str

class ChatMessage(BaseModel):
    message: str
    specialty: str = ""

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/match")
def match(profile: Profile):
    query = f"{profile.specialty} {profile.grad_type} Step2 {profile.step2_score}"
    programs = retrieve_programs(query, profile.specialty)
    context = format_programs(programs)

    result = llm(f"""You are a residency match advisor using real NRMP 2026 data.

Applicant:
- Step 2 CK: {profile.step2_score}
- Specialty: {profile.specialty}
- Graduate type: {profile.grad_type}

Real program data:
{context}

Classify into reach, match, and safe programs with reasoning.""")

    # ML match probability
    is_img = 1 if "IMG" in profile.grad_type else 0
    avg_img_rate = sum(float(p["match_rate_img"] or 0) for p in programs) / len(programs) if programs else 0.3
    avg_img_friendly = 1 if sum(int(p["img_friendly"] or 0) for p in programs) / len(programs) > 0.5 else 0

    features = np.array([[
        profile.step2_score,
        0,
        0,
        is_img,
        avg_img_friendly,
        avg_img_rate
    ]])
    prob = match_model.predict_proba(features)[0][1]

    return {
        "result": result,
        "programs_used": [p["name"] for p in programs],
        "match_probability": round(float(prob), 3),
        "match_percentage": f"{round(float(prob) * 100, 1)}%",
        "tier": "strong" if prob > 0.7 else "moderate" if prob > 0.4 else "reach"
    }

@app.post("/chat")
def chat(msg: ChatMessage):
    intent = classify_intent(msg.message)
    programs_used = []

    if intent == "match programs to applicant profile":
        programs = retrieve_programs(msg.message, msg.specialty)
        context = format_programs(programs)
        programs_used = [p["name"] for p in programs]
        prompt = f"""You are a residency match advisor. The user asked: "{msg.message}"

Real NRMP 2026 program data:
{context}

Answer their question using this data."""

    elif intent == "search programs by location or state":
        programs = retrieve_programs(msg.message, msg.specialty)
        context = format_programs(programs)
        programs_used = [p["name"] for p in programs]
        prompt = f"""You are a residency program search assistant. The user asked: "{msg.message}"

Relevant programs from NRMP 2026:
{context}

List and describe the relevant programs."""

    elif intent == "ask about visa sponsorship":
        programs = retrieve_programs(msg.message + " visa H1B J1", msg.specialty)
        context = format_programs(programs)
        programs_used = [p["name"] for p in programs]
        prompt = f"""You are a residency visa advisor. The user asked: "{msg.message}"

Programs with visa data:
{context}

Answer their visa question using this data."""

    else:
        # General strategy / observership / other — pure LLM no retrieval
        prompt = f"""You are an expert residency application advisor for USMLE graduates and IMGs.
 The user asked: "{msg.message}"

Give a helpful, specific answer. If you mention any websites or links, only mention the main domain homepage (e.g. aamc.org, nrmp.org) — do not generate specific URLs or page paths as they may be inaccurate. Tell the user to search for the resource by name instead."""

    result = llm(prompt)
    return {
        "intent": intent,
        "result": result,
        "programs_used": programs_used
    }
class PredictRequest(BaseModel):
    step2_score: int
    usce_months: int = 0
    research_pubs: int = 0
    is_img: int = 1
    img_friendly_program: int = 1
    program_img_match_rate: float = 0.3

@app.post("/predict")
def predict(req: PredictRequest):
    features = np.array([[
        req.step2_score,
        req.usce_months,
        req.research_pubs,
        req.is_img,
        req.img_friendly_program,
        req.program_img_match_rate
    ]])
    prob = match_model.predict_proba(features)[0][1]
    return {
        "match_probability": round(float(prob), 3),
        "percentage": f"{round(float(prob) * 100, 1)}%",
        "tier": "strong" if prob > 0.7 else "moderate" if prob > 0.4 else "reach"
    }