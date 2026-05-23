import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'medbook.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS leave_requests (
    id VARCHAR(36) PRIMARY KEY,
    doctor_id VARCHAR(36) NOT NULL,
    leave_date DATE NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT "APPROVED",
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
)
''')
conn.commit()
conn.close()
print(f"Table leave_requests created successfully in {os.path.abspath(db_path)}.")
