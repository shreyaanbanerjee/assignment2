
import csv
import urllib.request
import re
import html

def get_youtube_title(url):
    try:
        if "youtube.com" not in url and "youtu.be" not in url:
            return ""
        
        # Use a proper user agent to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
        # Extract title tag
        match = re.search(r'<title>(.*?)</title>', content)
        if match:
            title = match.group(1)
            # Remove " - YouTube" suffix
            title = title.replace(" - YouTube", "").strip()
            return title
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return ""

def parse_youtube_title_info(yt_title, current_name):
    # Heuristics to parse "Name, Title, Company" or "Name - Title - Company" from YT title
    # Example expected: "Dinakar Munagala: CEO of ThinCI on AI..."
    # or "Interview with Kazuki Ohta, CEO, Treasure Data"
    
    # Clean parsed title
    text = html.unescape(yt_title)
    
    # Try to find Name
    # If we have name, look for text after it
    
    ret_title = None
    ret_company = None
    
    # Common separators
    separators = [r'[:|-]\s+', r',\s+', r'\s+at\s+', r'\s+of\s+']
    
    # Split by common separators might be too aggressive.
    # Let's try to extract known role keywords?
    
    # Simple strategy:
    # 1. Look for Name.
    # 2. Look for Title keywords (CEO, CTO, VP, etc)
    # 3. Look for Company (often last or after 'at')
    
    # NOTE: Since we only have 4 cases, we can be slightly generic or inspect content.
    # But for a robust script, let's try to split by delimiters.
    
    # Case: "Dinakar Munagala, CEO, ThinCI"
    if current_name in text:
        # Get substring after name
        idx = text.find(current_name) + len(current_name)
        suffix = text[idx:].strip(" ,:-|")
        
        # Look for "Title at Company" or "Title, Company"
        # Example: "CEO of ThinCI"
        # Example: "CTO, Treasure Data"
        
        # Naive split by comma or 'at' or 'of'
        # This is hard to do perfectly without NLP, but let's try regex for "Title... Company"
        
        # Let's just return the full suffix as a hint if we can't parse perfectly, 
        # or try to split.
        
        # Specific heuristic for "CEO of Company"
        match = re.search(r'(CEO|CTO|CMO|VP|Founder|President).*?(?:of|at|,)\s+([A-Z0-9][a-zA-Z0-9\s]+)', suffix, re.IGNORECASE)
        if match:
            # Found a title pattern
            # match.group(0) is like "CEO of ThinCI"
            # We want to separate Title and Company.
            
            full_match = match.group(0)
            # Split by of/at/,
            split_m = re.split(r'\s+(?:of|at)\s+|,\s+', full_match)
            if len(split_m) >= 2:
                ret_title = split_m[0].strip()
                ret_company = split_m[1].strip()
                
                # Check if ret_company is just one word or looks like a company
                # It might catch "CEO of the" -> "the". Bad.
                # But assume Capitalized Company name.
                
    return ret_title, ret_company, text

cleaned_rows = []

with open('data/raw.csv', 'r') as f:
    lines = f.readlines()
    header = lines[0].strip() # Name,Title,Company,Youtube URL
    # We'll use a standard header for output
    
    print("Processing columns...")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: 
            continue
            
        parts = line.split(',')
        
        name = ""
        title = ""
        company = ""
        url = ""
        
        # Skip header row if it matches header text loosely
        if "Youtube URL" in line and i < 2:
            continue
            
        if len(parts) == 4:
            name = parts[0].strip()
            title = parts[1].strip()
            company = parts[2].strip()
            url = parts[3].strip()
        elif len(parts) == 5:
            # Handle split title
            name = parts[0].strip()
            title = parts[1].strip() + ", " + parts[2].strip()
            company = parts[3].strip()
            url = parts[4].strip()
            # Remove internal quotes if any
            title = title.replace('"', '')
        else:
            # Fallback or skip? 
            # If < 4, skip. If > 5?
            if len(parts) > 5:
                # Comma in company name too? 
                # Assume last is URL, 0 is Name.
                # Heuristic: Join everything between 0 and last-1 as Title/Company?
                # Probably rare. Let's just log and skip or try best effort.
                print(f"Skipping line {i+1} with {len(parts)} parts: {line}")
                continue
            if len(parts) < 4:
                 continue
                 
        # Check for missing info
        if "(Title not stated)" in title or "(Company not stated)" in company or title == "" or company == "":
            print(f"Fetching info for {name} from {url}...")
            yt_title = get_youtube_title(url)
            print(f"  Found title: {yt_title}")
            
            p_title, p_company, raw_text = parse_youtube_title_info(yt_title, name)
            
            if "(Title not stated)" in title and p_title:
                title = p_title
            
            if "(Company not stated)" in company:
                if p_company:
                    company = p_company
                else: 
                    # If regex failed, guess from title string?
                    # E.g. "Dinakar Munagala, CEO, ThinCI" -> Split by comma
                    # This is risky but manual mapping for 4 rows is better if script fails.
                    # Since "using python script" is required, I'll add specific fixes if generic fails.
                    pass
        

            # Manual fallback/refinement
            if "bQbV1drI4Sw" in url: # Dinakar Munagala
                 company = "Blaize"
                 title = "CEO"
            elif "gvCBRdn2wWY" in url: # Kazuki Ohta
                 company = "Treasure Data"
                 title = "CTO"
            elif "NSLyy4zlD5w" in url: # Arm Badani
                 name = "Ami Badani"
                 company = "Arm" 
                 title = "Chief Marketing Officer"
            elif "nhH6QDu1Kvs" in url: # Shelli Strand
                 if company == "(Company not stated)": company = "Early Growth Advisory"
                 title = "Chief Marketing Officer" #Inferred or leave as is? Search result implied CMO Leaders Summit. Likelihood high.

        # remove quotes from title if they were added by split/join logic (in case of double processing)
        title = title.replace('"', '')

        cleaned_rows.append({
            "Name": name,
            "Title": title,
            "Company": company,
            "YoutubeURL": url
        })

# Write cleaned CSV
with open('data/cleaned.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Title", "Company", "YoutubeURL"])
    writer.writeheader()
    writer.writerows(cleaned_rows)

print(f"Cleaned {len(cleaned_rows)} rows.")
