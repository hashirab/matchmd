import pdfplumber
import re
from supabase import create_client
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
model = SentenceTransformer("all-MiniLM-L6-v2")

def parse_nrmp(pdf_path):
    programs = []
    current_state = None

    state_pattern = re.compile(r'^([A-Z][A-Z\s]+(?:\s\(cont\.\))?)\s+Pos\.')
    row_pattern = re.compile(
        r'^(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)'
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                # Detect state header
                state_match = re.match(r'^([A-Z]{2,}(?:\s[A-Z]+)*)\s+Pos\.', line)
                if state_match:
                    state_raw = state_match.group(1).replace('(cont.)', '').strip()
                    current_state = state_raw
                    continue

                # Skip header/footer lines
                if any(skip in line for skip in ['Key:', 'Reproduction', 'NRMP', 'Applicant', 'Page']):
                    continue

                # Parse data rows
                row_match = row_pattern.match(line.strip())
                if row_match and current_state:
                    specialty = row_match.group(1).strip()
                    # Clean specialty name
                    specialty = re.sub(r'\s*\(PGY-\d+\).*', '', specialty).strip()
                    specialty = re.sub(r'\s*\(Integrated\).*', '', specialty).strip()
                    specialty = re.sub(r'\s*\(Physician\).*', '', specialty).strip()

                    try:
                        positions = int(row_match.group(2))
                        filled = int(row_match.group(3))
                        img = int(row_match.group(8))
                        pct_md_sr = float(row_match.group(11))
                        pct_tot = float(row_match.group(12))

                        if positions < 1:
                            continue

                        img_rate = round(img / positions, 2) if positions > 0 else 0
                        img_friendly = img_rate > 0.15

                        programs.append({
                            "name": f"{specialty} — {current_state}",
                            "specialty": specialty,
                            "location": current_state,
                            "img_friendly": img_friendly,
                            "avg_step2": None,
                            "match_rate_img": img_rate,
                            "visa_sponsorship": "J1/H1B" if img_friendly else "J1",
                            "program_type": "University",
                            "description": f"{specialty} program in {current_state}. "
                                         f"Positions: {positions}, Filled: {filled}, "
                                         f"IMG matched: {img}, IMG match rate: {img_rate:.0%}, "
                                         f"Fill rate: {pct_tot}%, MD senior fill rate: {pct_md_sr}%."
                        })
                    except (ValueError, ZeroDivisionError):
                        continue

    return programs

print("Parsing NRMP PDF...")
programs = parse_nrmp("nrmp_data.pdf")
print(f"Parsed {len(programs)} programs")

# Clear existing data
print("Clearing existing programs...")
supabase.table("programs").delete().neq("id", 0).execute()

# Seed in batches
print("Generating embeddings and seeding...")
batch_size = 20
for i in range(0, len(programs), batch_size):
    batch = programs[i:i+batch_size]
    for p in batch:
        text = f"{p['name']} {p['specialty']} {p['location']} {p['description']}"
        p["embedding"] = model.encode(text).tolist()
    supabase.table("programs").insert(batch).execute()
    print(f"Seeded {min(i+batch_size, len(programs))}/{len(programs)}")

print("Done!")
