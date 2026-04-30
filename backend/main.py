from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from supabase import create_client
from sentence_transformers import SentenceTransformer
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

class Profile(BaseModel):
    step2_score: int
    specialty: str
    grad_type: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/match")
def match(profile: Profile):
    # Step 1: Embed the user query
    query = f"{profile.specialty} {profile.grad_type} Step2 {profile.step2_score}"
    embedding = encoder.encode(query).tolist()

    # Step 2: Retrieve top matching programs from Supabase
    result = supabase.rpc("match_programs", {
        "query_embedding": embedding,
        "match_count": 6
    }).execute()

    programs = result.data
    context = "\n".join([
        f"- {p['name']} ({p['location']}): avg Step2={p['avg_step2']}, "
        f"IMG friendly={p['img_friendly']}, IMG match rate={p['match_rate_img']}, "
        f"visa={p['visa_sponsorship']}, type={p['program_type']}"
        for p in programs
    ])

    # Step 3: Call Llama 3 with retrieved context
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""You are a residency match advisor. Use the real program data below to recommend programs.

Applicant profile:
- Step 2 CK: {profile.step2_score}
- Specialty: {profile.specialty}
- Graduate type: {profile.grad_type}

Real program data:
{context}

Based on this data, classify the programs into reach, match, and safe categories for this applicant. Explain your reasoning for each."""
        }]
    )
    return {
        "result": response.choices[0].message.content,
        "programs_used": [p["name"] for p in programs]
    }