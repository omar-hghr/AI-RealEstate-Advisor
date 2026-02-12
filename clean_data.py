import re
import numpy as np
import pandas as pd

RAW_CSV = "egypt_real_estate_listings.csv"  
OUT_CSV = "cleaned_listings.csv" 


def parse_egp_amount(value):

    if pd.isna(value):
        return np.nan
    s = str(value)
    s = s.replace(",", "")
    match = re.search(r"(\d+(\.\d+)?)", s)
    if not match:
        return np.nan
    try:
        return float(match.group(1))
    except ValueError:
        return np.nan


def parse_size(size_str):
    
    if pd.isna(size_str):
        return np.nan, np.nan

    s = str(size_str).lower()

    sqm_match = re.search(r"(\d+(?:\.\d+)?)\s*sqm", s)
    sqft_match = re.search(r"(\d+(?:\.\d+)?)\s*sqft", s)

    sqm = None
    sqft = None

    if sqft_match:
        try:
            sqft = float(sqft_match.group(1).replace(",", ""))
        except ValueError:
            sqft = None

    if sqm_match:
        try:
            sqm = float(sqm_match.group(1).replace(",", ""))
        except ValueError:
            sqm = None
    elif sqft is not None:
        sqm = sqft * 0.092903

    return sqft, sqm


def parse_bedrooms(bed_str):
    
    if pd.isna(bed_str):
        return np.nan, False

    s = str(bed_str).strip().lower()
    has_maid = "maid" in s

    if "studio" in s:
        return 0, has_maid

    m = re.search(r"(\d+)", s)
    if m:
        try:
            beds = int(m.group(1))
        except ValueError:
            beds = np.nan
    else:
        beds = np.nan

    return beds, has_maid


def parse_bathrooms(bath_str):
  
    if pd.isna(bath_str):
        return np.nan

    s = str(bath_str).strip().lower()
    if s == "none":
        return 0

    s = s.replace("+", "")

    m = re.search(r"(\d+(\.\d+)?)", s)
    if not m:
        return np.nan
    try:
        val = float(m.group(1))
        return int(round(val))
    except ValueError:
        return np.nan


def parse_available_date(date_str):
   
    if pd.isna(date_str):
        return pd.NaT
    s = str(date_str).strip()
    try:
        return pd.to_datetime(s, dayfirst=True, errors="coerce")
    except Exception:
        return pd.NaT


def split_location(loc_str):
   
    if pd.isna(loc_str):
        return pd.Series([np.nan, np.nan, np.nan, np.nan])

    parts = [p.strip() for p in str(loc_str).split(",") if p.strip()]
    if not parts:
        return pd.Series([np.nan, np.nan, np.nan, np.nan])

    governorate = parts[-1] if len(parts) >= 1 else np.nan
    city_area = parts[-2] if len(parts) >= 2 else np.nan
    neighbourhood = parts[1] if len(parts) >= 3 else np.nan   
    project_name = parts[0] if len(parts) >= 1 else np.nan

    return pd.Series([project_name, neighbourhood, city_area, governorate])


def normalize_property_type(t):

    if pd.isna(t):
        return np.nan
    s = str(t).strip().lower()
    mapping = {
        "apartment": "apartment",
        "ivilla": "apartment",      
        "duplex": "duplex",
        "penthouse": "penthouse",
        "villa": "villa",
        "twin house": "twin_house",
        "townhouse": "townhouse",
        "chalet": "chalet",
        "bungalow": "bungalow",
        "hotel apartment": "hotel_apartment",
        "cabin": "cabin",
        "bulk sale unit": "bulk_sale_unit",
        "land": "land",
        "palace": "palace",
        "full floor": "full_floor",
        "whole building": "whole_building",
        "roof": "roof",
    }
    if s in mapping:
        return mapping[s]
    return s  



def main():
    print(f"Loading raw data from: {RAW_CSV!r}")
    df = pd.read_csv(RAW_CSV)

    print("Cleaning price and down_payment...")
    df["price_egp"] = df["price"].apply(parse_egp_amount)
    df["down_payment_egp"] = df["down_payment"].apply(parse_egp_amount)

    print("Parsing size...")
    size_parsed = df["size"].apply(parse_size)
    df["size_sqft"] = size_parsed.apply(lambda x: x[0])
    df["size_sqm"] = size_parsed.apply(lambda x: x[1])

    print("Cleaning bedrooms...")
    bed_parsed = df["bedrooms"].apply(parse_bedrooms)
    df["bedrooms_clean"] = bed_parsed.apply(lambda x: x[0])
    df["has_maid_room"] = bed_parsed.apply(lambda x: x[1])

    print("Cleaning bathrooms...")
    df["bathrooms_clean"] = df["bathrooms"].apply(parse_bathrooms)

    print("Parsing available_from dates...")
    df["available_from_date"] = df["available_from"].apply(parse_available_date)

    print("Splitting location into components...")
    loc_cols = df["location"].apply(split_location)
    loc_cols.columns = ["project_name", "neighbourhood", "city_area", "governorate"]
    df = pd.concat([df, loc_cols], axis=1)

    print("Normalizing property type...")
    df["property_type"] = df["type"].apply(normalize_property_type)

    print("Dropping rows with missing essential values...")
    before = len(df)
    df = df.dropna(subset=["price_egp", "city_area", "governorate"])
    after = len(df)
    print(f"Dropped {before - after} rows with missing price or location.")

    print(f"Saving cleaned data to: {OUT_CSV!r}")
    df.to_csv(OUT_CSV, index=False)
    print("Done.")
    print("Final shape:", df.shape)


if __name__ == "__main__":
    main()
