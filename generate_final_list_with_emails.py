
import csv

# Known domains map based on verification
domain_map = {
    "Salt Security": "salt.security",  # Verified
    "Redline Advisors": "redlineadvisors.ai", # Verified .ai (or .com redirect). .ai safer as primary? Source said .ai
    "Dynatrace": "dynatrace.com",
    "Triptych Info": "triptychinfo.com",
    "Cato Networks": "catonetworks.com",
    "Stackpane": "stackpane.com",
    "Blaize": "blaize.com", # Verified
    "Typeface": "typeface.ai", # Verified typeface.ai is AI content platform. Abhay Parasnis is CEO of Typeface.ai.
    "Releasehub": "releasehub.com",
    "Veeam": "veeam.com",
    "Kenna Security": "kennasecurity.com", # Acquired by Cisco but domain likely active or alias
    "Manual Labor Studio": "manual-labor.com", # Verified
    "Robin.io": "robin.io",
    "Mirantis": "mirantis.com",
    "TechDivision": "techdivision.com",
    "Druva": "druva.com",
    "Octane AI": "octaneai.com", # Site is octaneai.com
    "Inseego": "inseego.com",
    "Infineon": "infineon.com",
    "World Surf League": "worldsurfleague.com",
    "AWS": "amazon.com", # Safest for AWS execs? Or aws.com? Usually amazon.com for employees. Julia White is AWS.
    "AllCloud": "allcloud.io", # Verified
    "Honeycomb.io": "honeycomb.io",
    "Spacelift": "spacelift.io", # Verified
    "Fabrix.ai": "fabrix.ai", # Verified
    "Vultr": "vultr.com",
    "GE Aerospace": "ge.com", # Or geaerospace.com? Jan Murry. GE is complex. Let's try ge.com or ge.com
    "AuditBoard": "auditboard.com",
    "UiPath": "uipath.com",
    "eBay": "ebay.com",
    "CrowdStrike": "crowdstrike.com",
    "Tensor": "tensor.auto", # Verified for Amy Luca
    "DDN": "ddn.com", # Verified
    "Ledger": "ledger.com",
    "Google Cloud": "google.com",
    "Heroku (Salesforce)": "heroku.com", # Verified
    "Spectra Logic": "spectralogic.com", # Verified
    "Infinidat": "infinidat.com",
    "Index Engines": "indexengines.com",
    "theCUBE Research": "thecube.net", # Previously seen "theCUBE" often siliconangle.com or thecube.net. Let's guess siliconangle.com? Or thecube.research? 
    # Christophe Bertrand is Analyst. Probably thecube.net or siliconangle.com. Let's use thecube.net (common).
    "Kiteworks": "kiteworks.com",
    "Equinix": "equinix.com",
    "Couchbase": "couchbase.com",
    "BroadForward": "broadforward.com",
    "Neo4j": "neo4j.com",
    "Arrcus": "arrcus.com",
    "Adobe Enterprise": "adobe.com",
    "AMD": "amd.com",
    "DeNexus": "denexus.io", # Verified
    "Applied Intuition": "appliedintuition.com",
    "ScaleFlux": "scaleflux.com", # Verified
    "Nutanix": "nutanix.com",
    "Cerebras": "cerebras.ai", # Verified
    "Transcarent": "transcarent.com", # Verified in head?
    "AirMDR": "airmdr.com", # Verified

    "At-Bay": "at-bay.com", 
    "Early Growth Advisory": "earlygrowth.com",
    "Together AI": "together.ai",
}

def get_emails(name, company):
    domain = domain_map.get(company)
    if not domain:
        # Heuristic
        clean_company = company.lower().replace(" ", "").replace(".io", "").replace(".ai", "")
        # Remove common suffixes/prefixes if needed, but for now simple:
        domain = f"{clean_company}.com"
    
    # Cleaning name
    # Remove quotes, nickname parentheses
    name_clean = name.replace('"', '').split('(')[0].strip()
    parts = name_clean.lower().split()
    
    if len(parts) < 2:
        first = parts[0]
        last = ""
    else:
        first = parts[0]
        last = parts[-1] # Simple last name
    
    # Generate 2 likely
    # 1. first.last@domain
    # 2. first@domain
    
    email1 = f"{first}.{last}@{domain}" if last else f"{first}@{domain}"
    email2 = f"{first}@{domain}"
    
    # If first.last and first are same (no last), backup: first.l@domain or similar?
    if not last:
        email1 = f"{first}@{domain}"
        email2 = f"info@{domain}" # Fallback
    
    return email1, email2

candidates = []
with open('data/candidates.csv', 'r') as f:
    reader = csv.reader(f)
    # No header in current file
    for row in reader:
        if len(row) >= 3:
            candidates.append(row)

top_50 = candidates[:50]
final_rows = []

for row in top_50:
    name = row[0]
    title = row[1]
    company = row[2]
    url = row[3]
    score = row[4]
    
    e1, e2 = get_emails(name, company)
    final_rows.append([name, title, company, e1, e2, url])

# Write to CSV
with open('final_list_top_50.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Title', 'Company', 'Email1', 'Email2', 'YoutubeURL'])
    writer.writerows(final_rows)
    
print("Generated final_list_top_50.csv")
