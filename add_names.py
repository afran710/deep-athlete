import sqlite3
import random

DB_FILE = "athletes_v2.db"

# ── Strictly male first names ──
first_male = [
    "James","Liam","Noah","Oliver","Elijah","Lucas","Mason","Logan","Ethan","Aiden",
    "Ryan","Tyler","Marcus","Diego","Carlos","Andre","Kai","Zane","Blake","Hunter",
    "Cole","Nathan","Caleb","Owen","Adrian","Isaiah","Jaxon","Eli","Finn","Connor",
    "Rahul","Arjun","Dev","Vikram","Rohan","Anil","Kiran","Sanjay","Mihail","Stefan",
    "Jordan","Cameron","Alex","Chris","Daniel","Matthew","Andrew","Joshua","Samuel","David",
    "Mohammed","Omar","Yusuf","Tariq","Hassan","Leon","Felix","Lukas","Marco","Anton"
]

# ── Strictly female first names ──
first_female = [
    "Emma","Olivia","Ava","Sophia","Isabella","Mia","Charlotte","Amelia","Harper","Evelyn",
    "Luna","Zoe","Layla","Riley","Nora","Lily","Eleanor","Hannah","Stella","Violet",
    "Sofia","Camila","Aria","Scarlett","Penelope","Chloe","Aaliyah","Maya","Priya","Riya",
    "Meera","Ananya","Divya","Pooja","Sneha","Lakshmi","Kavya","Nisha","Aisha","Fatima",
    "Sarah","Emily","Grace","Chloe","Natalie","Victoria","Isabelle","Jasmine","Ruby","Alice",
    "Leila","Amira","Yasmin","Nadia","Sara","Elena","Anna","Maria","Nina","Clara"
]

# ── Gender neutral last names ──
last_names = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Wilson","Anderson","Taylor","Thomas","Moore","Jackson","Martin","Lee","Thompson","White",
    "Harris","Clark","Lewis","Robinson","Walker","Young","Allen","King","Scott","Green",
    "Nair","Menon","Kumar","Singh","Patel","Shah","Sharma","Gupta","Reddy","Iyer",
    "Chen","Kim","Park","Nguyen","Santos","Rivera","Reyes","Cruz","Flores","Torres"
]

random.seed(42)

conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

athletes = cursor.execute("SELECT athlete_id, gender FROM athletes").fetchall()
print(f"Updating names for {len(athletes)} athletes...")

male_count   = 0
female_count = 0

for athlete_id, gender in athletes:
    if gender and gender.lower() == "female":
        first = random.choice(first_female)
        female_count += 1
    else:
        first = random.choice(first_male)
        male_count += 1

    last = random.choice(last_names)
    cursor.execute("UPDATE athletes SET name=? WHERE athlete_id=?",
                   (f"{first} {last}", athlete_id))

conn.commit()

print(f"  👨 Male athletes renamed:   {male_count}")
print(f"  👩 Female athletes renamed: {female_count}")

print("\n=== Sample Male Names ===")
for row in cursor.execute("SELECT name, gender, age FROM athletes WHERE gender='male' LIMIT 5"):
    print(f"  {row[0]:<22} | {row[1]} | age {row[2]}")

print("\n=== Sample Female Names ===")
for row in cursor.execute("SELECT name, gender, age FROM athletes WHERE gender='female' LIMIT 5"):
    print(f"  {row[0]:<22} | {row[1]} | age {row[2]}")

print("\nDone! All names now match gender correctly.")
conn.close()