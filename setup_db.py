import sqlite3
import csv

# ---------------------------------------------------------------
# INSTRUCTIONS: Make sure these 3 files are in the same folder:
#   athletes.csv, daily_data.csv, activity_data.csv
# Then run:  python setup_db.py
# ---------------------------------------------------------------

DB_FILE = "athletes_v2.db"

conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("Creating tables...")

# --- Table 1: athlete profiles ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS athletes (
    athlete_id          TEXT PRIMARY KEY,
    gender              TEXT,
    age                 INTEGER,
    height_cm           REAL,
    weight_kg           REAL,
    hrv_baseline        REAL,
    vo2max              REAL,
    training_experience INTEGER,
    weekly_training_hrs REAL,
    recovery_rate       REAL,
    lifestyle           TEXT,
    sleep_quality       REAL,
    nutrition_factor    REAL,
    stress_factor       REAL
)
""")

# --- Table 2: daily readings (the most important table) ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_data (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id           TEXT,
    date                 TEXT,
    resting_hr           REAL,
    hrv                  REAL,
    sleep_hours          REAL,
    sleep_quality        REAL,
    body_battery_morning REAL,
    body_battery_evening REAL,
    stress               REAL,
    planned_tss          REAL,
    actual_tss           REAL,
    injury               INTEGER,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id)
)
""")

# --- Table 3: training sessions ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS activities (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id          TEXT,
    date                TEXT,
    sport               TEXT,
    workout_type        TEXT,
    duration_minutes    REAL,
    tss                 REAL,
    intensity_factor    REAL,
    avg_hr              REAL,
    distance_km         REAL,
    training_effect_aerobic  REAL,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id)
)
""")

conn.commit()
print("Tables created!")

# ---------------------------------------------------------------
# Load athletes.csv
# ---------------------------------------------------------------
print("\nLoading athletes.csv...")
count = 0
with open("athletes.csv", newline="") as f:
    for row in csv.DictReader(f):
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO athletes VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                row["athlete_id"],
                row["gender"],
                int(float(row["age"])),
                float(row["height_cm"]),
                float(row["weight_kg"]),
                float(row["hrv_baseline"]),
                float(row["vo2max"]),
                int(float(row["training_experience"])),
                float(row["weekly_training_hours"]),
                float(row["recovery_rate"]),
                row["lifestyle"],
                float(row["sleep_quality"]),
                float(row["nutrition_factor"]),
                float(row["stress_factor"]),
            ))
            count += 1
        except Exception as e:
            pass

conn.commit()
print(f"  Loaded {count} athletes")

# ---------------------------------------------------------------
# Load daily_data.csv
# ---------------------------------------------------------------
print("\nLoading daily_data.csv (366,000 rows — takes ~30 seconds)...")
count = 0
batch = []
with open("daily_data.csv", newline="") as f:
    for row in csv.DictReader(f):
        try:
            batch.append((
                row["athlete_id"],
                row["date"],
                float(row["resting_hr"])           if row["resting_hr"]           else None,
                float(row["hrv"])                  if row["hrv"]                  else None,
                float(row["sleep_hours"])          if row["sleep_hours"]          else None,
                float(row["sleep_quality"])        if row["sleep_quality"]        else None,
                float(row["body_battery_morning"]) if row["body_battery_morning"] else None,
                float(row["body_battery_evening"]) if row["body_battery_evening"] else None,
                float(row["stress"])               if row["stress"]               else None,
                float(row["planned_tss"])          if row["planned_tss"]          else None,
                float(row["actual_tss"])           if row["actual_tss"]           else None,
                int(row["injury"])                 if row["injury"]               else 0,
            ))
            count += 1
            if len(batch) >= 5000:
                cursor.executemany("""
                    INSERT INTO daily_data
                    (athlete_id, date, resting_hr, hrv, sleep_hours, sleep_quality,
                     body_battery_morning, body_battery_evening, stress,
                     planned_tss, actual_tss, injury)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                batch = []
                print(f"  {count:,} rows loaded...", end="\r")
        except Exception as e:
            pass

if batch:
    cursor.executemany("""
        INSERT INTO daily_data
        (athlete_id, date, resting_hr, hrv, sleep_hours, sleep_quality,
         body_battery_morning, body_battery_evening, stress,
         planned_tss, actual_tss, injury)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch)
    conn.commit()

print(f"\n  Loaded {count:,} daily records")

# ---------------------------------------------------------------
# Load activity_data.csv
# ---------------------------------------------------------------
print("\nLoading activity_data.csv (384,000 rows — takes ~30 seconds)...")
count = 0
batch = []
with open("activity_data.csv", newline="") as f:
    for row in csv.DictReader(f):
        try:
            batch.append((
                row["athlete_id"],
                row["date"],
                row["sport"],
                row["workout_type"],
                float(row["duration_minutes"])        if row["duration_minutes"]        else None,
                float(row["tss"])                     if row["tss"]                     else None,
                float(row["intensity_factor"])        if row["intensity_factor"]        else None,
                float(row["avg_hr"])                  if row["avg_hr"]                  else None,
                float(row["distance_km"])             if row["distance_km"]             else None,
                float(row["training_effect_aerobic"]) if row["training_effect_aerobic"] else None,
            ))
            count += 1
            if len(batch) >= 5000:
                cursor.executemany("""
                    INSERT INTO activities
                    (athlete_id, date, sport, workout_type, duration_minutes,
                     tss, intensity_factor, avg_hr, distance_km, training_effect_aerobic)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                batch = []
                print(f"  {count:,} rows loaded...", end="\r")
        except Exception as e:
            pass

if batch:
    cursor.executemany("""
        INSERT INTO activities
        (athlete_id, date, sport, workout_type, duration_minutes,
         tss, intensity_factor, avg_hr, distance_km, training_effect_aerobic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch)
    conn.commit()

print(f"\n  Loaded {count:,} activity records")

# ---------------------------------------------------------------
# Quick summary
# ---------------------------------------------------------------
print("\n=== Database Summary ===")

total_athletes   = cursor.execute("SELECT COUNT(*) FROM athletes").fetchone()[0]
total_days       = cursor.execute("SELECT COUNT(*) FROM daily_data").fetchone()[0]
total_activities = cursor.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
total_injuries   = cursor.execute("SELECT COUNT(*) FROM daily_data WHERE injury = 1").fetchone()[0]

print(f"  Athletes:          {total_athletes:,}")
print(f"  Daily records:     {total_days:,}")
print(f"  Activity sessions: {total_activities:,}")
print(f"  Injury days:       {total_injuries:,}")

print("\n=== Sample: 5 Injury Days ===")
for row in cursor.execute("""
    SELECT d.athlete_id, d.date, d.hrv, d.sleep_hours, d.actual_tss, d.stress
    FROM daily_data d
    WHERE d.injury = 1
    LIMIT 5
"""):
    print(f"  {row[0][:8]}... | {row[1]} | HRV: {row[2]:.1f} | Sleep: {row[3]:.1f}h | TSS: {row[4]:.0f} | Stress: {row[5]:.1f}")

print(f"\nDone! Database saved as {DB_FILE}")
conn.close()