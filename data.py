import pandas as pd

REQUIRED = {"name","city","property_type","price","expected_roi","base_risk","url"}

def load_properties(path="properties.xlsx"):
    df = pd.read_excel(path)
    if not REQUIRED.issubset(df.columns):
        raise ValueError("Dataset missing required columns")
    return df
