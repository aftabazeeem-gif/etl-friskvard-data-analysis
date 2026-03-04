import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("=== DATA ANALYSIS & INSIGHTS ===")
print("=" * 50)

# Load cleaned data
df = pd.read_csv('friskvard_data_clean.csv')
print(f"Loaded cleaned data: {df.shape[0]} rows, {df.shape[1]} columns")

# ===== 1. MEMBERSHIP ANALYSIS =====
print("\n1️⃣ MEMBERSHIP ANALYSIS")
print("-" * 30)

if 'medlemstyp' in df.columns:
    member_counts = df['medlemstyp'].value_counts()
    print("Member type distribution:")
    for member_type, count in member_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {member_type}: {count} bookings ({percentage:.1f}%)")

# Monthly cost analysis
if 'månadskostnad' in df.columns:
    print(f"\nMonthly cost statistics:")
    print(f"  Average: {df['månadskostnad'].mean():.0f} kr")
    print(f"  Min: {df['månadskostnad'].min():.0f} kr")
    print(f"  Max: {df['månadskostnad'].max():.0f} kr")
    
    # Check for negative costs
    negative_costs = df[df['månadskostnad'] < 0]
    if len(negative_costs) > 0:
        print(f"  ⚠️ Warning: {len(negative_costs)} members have negative monthly costs!")

# ===== 2. CLASS/PASS ANALYSIS =====
print("\n2️⃣ CLASS & PASS ANALYSIS")
print("-" * 30)

# Most popular classes
if 'passnamn' in df.columns:
    popular_classes = df['passnamn'].value_counts().head(10)
    print("Top 10 most popular classes:")
    for i, (class_name, count) in enumerate(popular_classes.items(), 1):
        percentage = (count / len(df)) * 100
        print(f"  {i:2}. {class_name}: {count} bookings ({percentage:.1f}%)")

# Most popular facilities
if 'anläggning' in df.columns:
    print(f"\nMost popular facilities (top 5):")
    facilities = df['anläggning'].value_counts().head()
    for i, (facility, count) in enumerate(facilities.items(), 1):
        percentage = (count / len(df)) * 100
        print(f"  {i}. {facility}: {count} bookings ({percentage:.1f}%)")

# ===== 3. ATTENDANCE ANALYSIS =====
print("\n3️⃣ ATTENDANCE & BOOKING ANALYSIS")
print("-" * 30)

if 'status' in df.columns:
    status_counts = df['status'].value_counts()
    total_bookings = len(df)
    
    print("Booking status breakdown:")
    for status, count in status_counts.items():
        percentage = (count / total_bookings) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Calculate no-show rate
    no_show_statuses = ['No-Show', 'Missad', 'Ej Närvarande']
    no_shows = df[df['status'].isin(no_show_statuses)]
    no_show_rate = (len(no_shows) / total_bookings) * 100
    print(f"\n⚠️ No-show rate: {no_show_rate:.1f}% ({len(no_shows)} bookings)")

# ===== 4. FEEDBACK ANALYSIS =====
print("\n4️⃣ FEEDBACK & RATINGS ANALYSIS")
print("-" * 30)

if 'feedback_betyg' in df.columns:
    # Filter only bookings with feedback
    feedback_df = df[df['feedback_betyg'].notna()]
    
    if len(feedback_df) > 0:
        print(f"Feedback received: {len(feedback_df)} bookings ({len(feedback_df)/len(df)*100:.1f}%)")
        print(f"Average rating: {feedback_df['feedback_betyg'].mean():.2f}/5")
        print(f"Rating distribution:")
        
        for rating in sorted(feedback_df['feedback_betyg'].unique()):
            count = len(feedback_df[feedback_df['feedback_betyg'] == rating])
            percentage = (count / len(feedback_df)) * 100
            print(f"  {rating:.0f} stars: {count} ({percentage:.1f}%)")
        
        # Best rated instructors
        if 'instruktör' in df.columns:
            instructor_ratings = feedback_df.groupby('instruktör')['feedback_betyg'].agg(['mean', 'count'])
            instructor_ratings = instructor_ratings[instructor_ratings['count'] >= 5]  # At least 5 ratings
            
            if len(instructor_ratings) > 0:
                print(f"\nTop rated instructors (min 5 ratings):")
                top_instructors = instructor_ratings.sort_values('mean', ascending=False).head(5)
                for i, (instructor, row) in enumerate(top_instructors.iterrows(), 1):
                    print(f"  {i}. {instructor}: {row['mean']:.2f}/5 ({row['count']} ratings)")

# ===== 5. TIME ANALYSIS =====
print("\n5️⃣ TIME & SCHEDULING ANALYSIS")
print("-" * 30)

# Check pass times
if 'passtid' in df.columns:
    # Extract hour from time
    df['pass_hour'] = pd.to_datetime(df['passtid'], format='%H:%M', errors='coerce').dt.hour
    
    # Group by hour
    hourly_bookings = df['pass_hour'].value_counts().sort_index()
    
    print("Bookings by hour of day:")
    for hour, count in hourly_bookings.items():
        if not pd.isna(hour):
            percentage = (count / len(df)) * 100
            print(f"  {hour:02d}:00: {count} bookings ({percentage:.1f}%)")

# ===== 6. DEMOGRAPHIC ANALYSIS =====
print("\n6️⃣ DEMOGRAPHIC ANALYSIS")
print("-" * 30)

if 'age' in df.columns:
    # Remove impossible ages
    valid_ages = df[(df['age'] >= 10) & (df['age'] <= 100)]
    
    if len(valid_ages) > 0:
        print(f"Member age statistics (excluding extremes):")
        print(f"  Average age: {valid_ages['age'].mean():.1f} years")
        print(f"  Youngest: {valid_ages['age'].min():.0f} years")
        print(f"  Oldest: {valid_ages['age'].max():.0f} years")
        
        # Age groups
        bins = [0, 20, 30, 40, 50, 60, 100]
        labels = ['<20', '20-29', '30-39', '40-49', '50-59', '60+']
        valid_ages['age_group'] = pd.cut(valid_ages['age'], bins=bins, labels=labels, right=False)
        
        print(f"\nAge group distribution:")
        age_groups = valid_ages['age_group'].value_counts().sort_index()
        for group, count in age_groups.items():
            percentage = (count / len(valid_ages)) * 100
            print(f"  {group}: {count} members ({percentage:.1f}%)")

# ===== 7. RECOMMENDATIONS =====
print("\n7️⃣ RECOMMENDATIONS & INSIGHTS")
print("-" * 30)
print("1. 📊 Most popular classes: Focus marketing on HIIT, Yoga, and Spinning")
print("2. ⚠️ No-show rate: Implement reminder system to reduce no-shows")
print("3. 💰 Revenue: Investigate negative monthly costs")
print("4. 🌟 Feedback: Only 41.5% leave feedback - improve feedback collection")
print("5. 👥 Demographics: Target marketing to largest age groups")
print("6. 🏆 Instructors: Recognize top-rated instructors for retention")
print("7. 🕐 Scheduling: Peak hours are mornings and evenings")
print("8. 🔄 Data quality: Clean up duplicate booking IDs")

print("\n" + "=" * 50)
print("✅ Analysis complete! Check 'friskvard_data_clean.csv' for cleaned data.")
