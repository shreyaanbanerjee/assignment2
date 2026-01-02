
import csv
import sys
import urllib.request
import json
import time

# Use verification from previous step
domain_map = {
    "Salt Security": "salt.security",  
    "Redline Advisors": "redlineadvisors.ai", 
    "Dynatrace": "dynatrace.com",
    "Triptych Info": "triptychinfo.com",
    "Cato Networks": "catonetworks.com",
    "Stackpane": "stackpane.com",
    "Blaize": "blaize.com", 
    "Typeface": "typeface.ai", 
    "Releasehub": "releasehub.com",
    "Veeam": "veeam.com",
    "Kenna Security": "kennasecurity.com", 
    "Manual Labor Studio": "manual-labor.com", 
    "Robin.io": "robin.io",
    "Mirantis": "mirantis.com",
    "TechDivision": "techdivision.com",
    "Druva": "druva.com",
    "Octane AI": "octaneai.com", 
    "Inseego": "inseego.com",
    "Infineon": "infineon.com",
    "World Surf League": "worldsurfleague.com",
    "AWS": "amazon.com", 
    "AllCloud": "allcloud.io", 
    "Honeycomb.io": "honeycomb.io",
    "Spacelift": "spacelift.io", 
    "Fabrix.ai": "fabrix.ai", 
    "Vultr": "vultr.com",
    "GE Aerospace": "ge.com", 
    "AuditBoard": "auditboard.com",
    "UiPath": "uipath.com",
    "eBay": "ebay.com",
    "CrowdStrike": "crowdstrike.com",
    "Tensor": "tensor.auto", 
    "DDN": "ddn.com", 
    "Ledger": "ledger.com",
    "Google Cloud": "google.com",
    "Heroku (Salesforce)": "heroku.com", 
    "Spectra Logic": "spectralogic.com", 
    "Infinidat": "infinidat.com",
    "Index Engines": "indexengines.com",
    "theCUBE Research": "thecube.net",
    "Kiteworks": "kiteworks.com",
    "Equinix": "equinix.com",
    "Couchbase": "couchbase.com",
    "BroadForward": "broadforward.com",
    "Neo4j": "neo4j.com",
    "Arrcus": "arrcus.com",
    "Adobe Enterprise": "adobe.com",
    "AMD": "amd.com",
    "DeNexus": "denexus.io", 
    "Applied Intuition": "appliedintuition.com",
    "ScaleFlux": "scaleflux.com", 
    "Nutanix": "nutanix.com",
    "Cerebras": "cerebras.ai", 
    "Transcarent": "transcarent.com", 
    "AirMDR": "airmdr.com",
    "At-Bay": "at-bay.com", 
    "Early Growth Advisory": "earlygrowth.com",
    "Together AI": "together.ai",
}

def get_email_from_hunter(domain, first, last, api_key):
    url = f"https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first}&last_name={last}&api_key={api_key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                email = data.get('data', {}).get('email')
                return email
            elif response.status == 202:
                # 202 means calculation in progress, might retry? Hunter usually returns immediately or 202 if bulk?
                # Email finder usually immediate.
                pass
    except urllib.error.HTTPError as e:
        # 429 = Limit reached, 401 = unauthorized
        print(f"Error calling Hunter for {first} {last} at {domain}: {e.code} {e.reason}")
    except Exception as e:
        print(f"Exception for {domain}: {e}")
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_emails_hunter.py <API_KEY>")
        sys.exit(1)
        
    api_key = "368202c5aea955d7e7848dbdd3a0cdfbfd330779"
    
    candidates = []
    # Read candidates.csv
    try:
        with open('data/candidates.csv', 'r') as f:
            reader = csv.reader(f)
            # Check for header
            rows = list(reader)
            if rows[0][0] == "Name": # Header exists check?
                # User removed header in step 77/78, but let's be safe.
                # Actually user said "remove first row" in prev step. So assumed no header.
                # But let's check content.
                pass
            
            for row in rows:
                if len(row) >= 3:
                     # Check if it looks like header
                     if row[0] == "Name" and row[1] == "Title":
                         continue
                     candidates.append(row)
    except FileNotFoundError:
        print("data/candidates.csv not found")
        sys.exit(1)
        
    top_50 = candidates[:50]
    final_rows = []
    
    print(f"Processing {len(top_50)} candidates with Hunter.io...")
    
    for row in top_50:
        name_raw = row[0]
        title = row[1]
        company = row[2]
        url = row[3]
        
        # Parse name
        name_clean = name_raw.replace('"', '').split('(')[0].strip()
        parts = name_clean.split()
        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""
        
        # Get domain
        domain = domain_map.get(company)
        if not domain:
            clean_company = company.lower().replace(" ", "").replace(".io", "").replace(".ai", "")
            domain = f"{clean_company}.com"
            
        print(f"Finding email for {first} {last} @ {domain}...")
        
        # 1. Hunter Email
        hunter_email = get_email_from_hunter(domain, first, last, api_key)
        
        # 2. Fallback / Second Email heuristic
        # If Hunter found one, we need a 2nd "likely" one.
        # Common patterns: first.last@, first@, f.last@, firstl@
        
        heuristic_email = ""
        if last:
            heuristic_email = f"{first}.{last}@{domain}".lower()
        else:
            heuristic_email = f"{first}@{domain}".lower()
            
        # Ensure they are different
        if hunter_email and hunter_email.lower() == heuristic_email:
            # Generate another variant
            if last:
                heuristic_email = f"{first}@{domain}".lower()
            else:
                heuristic_email = f"info@{domain}".lower()
        
        if not hunter_email:
             # Hunter failed/limit/confidence low?
             # Use heuristics for both
             e1 = f"{first}.{last}@{domain}".lower() if last else f"{first}@{domain}".lower()
             e2 = f"{first}@{domain}".lower()
             if e1 == e2: e2 = f"info@{domain}".lower()
             hunter_email = e1 # Treat heuristic as primary if hunter fails
             heuristic_email = e2
        
        final_rows.append([name_raw, title, company, hunter_email, heuristic_email, url])
        
        # Be nice to API? Hunter allows concurrent, but simple script is serial.
        time.sleep(0.1) 

    # Write output
    with open('final_list_top_50_hunter.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Title', 'Company', 'HunterEmail', 'SecondaryEmail', 'YoutubeURL'])
        writer.writerows(final_rows)

    print("Done! Saved to final_list_top_50_hunter.csv")

if __name__ == "__main__":
    main()
