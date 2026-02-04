import pandas as pd
import numpy as np
from datetime import datetime
import re

print("=== DATA CLEANING PROCESS ===")
print("=" * 50)

# Load the data
df = pd.read_csv('friskvard_data.csv')
print(f"Original data: {df.shape[0]} rows, {df.shape[1]} columns")

# ===== 1. INITIAL EXPLORATION =====
print("\n1️⃣ INITIAL EXPLORATION")
print("-" * 30)

print(f"Column names: {list(df.columns)}")
print(f"\nData types:\n{df.dtypes}")

print(f"\nMissing values:")
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_percent
})
print(missing_df[missing_df['Missing Count'] > 0])

# ===== 2. STANDARDIZE TEXT COLUMNS =====
print("\n2️⃣ STANDARDIZING TEXT COLUMNS")
print("-" * 30)

# Clean member types
if 'medlemstyp' in df.columns:
    df['medlemstyp'] = df['medlemstyp'].astype(str).str.strip().str.title()
    print(f"Member types found: {df['medlemstyp'].unique()}")

# Clean status
if 'status' in df.columns:
    df['status'] = df['status'].astype(str).str.strip().str.title()
    print(f"Status values found: {df['status'].unique()}")

# Clean pass names
if 'passnamn' in df.columns:
    df['passnamn'] = df['passnamn'].astype(str).str.strip().str.title()
    print(f"Pass names (sample): {df['passnamn'].unique()[:10]}")

# Clean facility names
if 'anläggning' in df.columns:
    df['anläggning'] = df['anläggning'].astype(str).str.strip().str.title()
    print(f"Facilities (sample): {df['anläggning'].unique()[:10]}")

# ===== 3. FIX DATE COLUMNS =====
print("\n3️⃣ FIXING DATE COLUMNS")
print("-" * 30)

def clean_date(date_val):
    if pd.isna(date_val):
        return pd.NaT
    
    date_str = str(date_val).strip()
    
    # Remove common issues
    date_str = date_str.replace('"', '').replace("'", "")
    
    # Common patterns in your data
    patterns = [
        '%Y-%m-%d',          # 2024-10-01
        '%d/%m/%Y',          # 27/09/2024
        '%Y/%m/%d',          # 2024/09/18
        '%B %d, %Y',         # July 03, 2023
        '%b %d, %Y',         # Jul 3, 2023
        '%d %B %Y',          # 03 July 2023
        '%Y-%m-%d %H:%M',    # 2024-10-01 11:00
        '%m/%d/%Y',          # 07/12/2024
        '%d-%m-%Y',          # 12-07-2024
    ]
    
    for pattern in patterns:
        try:
            return pd.to_datetime(date_str, format=pattern)
        except:
            continue
    
    # Fallback: use pandas flexible parser
    try:
        return pd.to_datetime(date_str, errors='coerce')
    except:
        return pd.NaT

# Clean all date columns
date_columns = [col for col in df.columns if 'datum' in col.lower() or 'date' in col.lower()]
print(f"Date columns found: {date_columns}")

for col in date_columns:
    df[f'{col}_clean'] = df[col].apply(clean_date)
    valid_dates = df[f'{col}_clean'].notna().sum()
    print(f"  {col}: {valid_dates}/{len(df)} valid dates")

# ===== 4. HANDLE NUMERIC COLUMNS =====
print("\n4️⃣ HANDLING NUMERIC COLUMNS")
print("-" * 30)

# Clean birth year
if 'födelseår' in df.columns:
    # Convert to numeric, coerce errors
    df['födelseår'] = pd.to_numeric(df['födelseår'], errors='coerce')
    
    # Calculate age
    current_year = datetime.now().year
    df['age'] = current_year - df['födelseår']
    
    # Check for impossible ages
    impossible_ages = df[(df['age'] < 10) | (df['age'] > 100)].shape[0]
    print(f"Birth year -> Age calculated")
    print(f"  Age range: {df['age'].min():.0f} to {df['age'].max():.0f}")
    print(f"  Impossible ages (<10 or >100): {impossible_ages}")

# Clean monthly cost
if 'månadskostnad' in df.columns:
    df['månadskostnad'] = pd.to_numeric(df['månadskostnad'], errors='coerce')
    print(f"Monthly cost range: {df['månadskostnad'].min()} to {df['månadskostnad'].max()}")

# Clean feedback rating
if 'feedback_betyg' in df.columns:
    df['feedback_betyg'] = pd.to_numeric(df['feedback_betyg'], errors='coerce')
    valid_ratings = df['feedback_betyg'].notna().sum()
    print(f"Feedback ratings: {valid_ratings}/{len(df)} valid ratings")

# ===== 5. HANDLE MISSING VALUES =====
print("\n5️⃣ HANDLING MISSING VALUES")
print("-" * 30)

print("Missing values before cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# Strategy: Fill with appropriate values
fill_strategies = {
    'numeric': 'median',
    'categorical': 'mode',
    'text': 'Unknown'
}

# Fill numeric columns with median
numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

# Fill categorical/text columns
text_cols = df.select_dtypes(include=['object']).columns
for col in text_cols:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna('Unknown')

print("\nMissing values after cleaning:")
remaining_missing = df.isnull().sum()[df.isnull().sum() > 0]
if len(remaining_missing) > 0:
    print(remaining_missing)
else:
    print("✅ No missing values remaining!")

# ===== 6. CHECK FOR DUPLICATES =====
print("\n6️⃣ CHECKING FOR DUPLICATES")
print("-" * 30)

# Check for duplicate booking IDs
if 'bokning_id' in df.columns:
    duplicates = df['bokning_id'].duplicated().sum()
    print(f"Duplicate booking IDs: {duplicates}")

# Check for duplicate pass IDs
if 'pass_id' in df.columns:
    duplicates = df['pass_id'].duplicated().sum()
    print(f"Duplicate pass IDs: {duplicates}")

# ===== 7. SAVE CLEANED DATA =====
print("\n7️⃣ SAVING CLEANED DATA")
print("-" * 30)

# Save to new CSV file
output_file = 'friskvard_data_clean.csv'
df.to_csv(output_file, index=False, encoding='utf-8')
print(f"✅ Cleaned data saved as: {output_file}")
print(f"Final shape: {df.shape[0]} rows, {df.shape[1]} columns")

# ===== 8. SUMMARY REPORT =====
print("\n8️⃣ CLEANING SUMMARY REPORT")
print("-" * 30)
print(f"Total rows processed: {df.shape[0]:,}")
print(f"Total columns: {df.shape[1]}")
print(f"Member types: {df['medlemstyp'].nunique()} types")
print(f"Pass types: {df['passnamn'].nunique()} types")
print(f"Facilities: {df['anläggning'].nunique()} locations")
print(f"Instructors: {df['instruktör'].nunique()} instructors")

if 'feedback_betyg' in df.columns:
    avg_rating = df['feedback_betyg'].mean()
    print(f"Average feedback rating: {avg_rating:.2f}/5")

print("\n✅ Data cleaning completed successfully!")
