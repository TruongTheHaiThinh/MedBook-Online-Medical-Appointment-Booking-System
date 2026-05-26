import csv
import os

csv_path = "medicine_dataset.csv"
if not os.path.exists(csv_path):
    csv_path = "../medicine_dataset.csv"

with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    all_rows = list(reader)

print(f"Total rows: {len(all_rows)}")

# Check duplicates by all columns
unique_full = []
seen_full = set()
for r in all_rows:
    # Use tuple of all values
    key = tuple(r.values())
    if key not in seen_full:
        seen_full.add(key)
        unique_full.append(r)

print(f"Unique rows by ALL columns: {len(unique_full)}")
print("First 5 unique rows by all columns:")
for r in unique_full[:5]:
    print(r)

print("\nLast 5 unique rows by all columns:")
for r in unique_full[-5:]:
    print(r)
