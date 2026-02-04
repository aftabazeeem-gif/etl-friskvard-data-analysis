print("Hello! Starting analysis...")

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
    
    # Try to load the data
    df = pd.read_csv('friskvard_data.csv')
    print(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
    
    print("\n📋 First few columns:")
    for i, col in enumerate(df.columns[:10], 1):
        print(f"  {i}. {col}")
    
    print("\n🔍 First row sample:")
    print(df.iloc[0].to_dict())
    
except ImportError:
    print("❌ Pandas not installed. Run: pip install pandas")
except FileNotFoundError:
    print("❌ friskvard_data.csv not found in current folder")
    import os
    print(f"   Current folder: {os.getcwd()}")
    print(f"   Files here: {os.listdir('.')}")
except Exception as e:
    print(f"❌ Error: {e}")
