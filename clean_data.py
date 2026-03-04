import pandas as pd
import numpy as np
from datetime import datetime


# -----------------------------
# NORMALIZATION MAPS (G-krav)
# -----------------------------
MEMBERSHIP_MAP = {
    "bas": "Basic",
    "basic": "Basic",
    "grund": "Basic",
    "premium": "Premium",
    "plus": "Premium",
    "gold": "Premium",
    "student": "Student",
    "studerande": "Student",
}

STATUS_MAP = {
    # Completed
    "genomförd": "Completed",
    "klar": "Completed",
    "deltog": "Completed",
    "completed": "Completed",

    # Cancelled
    "cancelled": "Cancelled",
    "canceled": "Cancelled",
    "struken": "Cancelled",
    "avbokad": "Cancelled",
    "avbokat": "Cancelled",
    "inställd": "Cancelled",

    # No Show
    "missad": "No Show",
    "ej närvarande": "No Show",
    "no show": "No Show",
    "no-show": "No Show",
    "noshow": "No Show",
}


def normalize_facility(x: str) -> str:
    if not isinstance(x, str):
        return "Unknown"
    s = x.strip().lower()

    # Malmö
    if "malmö" in s and ("västra hamnen" in s or "vastra hamnen" in s or " vh" in s or s.endswith("vh")):
        return "Malmö Västra Hamnen"
    if "malmö" in s and ("centrum" in s or s in ["malmö c", "malmö centrum", "malmö c."]):
        return "Malmö Centrum"

    # Stockholm
    if ("stockholm" in s or "sthlm" in s) and ("södermalm" in s or "sodermalm" in s):
        return "Stockholm Södermalm"
    if ("stockholm" in s or "sthlm" in s) and ("kungsholmen" in s):
        return "Stockholm Kungsholmen"
    if "stockholm" in s and "city" in s:
        return "Stockholm City"

    # Göteborg
    if ("göteborg" in s or "gbg" in s) and ("centrum" in s or s.endswith(" c") or "göteborg c" in s):
        return "Göteborg Centrum"
    if ("göteborg" in s or "gbg" in s) and ("hisingen" in s):
        return "Göteborg Hisingen"

    # Other cities
    if "uppsala" in s:
        return "Uppsala"
    if "västerås" in s or "vasteras" in s:
        return "Västerås"
    if "örebro" in s or "orebro" in s:
        return "Örebro"
    if "linköping" in s or "linkoping" in s:
        return "Linköping"
    if "lund" in s:
        return "Lund"

    return "Unknown"


def normalize_class(x: str) -> str:
    if not isinstance(x, str):
        return "Unknown"
    s = x.strip().lower()

    if "yoga" in s:
        return "Yoga"
    if "pilates" in s:
        return "Pilates"
    if "cykel" in s or "spinning" in s:
        return "Cykel"
    if "styrk" in s:
        return "Styrketräning"
    if "hiit" in s:
        return "HIIT"
    if "box" in s:
        return "Box"
    if "cross" in s:
        return "Crossfit"

    return x.strip().title()


def clean_date(date_val):
    """Parse messy date strings to pandas datetime. Returns NaT if cannot parse."""
    if pd.isna(date_val):
        return pd.NaT

    date_str = str(date_val).strip().replace('"', "").replace("'", "")

    patterns = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y",
        "%d-%m-%Y",
    ]

    for pattern in patterns:
        try:
            return pd.to_datetime(date_str, format=pattern)
        except Exception:
            continue

    return pd.to_datetime(date_str, errors="coerce")


def clean_dataset(input_csv: str, output_csv: str) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print(f"📥 Cleaning dataset: {input_csv}")
    print("=" * 60)

    df = pd.read_csv(input_csv)
    print(f"Original: {df.shape[0]} rows, {df.shape[1]} cols")

    # -----------------------------
    # 1) Normalize categorical columns (explicit mappings)
    # -----------------------------
    print("\n✅ NORMALIZATION (G-krav)")

    if "medlemstyp" in df.columns:
        before = df["medlemstyp"].nunique()
        df["medlemstyp"] = df["medlemstyp"].astype(str).str.strip().str.lower().replace(MEMBERSHIP_MAP)
        after = df["medlemstyp"].nunique()
        print(f"medlemstyp: {before} -> {after}")

    if "status" in df.columns:
        before = df["status"].nunique()
        df["status"] = df["status"].astype(str).str.strip().str.lower().replace(STATUS_MAP)
        after = df["status"].nunique()
        print(f"status: {before} -> {after}")

    if "anläggning" in df.columns:
        before = df["anläggning"].nunique()
        df["anläggning"] = df["anläggning"].apply(normalize_facility)
        after = df["anläggning"].nunique()
        print(f"anläggning: {before} -> {after}")

    if "passnamn" in df.columns:
        before = df["passnamn"].nunique()
        df["passnamn"] = df["passnamn"].apply(normalize_class)
        after = df["passnamn"].nunique()
        print(f"passnamn: {before} -> {after}")

    # -----------------------------
    # 2) Clean date columns
    # -----------------------------
    print("\n📅 DATE CLEANING")
    date_columns = [col for col in df.columns if "datum" in col.lower() or "date" in col.lower()]
    for col in date_columns:
        df[f"{col}_clean"] = df[col].apply(clean_date)
        valid = df[f"{col}_clean"].notna().sum()
        print(f"{col}: {valid}/{len(df)} valid")

    # -----------------------------
    # 3) Numeric cleanup + age feature
    # -----------------------------
    print("\n🔢 NUMERIC CLEANING")
    if "födelseår" in df.columns:
        df["födelseår"] = pd.to_numeric(df["födelseår"], errors="coerce")
        current_year = datetime.now().year
        df["age"] = current_year - df["födelseår"]

    if "månadskostnad" in df.columns:
        df["månadskostnad"] = pd.to_numeric(df["månadskostnad"], errors="coerce")

    if "feedback_betyg" in df.columns:
        df["feedback_betyg"] = pd.to_numeric(df["feedback_betyg"], errors="coerce")

    # -----------------------------
    # 4) Missing values
    # -----------------------------
    print("\n🧹 MISSING VALUES")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna(df[col].median())

    text_cols = df.select_dtypes(include=["object"]).columns
    for col in text_cols:
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna("Unknown")

    # -----------------------------
    # 5) Save cleaned output
    # -----------------------------
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"\n✅ Saved cleaned file: {output_csv}")
    print(f"Final: {df.shape[0]} rows, {df.shape[1]} cols")

    # -----------------------------
    # 6) Summary report (teacher-friendly)
    # -----------------------------
    print("\n📊 SUMMARY REPORT")
    if "medlemstyp" in df.columns:
        print("Member types:", df["medlemstyp"].value_counts().to_dict())
    if "status" in df.columns:
        print("Status values:", df["status"].value_counts().to_dict())
    if "anläggning" in df.columns:
        print("Facilities:", df["anläggning"].value_counts().head(15).to_dict())
    if "passnamn" in df.columns:
        print("Top passnamn:", df["passnamn"].value_counts().head(10).to_dict())

    return df


if __name__ == "__main__":
    # MAIN dataset
    clean_dataset("friskvard_data.csv", "friskvard_data_clean.csv")

    # VALIDATION dataset (if exists)
    try:
        clean_dataset("friskvard_validation.csv", "friskvard_validation_clean.csv")
    except FileNotFoundError:
        print("\n⚠️ friskvard_validation.csv not found. (If you have it, place it in the same folder and run again.)")