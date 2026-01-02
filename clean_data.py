
import csv
import re

def is_senior(title):
    title = title.lower()
    senior_keywords = [
        "chief", "ceo", "cto", "cfo", "coo", "cmo", "cro", "pres", "president", 
        "founder", "vp", "vice president", "head of", "director", "managing director",
        "svp", "evp"
    ]
    # Exclude if it looks like a low level role just containing a keyword? 
    # E.g. "Assistant to the VP" - but for now simple keyword match is likely fine for this dataset.
    
    # Filter out "not stated", "-", empty
    if not title or "not stated" in title or title.strip() == "-" or title.strip() == "–":
        return False
        
    return any(keyword in title for keyword in senior_keywords)

processed_rows = []

with open('data/raw.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
    # Skip header if present (heuristic)
    start_idx = 1 if "Name,Title" in lines[0] else 0
    
    for line in lines[start_idx:]:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split(',')
        if len(parts) < 4:
            continue
            
        # Heuristic: 
        # Name = parts[0]
        # URL = parts[-1]
        # Company = parts[-2]
        # Title = join(parts[1:-2])
        
        name = parts[0].strip()
        url = parts[-1].strip()
        company = parts[-2].strip()
        title = ", ".join(parts[1:-2]).replace('"', '').strip()
        
        # Clean specific bad values
        if "not stated" in company or not company or company == "–":
            continue
            

        if is_senior(title):
            # Scoring
            score = 0
            t_lower = title.lower()
            if "ceo" in t_lower or "chief executive officer" in t_lower or "founder" in t_lower:
                score = 10
            elif "chief" in t_lower or re.search(r'\bc[a-z]o\b', t_lower): # Matches CxO
                score = 9 
            elif "evp" in t_lower or "executive vice president" in t_lower:
                score = 8
            elif "svp" in t_lower or "senior vice president" in t_lower:
                score = 7
            elif "vp" in t_lower or "vice president" in t_lower:
                score = 6
            else:
                score = 5
                
            processed_rows.append({
                "Name": name,
                "Title": title,
                "Company": company,
                "YoutubeURL": url,
                "Score": score
            })

# Deduplicate by Name+Company
unique_rows = {}
for row in processed_rows:
    key = (row['Name'].lower(), row['Company'].lower())
    if key not in unique_rows:
        unique_rows[key] = row
    elif row['Score'] > unique_rows[key]['Score']: # Keep higher score duplicate? Unlikely to happen but good check
        unique_rows[key] = row

final_list = list(unique_rows.values())
# Sort by score desc
final_list.sort(key=lambda x: x['Score'], reverse=True)

# Take top 52 (buffer)
final_list = final_list[:52]

print(f"Selected {len(final_list)} top senior executives.")

# Save to CSV
with open('data/candidates.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Title", "Company", "YoutubeURL", "Score"])

    writer.writeheader()
    writer.writerows(final_list)
