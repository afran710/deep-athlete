import sqlite3
import pickle
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, average_precision_score
)

DB_FILE    = "athletes_v2.db"
MODEL_FILE = "model.pkl"

# ── Load models ──
with open(MODEL_FILE, "rb") as f:
    d = pickle.load(f)

male_model   = d["male"]
female_model = d["female"]
feat_names   = d["feature_names"]

# ── Load data ──
print("Loading data...")
conn = sqlite3.connect(DB_FILE)
rows = conn.execute("""
    SELECT a.gender,
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
    WHERE r.acwr IS NOT NULL AND d.hrv IS NOT NULL AND d.sleep_hours IS NOT NULL
""").fetchall()
conn.close()

male_rows   = [r for r in rows if r[0].lower()=="male"]
female_rows = [r for r in rows if r[0].lower()=="female"]

def evaluate(model, gender_rows, label):
    X = [[float(c) if c is not None else 0.0 for c in r[1:-1]] for r in gender_rows]
    y = [int(r[-1]) for r in gender_rows]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    print(f"\n{'='*55}")
    print(f"  {label} MODEL EVALUATION")
    print(f"{'='*55}")
    print(f"  Test set size:    {len(y_test):,} rows")
    print(f"  Injured in test:  {sum(y_test):,}")
    print(f"  Healthy in test:  {len(y_test)-sum(y_test):,}")

    print(f"\n── Classification Report ──")
    print(classification_report(y_test, y_pred,
                                target_names=["Healthy","Injured"],
                                digits=3))

    print(f"── Confusion Matrix ──")
    print(f"  True Healthy:  {tn:>6,}  |  False Alarm:  {fp:>6,}")
    print(f"  Missed Injury: {fn:>6,}  |  True Injured: {tp:>6,}")

    print(f"\n── Key Metrics ──")
    recall    = tp / (tp + fn)
    precision = tp / (tp + fp) if (tp+fp) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision+recall) > 0 else 0
    accuracy  = (tp + tn) / len(y_test)
    specificity = tn / (tn + fp)
    roc_auc   = roc_auc_score(y_test, y_prob)
    pr_auc    = average_precision_score(y_test, y_prob)

    print(f"  Accuracy:       {accuracy*100:.1f}%  — overall correct predictions")
    print(f"  Recall:         {recall*100:.1f}%  — injuries caught out of all real injuries")
    print(f"  Precision:      {precision*100:.1f}%  — of flagged athletes, how many actually injured")
    print(f"  F1 Score:       {f1:.3f}   — balance of recall and precision")
    print(f"  Specificity:    {specificity*100:.1f}%  — healthy athletes correctly cleared")
    print(f"  ROC-AUC:        {roc_auc:.3f}   — overall discrimination ability (1.0 = perfect)")
    print(f"  PR-AUC:         {pr_auc:.3f}   — precision-recall tradeoff (higher = better)")

    print(f"\n── Cross Validation (5-fold Recall) ──")
    cv = cross_val_score(model, X, y, cv=5, scoring="recall", n_jobs=-1)
    print(f"  Fold scores: {[round(s,3) for s in cv]}")
    print(f"  Mean recall: {cv.mean():.3f} (+/- {cv.std():.3f})")

    print(f"\n── What this means in plain English ──")
    print(f"  Out of every 10 injured athletes:")
    print(f"    → {recall*10:.1f} are correctly flagged as high risk")
    print(f"    → {(1-recall)*10:.1f} are missed (predicted safe but actually injured)")
    print(f"  Out of every 10 athletes flagged as high risk:")
    print(f"    → {precision*10:.1f} are genuinely injured")
    print(f"    → {(1-precision)*10:.1f} are false alarms (healthy but flagged)")

# ── Run evaluation ──
evaluate(male_model,   male_rows,   "MALE")
evaluate(female_model, female_rows, "FEMALE")

print(f"\n{'='*55}")
print("  COMPARISON SUMMARY")
print(f"{'='*55}")
print(f"  {'Metric':<20} {'Male':>10} {'Female':>10}")
print(f"  {'-'*42}")

for label, model, rows_ in [("Male", male_model, male_rows), ("Female", female_model, female_rows)]:
    X = [[float(c) if c is not None else 0.0 for c in r[1:-1]] for r in rows_]
    y = [int(r[-1]) for r in rows_]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    if label == "Male":
        m_recall = tp/(tp+fn); m_prec = tp/(tp+fp) if tp+fp>0 else 0
        m_f1 = 2*m_prec*m_recall/(m_prec+m_recall) if m_prec+m_recall>0 else 0
        m_acc = (tp+tn)/len(y_test); m_auc = roc_auc_score(y_test, y_prob)
    else:
        f_recall = tp/(tp+fn); f_prec = tp/(tp+fp) if tp+fp>0 else 0
        f_f1 = 2*f_prec*f_recall/(f_prec+f_recall) if f_prec+f_recall>0 else 0
        f_acc = (tp+tn)/len(y_test); f_auc = roc_auc_score(y_test, y_prob)

print(f"  {'Recall':<20} {m_recall*100:>9.1f}% {f_recall*100:>9.1f}%")
print(f"  {'Precision':<20} {m_prec*100:>9.1f}% {f_prec*100:>9.1f}%")
print(f"  {'F1 Score':<20} {m_f1:>10.3f} {f_f1:>10.3f}")
print(f"  {'Accuracy':<20} {m_acc*100:>9.1f}% {f_acc*100:>9.1f}%")
print(f"  {'ROC-AUC':<20} {m_auc:>10.3f} {f_auc:>10.3f}")
print()