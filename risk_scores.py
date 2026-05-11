import sqlite3

# ---------------------------------------------------------------
# INSTRUCTIONS: Run this after setup_db.py
# python risk_scores.py
# ---------------------------------------------------------------

DB_FILE = "athletes_v2.db"

conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# --- Create table to store ACWR and risk scores ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS risk_scores (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id   TEXT,
    date         TEXT,
    acwr         REAL,
    acute_load   REAL,
    chronic_load REAL,
    risk_zone    TEXT,
    hrv_drop     REAL,
    sleep_avg    REAL,
    stress_avg   REAL,
    UNIQUE(athlete_id, date)
)
""")
conn.commit()

# ---------------------------------------------------------------
# For each athlete, calculate ACWR for every day
# ACWR = last 7 days TSS (acute) ÷ last 28 days avg TSS (chronic)
# ---------------------------------------------------------------

print("Fetching athletes...")
athletes = cursor.execute("SELECT athlete_id FROM athletes").fetchall()
total    = len(athletes)

print(f"Calculating ACWR for {total} athletes over 366 days each...")
print("This will take about 60 seconds...\n")

all_rows = []
done     = 0

for (athlete_id,) in athletes:

    # Get all daily data for this athlete sorted by date
    days = cursor.execute("""
        SELECT date, actual_tss, hrv, sleep_hours, stress
        FROM daily_data
        WHERE athlete_id = ?
        ORDER BY date ASC
    """, (athlete_id,)).fetchall()

    # Need at least 28 days to calculate ACWR
    for i in range(27, len(days)):

        today       = days[i]
        date        = today[0]

        # Acute load = sum of last 7 days TSS
        last_7      = [d[1] for d in days[i-6:i+1] if d[1] is not None]
        acute_load  = sum(last_7)

        # Chronic load = avg of last 28 days TSS × 7
        # (we multiply by 7 so it's on the same scale as acute)
        last_28     = [d[1] for d in days[i-27:i+1] if d[1] is not None]
        chronic_load = (sum(last_28) / len(last_28)) * 7 if last_28 else None

        if not chronic_load or chronic_load == 0:
            continue

        acwr = round(acute_load / chronic_load, 3)

        # HRV drop: today's HRV vs 7-day average
        hrv_vals    = [d[2] for d in days[i-6:i+1] if d[2] is not None]
        hrv_avg     = sum(hrv_vals) / len(hrv_vals) if hrv_vals else None
        today_hrv   = today[2]
        hrv_drop    = round(hrv_avg - today_hrv, 2) if (hrv_avg and today_hrv) else None

        # Sleep average over last 7 days
        sleep_vals  = [d[3] for d in days[i-6:i+1] if d[3] is not None]
        sleep_avg   = round(sum(sleep_vals) / len(sleep_vals), 2) if sleep_vals else None

        # Stress average over last 7 days
        stress_vals = [d[4] for d in days[i-6:i+1] if d[4] is not None]
        stress_avg  = round(sum(stress_vals) / len(stress_vals), 2) if stress_vals else None

        # Risk zone based on ACWR
        # < 0.8  = undertraining (also risky long term)
        # 0.8–1.3 = GREEN sweet spot
        # 1.3–1.5 = YELLOW monitor
        # > 1.5  = RED danger zone (4x injury risk)
        if acwr > 1.5:
            zone = "RED"
        elif acwr > 1.3:
            zone = "YELLOW"
        elif acwr >= 0.8:
            zone = "GREEN"
        else:
            zone = "LOW"   # undertraining

        all_rows.append((
            athlete_id, date, acwr,
            round(acute_load, 1),
            round(chronic_load, 1),
            zone, hrv_drop, sleep_avg, stress_avg
        ))

    done += 1
    if done % 100 == 0:
        print(f"  {done}/{total} athletes processed...")

# --- Save all risk scores ---
print(f"\nSaving {len(all_rows):,} risk score records...")
cursor.executemany("""
    INSERT OR REPLACE INTO risk_scores
    (athlete_id, date, acwr, acute_load, chronic_load,
     risk_zone, hrv_drop, sleep_avg, stress_avg)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", all_rows)
conn.commit()
print("Saved!")

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("\n=== Risk Zone Summary (across all athletes, all days) ===")
for row in cursor.execute("""
    SELECT risk_zone, COUNT(*) as total
    FROM risk_scores
    GROUP BY risk_zone
    ORDER BY total DESC
"""):
    emoji = {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢", "LOW": "⚪"}.get(row[0], "")
    print(f"  {emoji} {row[0]:<8} {row[1]:,} days")

print("\n=== ACWR vs Injury (does high ACWR = more injuries?) ===")
for row in cursor.execute("""
    SELECT r.risk_zone,
           COUNT(*) as total_days,
           SUM(d.injury) as injury_days,
           ROUND(SUM(d.injury) * 100.0 / COUNT(*), 2) as injury_rate_pct
    FROM risk_scores r
    JOIN daily_data d ON d.athlete_id = r.athlete_id AND d.date = r.date
    GROUP BY r.risk_zone
    ORDER BY injury_rate_pct DESC
"""):
    print(f"  {row[0]:<8} | days: {row[1]:>8,} | injuries: {row[2]:>6,} | injury rate: {row[3]}%")

print("\n=== Most Recent Risk Zones (today's status per athlete, sample 10) ===")
for row in cursor.execute("""
    SELECT r.athlete_id, r.date, r.acwr, r.risk_zone,
           r.sleep_avg, r.stress_avg
    FROM risk_scores r
    INNER JOIN (
        SELECT athlete_id, MAX(date) as max_date
        FROM risk_scores
        GROUP BY athlete_id
    ) latest ON r.athlete_id = latest.athlete_id AND r.date = latest.max_date
    WHERE r.risk_zone = 'RED'
    LIMIT 10
"""):
    print(f"  {row[0][:8]}... | {row[1]} | ACWR: {row[2]} | {row[3]} | sleep: {row[4]}h | stress: {row[5]}")

print("\nDone! Risk scores saved to athletes_v2.db")
conn.close()