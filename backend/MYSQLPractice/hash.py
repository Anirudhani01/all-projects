import random
import string
from mysql.connector import connect

# ✅ Connect to MySQL
connection = connect(
    host='localhost',
    user='anirudh',
    password='password123',
    database='players_data'
)

cursor = connection.cursor()

# ✅ Check if column exists
cursor.execute("SHOW COLUMNS FROM players_table LIKE 'playerHash'")
if not cursor.fetchone():
    print("⚠️ 'playerHash' column missing!")
    exit()

# ✅ Fetch players without a hash
cursor.execute("SELECT playerID FROM players_table WHERE playerHash IS NULL")
players = cursor.fetchall()

print(f"Found {len(players)} players without hash.")

# ✅ Generate random alphanumeric string
def generate_random_hash(length=32):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

updated_count = 0

# ✅ Update each player
for (playerID,) in players:
    random_hash = generate_random_hash()
    cursor.execute(
        "UPDATE players_table SET playerHash = %s WHERE playerID = %s",
        (random_hash, playerID)
    )
    updated_count += 1
    print(f"✅ Updated {playerID} → {random_hash}")

connection.commit()
cursor.close()
connection.close()

print(f"✅ {updated_count} hashes inserted and committed.")
