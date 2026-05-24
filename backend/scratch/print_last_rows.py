import csv
import os

csv_path = "medicine_dataset.csv"
if not os.path.exists(csv_path):
    csv_path = "../medicine_dataset.csv"

with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    all_rows = list(reader)

print(f"Total rows: {len(all_rows)}")
last_316 = all_rows[-316:]

vietnamese_count = 0
unique_names_in_last_316 = set()
for idx, row in enumerate(last_316):
    name = row['Name']
    unique_names_in_last_316.add(name)
    # Check if there are any obvious Vietnamese characters or names
    if any(c in name.lower() for c in ['á', 'à', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ', 'é', 'è', 'ẻ', 'ẽ', 'ẹ', 'ê', 'ế', 'ề', 'ể', 'ễ', 'ệ', 'í', 'ì', 'ỉ', 'ĩ', 'ị', 'ó', 'ò', 'ỏ', 'õ', 'ọ', 'ô', 'ố', 'ồ', 'ổ', 'ỗ', 'ộ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ú', 'ù', 'ủ', 'ũ', 'ụ', 'ư', 'ứ', 'ừ', 'ử', 'ữ', 'ự', 'ý', 'ỳ', 'ỷ', 'ỹ', 'ỵ', 'đ']):
        vietnamese_count += 1

print(f"Number of rows with Vietnamese characters in last 316: {vietnamese_count}")
print(f"Unique names in last 316: {len(unique_names_in_last_316)}")
print("Sample names from the last 316:")
for r in last_316[:15]:
    print(f"Name: {r['Name']} | Category: {r.get('Category')} | Dosage: {r.get('Dosage Form')} | Strength: {r.get('Strength')} | Manufacturer: {r.get('Manufacturer')}")
