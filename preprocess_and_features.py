
import numpy as np
import pandas as pd

CLEANED = "cleaned_listings.csv"
OUTFILE = "properties.xlsx"

def roi_from_location(governorate, city_area):
    gov = str(governorate).lower()
    area = str(city_area).lower()

    if "cairo" in gov:
        if "new cairo" in area or "5" in area or "settlement" in area or "zayed" in area or "october" in area:
            return 0.10
        return 0.085

    if "alex" in gov:
        return 0.085

    coast_keywords = ["coast", "sokhna", "marassi", "gouna", "sahel", "north"]
    if any(k in area for k in coast_keywords):
        return 0.14

    if "capital" in area or "capital" in gov:
        return 0.12

    return 0.09


def adjust_roi_property_type(base_roi, ptype):
    t = str(ptype).lower()
    if "villa" in t:
        return base_roi - 0.015
    if "chalet" in t or "cabin" in t:
        return base_roi + 0.03
    if "duplex" in t:
        return base_roi + 0.01
    return base_roi


def adjust_roi_price(base_roi, price):
    if price < 2_000_000:
        return base_roi - 0.01
    if 2_000_000 <= price <= 10_000_000:
        return base_roi + 0.01
    if price > 15_000_000:
        return base_roi - 0.02
    return base_roi


def adjust_roi_payment(base_roi, down_payment):
    if pd.isna(down_payment):
        return base_roi
    if down_payment >= 1_000_000:
        return base_roi + 0.005
    return base_roi

def compute_risk(governorate, city_area, ptype, price):
    gov = str(governorate).lower()
    area = str(city_area).lower()
    t = str(ptype).lower()

    if any(k in area for k in ["coast", "sokhna", "gouna", "sahel", "marassi"]):
        return 3
    if price > 15_000_000:
        return 3
    if "chalet" in t or "cabin" in t:
        return 3

    if "cairo" in gov and ("new cairo" in area or "5" in area or "zayed" in area or "october" in area):
        return 1
    if price < 3_000_000 and "apartment" in t:
        return 1

    return 2


def main():
    print("Loading cleaned data...")
    df = pd.read_csv(CLEANED)

    print("Computing ROI...")
    base_roi = df.apply(lambda r: roi_from_location(r["governorate"], r["city_area"]), axis=1)
    roi1 = [adjust_roi_property_type(br, t) for br, t in zip(base_roi, df["property_type"])]
    roi2 = [adjust_roi_price(r, p) for r, p in zip(roi1, df["price_egp"])]
    final_roi = [adjust_roi_payment(r, d) for r, d in zip(roi2, df["down_payment_egp"])]

    df["expected_roi"] = np.clip(final_roi, 0.05, 0.22)

    print("Computing risk...")
    df["base_risk"] = df.apply(
        lambda r: compute_risk(r["governorate"], r["city_area"], r["property_type"], r["price_egp"]),
        axis=1
    )

    print("Selecting final columns...")
    df_final = pd.DataFrame({
        "name": df["project_name"].fillna("Property"),
        "city": df["city_area"].fillna(df["governorate"]),
        "property_type": df["property_type"],
        "price": df["price_egp"],
        "expected_roi": df["expected_roi"],
        "base_risk": df["base_risk"],
        "url": df["url"]  # KEEP URL
    })

    print("Saving final dataset to properties.xlsx ...")
    df_final.to_excel(OUTFILE, index=False)
    print("DONE ✔")
    print("Final shape:", df_final.shape)


if __name__ == "__main__":
    main()
