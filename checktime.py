import pandas as pd
df = pd.read_csv("data/mlb_boxscores_cleaned.csv")
print(df["Game Date"].unique())

