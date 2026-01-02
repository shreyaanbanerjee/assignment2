
with open('data/raw.csv', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines):
    parts = line.strip().split(',')
    if len(parts) != 4:
        print(f"Line {i+1} has {len(parts)} columns: {line.strip()}")
