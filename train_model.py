import sqlite3
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import pickle

DB_FILE = "athletes_v2.db"

conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ---------------------------------------------------------------
# STEP 1 — Load data joined with gender
# ---------------------------------------------------------------
print("Loading data...")
rows = cursor.execute("""
    SELECT
        a.gender,
        r.acwr, r.acute_load, r.chronic_load, r.hrv_drop,
        r.sleep_avg, r.stress_avg,
        d.resting_hr, d.hrv,
        d.body_battery_morning, d.body_battery_evening,
        a.age, a.vo2max, a.recovery_rate, a.hrv_baseline,
        a.weekly_training_hrs,
        d.injury
    FROM risk_scores r
    JOIN daily_data d  ON d.athlete_id=r.athlete_id AND d.date=r.date
    JOIN athletes a    ON a.athlete_id=r.athlete_id
    WHERE r.acwr IS NOT NULL
      AND d.hrv IS NOT NULL
      AND d.sleep_hours IS NOT NULL
""").fetchall()
conn.close()

feature_names = [
    "acwr","acute_load","chronic_load","hrv_drop",
    "sleep_avg","stress_avg","resting_hr","hrv",
    "body_battery_morning","body_battery_evening",
    "age","vo2max","recovery_rate","hrv_baseline","weekly_training_hrs"
]

# Split by gender
male_rows   = [r for r in rows if r[0].lower()=="male"]
female_rows = [r for r in rows if r[0].lower()=="female"]

print(f"Total rows: {len(rows):,}")
print(f"Male rows:  {len(male_rows):,}")
print(f"Female rows:{len(female_rows):,}")

# ---------------------------------------------------------------
# STEP 2 — Train function (reused for both genders)
# ---------------------------------------------------------------
def train_gender_model(gender_rows, gender_label):
    print(f"\n{'='*50}")
    print(f"Training {gender_label.upper()} model...")
    print(f"{'='*50}")

    X = [[float(c) if c is not None else 0.0 for c in r[1:-1]] for r in gender_rows]
    y = [int(r[-1]) for r in gender_rows]

    injured = sum(y)
    healthy = len(y) - injured
    print(f"  Injured days: {injured:,} ({injured/len(y)*100:.1f}%)")
    print(f"  Healthy days: {healthy:,} ({healthy/len(y)*100:.1f}%)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    ratio = round(healthy / injured, 2)
    print(f"  Class ratio: {ratio}")

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        scale_pos_weight=ratio,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    cm     = confusion_matrix(y_test, y_pred)

    print(f"\n  === {gender_label.upper()} Model Performance ===")
    print(classification_report(y_test, y_pred, target_names=["Healthy","Injured"]))

    total_inj = cm[1][0] + cm[1][1]
    caught    = cm[1][1]
    print(f"  Confusion Matrix:")
    print(f"    True Healthy:  {cm[0][0]:,}  |  False Alarm:  {cm[0][1]:,}")
    print(f"    Missed Injury: {cm[1][0]:,}  |  True Injured: {cm[1][1]:,}")
    print(f"    Caught {caught:,} / {total_inj:,} injuries ({caught/total_inj*100:.1f}%)")

    print(f"\n  Cross validation...")
    cv = cross_val_score(model, X, y, cv=5, scoring="recall", n_jobs=-1)
    print(f"  Recall scores: {[round(s,3) for s in cv]}")
    print(f"  Avg recall:    {cv.mean():.3f} (+/- {cv.std():.3f})")

    print(f"\n  === Feature Importance ({gender_label.upper()}) ===")
    ranked = sorted(zip(feature_names, model.feature_importances_),
                    key=lambda x: x[1], reverse=True)
    for name, score in ranked:
        bar = "█" * int(score * 200)
        print(f"    {name:<25} {bar} {score:.4f}")

    return model

# ---------------------------------------------------------------
# STEP 3 — Train both models
# ---------------------------------------------------------------
male_model   = train_gender_model(male_rows,   "male")
female_model = train_gender_model(female_rows, "female")

# ---------------------------------------------------------------
# STEP 4 — Save both models in one file
# ---------------------------------------------------------------
with open("model.pkl", "wb") as f:
    pickle.dump({
        "male":         male_model,
        "female":       female_model,
        "feature_names": feature_names
    }, f)

print("\n" + "="*50)
print("Both models saved to model.pkl")
print("="*50)

# ---------------------------------------------------------------
# STEP 5 — Compare feature importance between genders
# ---------------------------------------------------------------
print("\n=== MALE vs FEMALE Feature Importance Comparison ===")
print(f"{'Feature':<25} {'Male':>8} {'Female':>8} {'Difference':>12}")
print("-"*55)

male_imp   = dict(zip(feature_names, male_model.feature_importances_))
female_imp = dict(zip(feature_names, female_model.feature_importances_))

ranked_diff = sorted(feature_names,
    key=lambda f: abs(male_imp[f]-female_imp[f]), reverse=True)

for f in ranked_diff:
    m = male_imp[f]
    fe= female_imp[f]
    diff = fe - m
    arrow = "↑ Female" if diff > 0.01 else "↑ Male" if diff < -0.01 else "≈ Similar"
    print(f"  {f:<25} {m:>7.4f}  {fe:>7.4f}  {arrow}")

print("\nDone! Dashboard will now use gender-specific models automatically.")