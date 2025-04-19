import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# === Paths ===
DATA_PATH = "data/yrfi_training_pregame.csv"
MODEL_PATH = "models/yrfi_pregame_model.pkl"
os.makedirs("models", exist_ok=True)

# === Load data ===
df = pd.read_csv(DATA_PATH)

features = [
    "Away_YRFI_Rate", "Away_Avg_1st",
    "Home_YRFI_Rate", "Home_Avg_1st"
]
target = "YRFI"

X = df[features]
y = df[target]

# === Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# === Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === Evaluate
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("📈 ROC AUC Score:", roc_auc_score(y_test, y_prob))
print("🔍 Classification Report:\n", classification_report(y_test, y_pred))

# === Save model
joblib.dump(model, MODEL_PATH)
print(f"\n✅ Model saved to {MODEL_PATH}")
