import csv
import os

csv_path = "medicine_dataset.csv"
if not os.path.exists(csv_path):
    csv_path = "../medicine_dataset.csv"

with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    all_rows = list(reader)

print(f"Total rows in CSV: {len(all_rows)}")

# Count unique
unique_rows = []
seen = set()
for row in all_rows:
    if row['Name'] not in seen:
        seen.add(row['Name'])
        unique_rows.append(row)

print(f"Total unique rows: {len(unique_rows)}")
print("First 5 unique rows:")
for r in unique_rows[:5]:
    print(r['Name'], "|", r.get('Category'))

print("\nLast 5 unique rows:")
for r in unique_rows[-5:]:
    print(r['Name'], "|", r.get('Category'))
