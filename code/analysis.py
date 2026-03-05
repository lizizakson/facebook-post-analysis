import sys
#print("Running python:", sys.executable)

import pandas as pd

df = pd.read_csv("../data/sep2025_march2026_facebook.csv")

print("Rows, Columns:", df.shape)
print(df.head())

print(df.columns.tolist())

