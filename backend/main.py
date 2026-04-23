from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
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

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Profile(BaseModel):
    step2_score: int
    specialty: str
    grad_type: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/match")
def match(profile: Profile):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{
            "role": "user",
            "content": f"""You are a residency match advisor. Analyse this applicant:
- Step 2 CK: {profile.step2_score}
- Specialty: {profile.specialty}
- Graduate type: {profile.grad_type}

Give 3 reach, 3 match, and 3 safe program recommendations with brief reasons."""
        }]
    )
    return {"result": response.choices[0].message.content}
