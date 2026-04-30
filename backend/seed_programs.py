from supabase import create_client
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
model = SentenceTransformer("all-MiniLM-L6-v2")

programs = [
    {"name": "Johns Hopkins IM", "specialty": "Internal Medicine", "location": "Baltimore, MD", "img_friendly": False, "avg_step2": 260, "match_rate_img": 0.05, "visa_sponsorship": "J1", "program_type": "University", "description": "Elite university program, highly competitive, strong research focus, low IMG match rate."},
    {"name": "Massachusetts General Hospital IM", "specialty": "Internal Medicine", "location": "Boston, MA", "img_friendly": False, "avg_step2": 262, "match_rate_img": 0.04, "visa_sponsorship": "J1", "program_type": "University", "description": "Top tier Harvard program, extremely competitive, research heavy, rarely matches IMGs."},
    {"name": "UCSF Internal Medicine", "specialty": "Internal Medicine", "location": "San Francisco, CA", "img_friendly": False, "avg_step2": 258, "match_rate_img": 0.06, "visa_sponsorship": "J1", "program_type": "University", "description": "Prestigious west coast program, very competitive, strong clinical and research training."},
    {"name": "University of Chicago IM", "specialty": "Internal Medicine", "location": "Chicago, IL", "img_friendly": True, "avg_step2": 250, "match_rate_img": 0.15, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "Strong university program, moderately IMG friendly, good research opportunities."},
    {"name": "Cleveland Clinic IM", "specialty": "Internal Medicine", "location": "Cleveland, OH", "img_friendly": True, "avg_step2": 245, "match_rate_img": 0.20, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "Renowned clinical program, accepts IMGs, strong cardiology exposure."},
    {"name": "Montefiore Medical Center IM", "specialty": "Internal Medicine", "location": "New York, NY", "img_friendly": True, "avg_step2": 235, "match_rate_img": 0.40, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "Very IMG friendly, diverse patient population, strong clinical training in New York."},
    {"name": "Lincoln Medical Center IM", "specialty": "Internal Medicine", "location": "Bronx, NY", "img_friendly": True, "avg_step2": 220, "match_rate_img": 0.60, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "Community program, highly IMG friendly, good clinical volume, safety net hospital."},
    {"name": "Brookdale Hospital IM", "specialty": "Internal Medicine", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 215, "match_rate_img": 0.65, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "IMG friendly community program, diverse cases, good Step score flexibility."},
    {"name": "Interfaith Medical Center IM", "specialty": "Internal Medicine", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 210, "match_rate_img": 0.70, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "Safe community program for IMGs, flexible with gaps, good step score range."},
    {"name": "University of Florida IM", "specialty": "Internal Medicine", "location": "Gainesville, FL", "img_friendly": True, "avg_step2": 245, "match_rate_img": 0.25, "visa_sponsorship": "J1", "program_type": "University", "description": "State university program, moderately IMG friendly, good clinical training."},
]

print("Generating embeddings and seeding programs...")

for program in programs:
    text = f"{program['name']} {program['specialty']} {program['location']} {program['description']}"
    embedding = model.encode(text).tolist()
    
    data = {**program, "embedding": embedding}
    result = supabase.table("programs").insert(data).execute()
    print(f"Inserted: {program['name']}")

print("Done! All programs seeded.")
