import sqlite3
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (recall_score, precision_score, f1_score,
                             accuracy_score, roc_auc_score)
import pickle

DB_PATH    = "athletes_v2.db"
MODEL_PATH = "model.pkl"

FEATURES = [
    "acwr", "acute_load", "chronic_load", "hrv_drop", "sleep_avg",
    "stress_avg", "resting_hr", "hrv", "body_battery_morning",
    "body_battery_evening", "age", "vo2max",
    "hrv_baseline", "weekly_training_hrs"
]

HEALTHY_RATIO = 5

# Fixed calibration range — do not change
# Keeps scores consistent across retrains
P_MIN = 0.0001
P_MAX = 0.9500

# Dashboard thresholds — must match dashboard.py exactly
GREEN_MAX  =  8   # 0–8%   = GREEN  safe to train
YELLOW_MAX = 40   # 8–40%  = YELLOW monitor closely
                  # 40%+   = RED    high risk

QUERY = """
SELECT
    d.athlete_id, d.date,
    r.acwr, r.acute_load, r.chronic_load, r.hrv_drop, r.sleep_avg, r.stress_avg,
    d.resting_hr, d.hrv, d.body_battery_morning, d.body_battery_evening,
    a.age, a.vo2max, a.hrv_baseline, a.weekly_training_hrs,
    a.gender,
    CASE
        WHEN d.injury = 1
         AND r.acwr > 1.2
         AND (
             r.stress_avg > 40
             OR (d.hrv < 65 AND r.sleep_avg < 6.5)
         )
        THEN 1 ELSE 0
    END AS injury_strict
FROM daily_data d
JOIN athletes    a ON d.athlete_id = a.athlete_id
JOIN risk_scores r ON d.athlete_id = r.athlete_id AND d.date = r.date
WHERE r.acwr IS NOT NULL AND r.acute_load IS NOT NULL
  AND r.chronic_load IS NOT NULL AND r.chronic_load > 0
"""

print("Loading data from database...")
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query(QUERY, conn)
conn.close()

print(f"Total rows loaded : {len(df):,}")
print(f"Strict injuries   : {df['injury_strict'].sum():,}  ({df['injury_strict'].mean()*100:.2f}%)")

df = df.dropna(subset=FEATURES + ["injury_strict", "gender"])
print(f"Rows after dropna : {len(df):,}")

male_df   = df[df["gender"].str.lower() == "male"].copy()
female_df = df[df["gender"].str.lower() == "female"].copy()
print(f"\nMale rows   : {len(male_df):,}  (injuries: {male_df['injury_strict'].sum():,})")
print(f"Female rows : {len(female_df):,}  (injuries: {female_df['injury_strict'].sum():,})")


def calibrate(raw):
    return round(float(np.clip((raw - P_MIN) / (P_MAX - P_MIN), 0, 1)) * 100, 1)


def zone_label(pct):
    if pct >= YELLOW_MAX:
        return "🔴 RED   — HIGH RISK"
    elif pct >= GREEN_MAX:
        return "🟡 YELLOW — MONITOR"
    else:
        return "🟢 GREEN  — SAFE"


