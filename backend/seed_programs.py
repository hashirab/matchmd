from supabase import create_client
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
model = SentenceTransformer("all-MiniLM-L6-v2")

programs = [
    # Internal Medicine
    {"name": "Johns Hopkins IM", "specialty": "Internal Medicine", "location": "Baltimore, MD", "img_friendly": False, "avg_step2": 260, "match_rate_img": 0.05, "visa_sponsorship": "J1", "program_type": "University", "description": "Elite university internal medicine program, highly competitive, strong research focus, low IMG match rate."},
    {"name": "Montefiore Medical Center IM", "specialty": "Internal Medicine", "location": "New York, NY", "img_friendly": True, "avg_step2": 235, "match_rate_img": 0.40, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "Very IMG friendly internal medicine, diverse patient population, strong clinical training in New York."},
    {"name": "Brookdale Hospital IM", "specialty": "Internal Medicine", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 215, "match_rate_img": 0.65, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "IMG friendly community internal medicine program, diverse cases, good Step score flexibility."},

    # Family Medicine
    {"name": "UCLA Family Medicine", "specialty": "Family Medicine", "location": "Los Angeles, CA", "img_friendly": True, "avg_step2": 230, "match_rate_img": 0.35, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "Strong university family medicine program, IMG friendly, diverse patient population in LA."},
    {"name": "Adventist Health Family Medicine", "specialty": "Family Medicine", "location": "Lodi, CA", "img_friendly": True, "avg_step2": 210, "match_rate_img": 0.60, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "Very IMG friendly family medicine community program, high match rate for IMGs, flexible with scores."},
    {"name": "Creighton University Family Medicine", "specialty": "Family Medicine", "location": "Omaha, NE", "img_friendly": True, "avg_step2": 220, "match_rate_img": 0.50, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "IMG friendly family medicine program, good clinical training, moderate Step score requirements."},

    # Psychiatry
    {"name": "Johns Hopkins Psychiatry", "specialty": "Psychiatry", "location": "Baltimore, MD", "img_friendly": False, "avg_step2": 255, "match_rate_img": 0.08, "visa_sponsorship": "J1", "program_type": "University", "description": "Elite psychiatry program, very competitive, low IMG match rate, strong research focus."},
    {"name": "Kings County Hospital Psychiatry", "specialty": "Psychiatry", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 220, "match_rate_img": 0.55, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "IMG friendly psychiatry program, high volume of diverse psychiatric cases, good IMG match rate."},
    {"name": "Maimonides Medical Center Psychiatry", "specialty": "Psychiatry", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 215, "match_rate_img": 0.60, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "Very IMG friendly psychiatry program, strong clinical training, flexible with Step scores and gaps."},

    # Pediatrics
    {"name": "Boston Children's Hospital Pediatrics", "specialty": "Pediatrics", "location": "Boston, MA", "img_friendly": False, "avg_step2": 258, "match_rate_img": 0.05, "visa_sponsorship": "J1", "program_type": "University", "description": "Top tier pediatrics program, extremely competitive, rarely matches IMGs, strong research."},
    {"name": "SUNY Downstate Pediatrics", "specialty": "Pediatrics", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 225, "match_rate_img": 0.45, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "IMG friendly pediatrics program, diverse patient population, good clinical training in New York."},
    {"name": "Brookdale Hospital Pediatrics", "specialty": "Pediatrics", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 210, "match_rate_img": 0.65, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "Very IMG friendly community pediatrics program, high IMG match rate, flexible with Step scores."},

    # Emergency Medicine
    {"name": "UCSF Emergency Medicine", "specialty": "Emergency Medicine", "location": "San Francisco, CA", "img_friendly": False, "avg_step2": 258, "match_rate_img": 0.06, "visa_sponsorship": "J1", "program_type": "University", "description": "Elite emergency medicine program, very competitive, low IMG match rate, strong training."},
    {"name": "Lincoln Medical Center EM", "specialty": "Emergency Medicine", "location": "Bronx, NY", "img_friendly": True, "avg_step2": 225, "match_rate_img": 0.40, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "IMG friendly emergency medicine, high volume trauma center, good clinical exposure."},

    # Neurology
    {"name": "Mayo Clinic Neurology", "specialty": "Neurology", "location": "Rochester, MN", "img_friendly": False, "avg_step2": 260, "match_rate_img": 0.05, "visa_sponsorship": "J1", "program_type": "University", "description": "World renowned neurology program, extremely competitive, very low IMG match rate."},
    {"name": "Wayne State University Neurology", "specialty": "Neurology", "location": "Detroit, MI", "img_friendly": True, "avg_step2": 230, "match_rate_img": 0.40, "visa_sponsorship": "J1/H1B", "program_type": "University", "description": "IMG friendly neurology program, good clinical volume, moderate Step score requirements."},
    {"name": "Interfaith Medical Center Neurology", "specialty": "Neurology", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 215, "match_rate_img": 0.60, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "Very IMG friendly neurology community program, flexible with scores and gaps, high IMG acceptance."},

    # General Surgery
    {"name": "Johns Hopkins General Surgery", "specialty": "General Surgery", "location": "Baltimore, MD", "img_friendly": False, "avg_step2": 262, "match_rate_img": 0.03, "visa_sponsorship": "J1", "program_type": "University", "description": "Elite general surgery program, extremely competitive, almost never matches IMGs."},
    {"name": "Maimonides Medical Center Surgery", "specialty": "General Surgery", "location": "Brooklyn, NY", "img_friendly": True, "avg_step2": 235, "match_rate_img": 0.30, "visa_sponsorship": "J1/H1B", "program_type": "Community", "description": "IMG friendly general surgery program, high surgical volume, good training for IMGs."},
]

print("Generating embeddings and seeding programs...")

for program in programs:
    text = f"{program['name']} {program['specialty']} {program['location']} {program['description']}"
    embedding = model.encode(text).tolist()
    
    data = {**program, "embedding": embedding}
    result = supabase.table("programs").insert(data).execute()
    print(f"Inserted: {program['name']}")

print("Done! All programs seeded.")
