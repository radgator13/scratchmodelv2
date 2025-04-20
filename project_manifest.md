# 🔧 Project Manifest: ScratchModelV2

## 🧠 Project Overview
ScratchModelV2 is a full-stack machine learning and data automation system for MLB YRFI/NRFI predictions. It scrapes data, builds a model pipeline, makes predictions, and visualizes results via a Streamlit dashboard.

---

## 📂 Directory Structure
ScratchModelV2/ ├── app.py # (or yrfi_dashboard.py) Main Streamlit dashboard app ├── ScratchModelV2.py # CLI pipeline script to run the full process ├── .gitignore # Git ignore rules ├── requirements.txt # Python dependencies ├── README.md # Project documentation (optional) ├── .streamlit/ │ └── config.toml # Streamlit configuration ├── data/ │ ├── mlb_boxscores_cleaned.csv │ ├── yrfi_predictions_pregame.csv │ └── yrfi_value_targets.csv ├── models/ │ └── yrfi_pregame_model.pkl ├── get_scores.py ├── prepare_pregame_training_data.py ├── train_pregame_yrfi_model.py ├── prepare_pregame_features.py ├── predict_yrfi_pregame.py └── run_pipeline.bat # Batch script for scheduling pipeline

yaml
Copy
Edit

---

## ⚙️ Pipeline Workflow (`ScratchModelV2.py`)
1. **Step 1** – Scrape latest game data: `get_scores.py`  
2. **Step 2** – Prepare training data: `prepare_pregame_training_data.py`  
3. **Step 3** – Train model: `train_pregame_yrfi_model.py`  
4. **Step 4** – Build prediction features: `prepare_pregame_features.py`  
5. **Step 5** – Predict YRFI probabilities: `predict_yrfi_pregame.py`  
6. **Step 6** – Merge, label fireballs, and output final CSVs  
7. **Step 7** – Auto `git add`, `commit`, and `push` changes to GitHub  
8. **Step 8** – Launch local Streamlit dashboard in browser: `streamlit run yrfi_dashboard.py`

Each step is logged via `print()` calls when run locally or via `.bat`/Task Scheduler.

---

## 🌐 Streamlit Dashboard
- **Entry point**: `app.py` or `yrfi_dashboard.py`
- **Main Features**:
  - Daily predictions display
  - Rolling fireball accuracy summary (🔥 to 🔥🔥🔥🔥🔥)
  - Calendar-based game filtering
  - Model confidence scores

---

## 📦 Key Files to Track in Git
```gitignore
!data/mlb_boxscores_cleaned.csv
!data/yrfi_predictions_pregame.csv
!data/yrfi_value_targets.csv
!models/yrfi_pregame_model.pkl
🚀 Deployment Notes
Hosted on: Streamlit Cloud

Main file: app.py

Branch: main

GitHub Repo: https://github.com/radgator13/scratchmodelv2

Python version: 3.12

✅ Requirements Summary
txt
Copy
Edit
streamlit
pandas
numpy
scikit-learn
requests
plotly
joblib
pyarrow
🔁 Automation
Scheduled via Task Scheduler using run_pipeline.bat

Outputs are logged to pipeline.log

Auto-pushes updated CSVs to GitHub each run

Auto-launches the Streamlit dashboard locally after each pipeline run

Predictions refresh automatically before each day