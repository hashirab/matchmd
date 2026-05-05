import pandas as pd
import numpy as np
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("Fetching programs from Supabase...")
result = supabase.table("programs").select("*").execute()
programs = result.data
print(f"Loaded {len(programs)} programs")

# Build training dataset from NRMP program data
rows = []
for p in programs:
    img_rate = float(p["match_rate_img"] or 0)
    img_friendly = int(p["img_friendly"] or False)

    # Simulate applicant profiles across different score ranges
    for step2 in [200, 210, 220, 230, 240, 250, 260]:
        for usce_months in [0, 3, 6, 12]:
            for research_pubs in [0, 1, 3]:
                for is_img in [0, 1]:

                    # Calculate match probability based on real data
                    base_prob = img_rate if is_img else (1 - img_rate + 0.3)

                    # Step 2 effect
                    avg_step2 = p["avg_step2"] or 235
                    step2_diff = step2 - avg_step2
                    step2_effect = step2_diff * 0.008

                    # USCE boost for IMGs
                    usce_effect = (usce_months / 12) * 0.15 if is_img else 0

                    # Research boost
                    research_effect = research_pubs * 0.03

                    # IMG friendly boost
                    img_friendly_effect = 0.1 if (is_img and img_friendly) else 0

                    prob = base_prob + step2_effect + usce_effect + research_effect + img_friendly_effect
                    prob = max(0.02, min(0.98, prob))

                    matched = int(np.random.random() < prob)

                    rows.append({
                        "step2_score": step2,
                        "usce_months": usce_months,
                        "research_pubs": research_pubs,
                        "is_img": is_img,
                        "img_friendly_program": img_friendly,
                        "program_img_match_rate": img_rate,
                        "matched": matched
                    })

df = pd.DataFrame(rows)
print(f"Training dataset: {len(df)} rows")
print(f"Match rate: {df['matched'].mean():.2%}")

# Features and target
X = df.drop("matched", axis=1)
y = df["matched"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train with MLflow tracking
mlflow.set_experiment("matchmd-predictor")

with mlflow.start_run():
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    # Cross validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")

    print(f"\nResults:")
    print(f"Accuracy:  {acc:.3f}")
    print(f"ROC AUC:   {auc:.3f}")
    print(f"CV AUC:    {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    print(f"\n{classification_report(y_test, y_pred)}")

    # Feature importance
    print("Feature importance:")
    for feat, imp in sorted(zip(X.columns, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {feat}: {imp:.3f}")

    # Log to MLflow
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 4)
    mlflow.log_param("learning_rate", 0.1)
    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("roc_auc", auc)
    mlflow.log_metric("cv_auc_mean", cv_scores.mean())
    mlflow.log_metric("cv_auc_std", cv_scores.std())
    mlflow.xgboost.log_model(model, "model")

    # Save model locally
    model.save_model("match_predictor.json")
    print("\nModel saved to match_predictor.json")
    print(f"MLflow run logged successfully")

