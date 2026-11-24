import sqlite3
from datetime import datetime

# Connect to the database file in the main folder
conn = sqlite3.connect("civil_engineering_lab.db")
cursor = conn.cursor()

try:
    # Check what columns the table actually has
    cursor.execute("PRAGMA table_info(concrete_tests)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Columns in concrete_tests:", columns)

    # Insert a dummy test record
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO concrete_tests (date, compressive_strength) VALUES (?, ?)", (today, 25.5))
    
    # SAVE IT
    conn.commit()
    print("✅ Data successfully inserted and committed!")
    
except Exception as e:
    print("❌ Error inserting data:", e)

finally:
    conn.close()