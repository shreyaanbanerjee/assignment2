
import csv

candidates = []
with open('data/candidates.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 3:
            candidates.append(row)

top_50 = candidates[:50]
companies = sorted(list(set(c[2].strip() for c in top_50)))

print(f"Unique companies in top 50 ({len(companies)}):")
for company in companies:
    print(company)
