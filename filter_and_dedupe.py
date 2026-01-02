
import csv
import re

def is_senior(title):
    if not title: return False
    title = title.lower()
    senior_keywords = [
        "chief", "ceo", "cto", "cfo", "coo", "cmo", "cro", "pres", "president", 
        "founder", "vp", "vice president", "head of", "director", "managing director",
        "svp", "evp", "executive", "principal", "partner", "chair"
    ]
    
    # Exclude invalid/placeholder titles
    if "not stated" in title or title.strip() in ["-", "–", ""]:
        return False
        
    return any(keyword in title for keyword in senior_keywords)

def calculate_priority_score(title):
    title = title.lower()
    if "ceo" in title or "chief executive" in title or "founder" in title:
        return 10
    if "chief" in title or re.search(r'\bc[a-z]o\b', title): # C-suite
        return 9
    if "evp" in title or "executive vice president" in title:
        return 8
    if "svp" in title or "senior vice president" in title:
        return 7
    if "vp" in title or "vice president" in title:
        return 6
    return 5

candidates = []

with open('data/cleaned.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['Name'].strip()
        title = row['Title'].strip()
        company = row['Company'].strip()
        url = row['YoutubeURL'].strip()
        
        # Check for null/empty
        if not name or not title or not company:
            continue
            
        if "not stated" in company or company in ["-", "–"]:
            continue
            
        if is_senior(title):
            row['Score'] = calculate_priority_score(title)
            candidates.append(row)

# Deduplicate
# Key: Name + Company
unique_candidates = {}
for c in candidates:
    key = (c['Name'].lower(), c['Company'].lower())
    
    # If duplicate, keep the one with better data or higher score?
    # Usually just first seen or verify. 
    # Let's keep the one with higher score if multiple (unlikely for same name/company but possible if dirty data)
    
    if key not in unique_candidates:
        unique_candidates[key] = c
    else:
        if c['Score'] > unique_candidates[key]['Score']:
            unique_candidates[key] = c

final_list = list(unique_candidates.values())

# Sort by Score Descending
final_list.sort(key=lambda x: x['Score'], reverse=True)

print(f"Filtered down to {len(final_list)} senior executives.")

with open('data/candidates.csv', 'w', newline='') as f:
    fieldnames = ['Name', 'Title', 'Company', 'YoutubeURL', 'Score']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_list)
