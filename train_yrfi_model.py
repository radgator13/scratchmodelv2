import pandas as pd 
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib

# === CONFIG ===
DATA_PATH = "data/mlb_boxscores_cleaned.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "yrfi_model.pkl")

# === Ensure model directory exists ===
os.makedirs(MODEL_DIR, exist_ok=True)

# === Load and clean data ===
df = pd.read_csv(DATA_PATH)

# Drop any rows with missing YRFI values
df = df.dropna(subset=["YRFI"])

# Convert 1st inning scores to numeric if needed
df["Away 1st"] = pd.to_numeric(df["Away 1st"], errors="coerce").fillna(0)
df["Home 1st"] = pd.to_numeric(df["Home 1st"], errors="coerce").fillna(0)

# === Class balance check ===
print("🔢 YRFI class distribution:\n", df["YRFI"].value_counts(), "\n")

# === Feature Engineering ===
# Basic: average 1st inning scoring behavior by team role
df["Away Avg 1st"] = df.groupby("Away Team")["Away 1st"].transform("mean")
df["Home Avg 1st"] = df.groupby("Home Team")["Home 1st"].transform("mean")

features = ["Away Avg 1st", "Home Avg 1st"]
target = "YRFI"

X = df[features]
y = df[target]

# === Split for training/testing ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# === Train Model ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === Evaluate ===
y_pred = model.predict(X_test)

# Safe ROC AUC calculation
if len(model.classes_) == 2:
    y_proba = model.predict_proba(X_test)[:, 1]
    print("📈 ROC AUC Score:", roc_auc_score(y_test, y_proba))
else:
    print("⚠️ Only one class in y_test — skipping ROC AUC.")

print("🔍 Classification Report:\n", classification_report(y_test, y_pred))

# === Save model ===
joblib.dump(model, MODEL_PATH)
print(f"✅ Model saved to {MODEL_PATH}")