def train_gender_model(data, label):
    X_all = data[FEATURES]
    y_all = data["injury_strict"]
    n_pos = int((y_all == 1).sum())
    n_neg = int((y_all == 0).sum())
    if n_pos == 0:
        raise ValueError(f"No injury cases for {label}")

    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X_all, y_all, test_size=0.2, random_state=42, stratify=y_all
    )

    train_df        = X_train_full.copy()
    train_df["_y"]  = y_train_full.values
    injured_rows    = train_df[train_df["_y"] == 1]
    healthy_rows    = train_df[train_df["_y"] == 0]
    n_keep          = min(len(healthy_rows), len(injured_rows) * HEALTHY_RATIO)
    healthy_sampled = healthy_rows.sample(n=n_keep, random_state=42)
    balanced        = pd.concat([injured_rows, healthy_sampled]).sample(frac=1, random_state=42)
    X_train         = balanced[FEATURES]
    y_train         = balanced["_y"]

    injury_pct = len(injured_rows) / len(balanced) * 100
    print(f"\n[{label}] Full data    : {n_neg:,} healthy | {n_pos:,} injured")
    print(f"[{label}] Training set : {n_keep:,} healthy | {len(injured_rows):,} injured ({injury_pct:.1f}%)")

    model = XGBClassifier(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        reg_alpha=0.1,
        reg_lambda=1.5,
        scale_pos_weight=1,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    print(f"[{label}] Recall    : {recall_score(y_test, y_pred)*100:.1f}%")
    print(f"[{label}] Precision : {precision_score(y_test, y_pred)*100:.1f}%")
    print(f"[{label}] F1 Score  : {f1_score(y_test, y_pred):.3f}")
    print(f"[{label}] Accuracy  : {accuracy_score(y_test, y_pred)*100:.1f}%")
    print(f"[{label}] ROC-AUC   : {roc_auc_score(y_test, y_proba):.3f}")

    # ── Sanity check against dashboard thresholds ──
    healthy_s  = pd.DataFrame([{
        "acwr":0.93, "acute_load":280, "chronic_load":300,
        "hrv_drop":1, "sleep_avg":8.5, "stress_avg":15,
        "resting_hr":55, "hrv":75, "body_battery_morning":80,
        "body_battery_evening":60, "age":28, "vo2max":55,
        "hrv_baseline":76, "weekly_training_hrs":10
    }])
    highrisk_s = pd.DataFrame([{
        "acwr":2.1, "acute_load":620, "chronic_load":300,
        "hrv_drop":30, "sleep_avg":4.5, "stress_avg":90,
        "resting_hr":78, "hrv":45, "body_battery_morning":20,
        "body_battery_evening":10, "age":38, "vo2max":38,
        "hrv_baseline":75, "weekly_training_hrs":22
    }])

    p_h  = calibrate(model.predict_proba(healthy_s[FEATURES])[0][1])
    p_hr = calibrate(model.predict_proba(highrisk_s[FEATURES])[0][1])

    h_pass  = "✅ PASS" if p_h  <  GREEN_MAX  else "❌ FAIL — should be GREEN"
    hr_pass = "✅ PASS" if p_hr >= YELLOW_MAX else "❌ FAIL — should be RED"

    print(f"\n[{label}] ── Dashboard Sanity Check ──")
    print(f"[{label}] Healthy   : {p_h}%  {zone_label(p_h)}  {h_pass}")
    print(f"[{label}] High-risk : {p_hr}%  {zone_label(p_hr)}  {hr_pass}")

    if "FAIL" in h_pass or "FAIL" in hr_pass:
        print(f"[{label}] ⚠️  WARNING: Model failed sanity check — review before deploying")
    else:
        print(f"[{label}] ✅  All checks passed — safe to deploy")

    return model


male_model   = train_gender_model(male_df,   "MALE")
female_model = train_gender_model(female_df, "FEMALE")

payload = {
    "male":          male_model,
    "female":        female_model,
    "feature_names": FEATURES,
    "male_cal":      (P_MIN, P_MAX),
    "female_cal":    (P_MIN, P_MAX),
}
with open(MODEL_PATH, "wb") as f:
    pickle.dump(payload, f)

print(f"\n✅  Models saved to {MODEL_PATH}")
print(f"    HEALTHY_RATIO = {HEALTHY_RATIO}")
print(f"    Calibration   = {P_MIN} → {P_MAX}")
print(f"    Thresholds    = GREEN < {GREEN_MAX}%  |  YELLOW {GREEN_MAX}–{YELLOW_MAX}%  |  RED >= {YELLOW_MAX}%")
print("    Next step: streamlit run dashboard.py")