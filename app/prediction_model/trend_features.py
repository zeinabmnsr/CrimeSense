import pandas as pd

def add_trend_features(df):
    df = df.sort_values(by=["location", "crime_type", "year", "quarter"])
    df["prev_incidents"] = df.groupby(["location", "crime_type"])["incidents"].shift(1)
    df["growth_rate"] = (df["incidents"] - df["prev_incidents"]) / df["prev_incidents"].replace(0, 1)
    df["rolling_avg_3q"] = df.groupby(["location", "crime_type"])["incidents"].transform(lambda x: x.rolling(3).mean())

    #X = df[['location_enc', 'crime_type_enc', 'year_enc', 'quarter_enc', 'description_enc', 'trend_label_enc', 'rolling_avg_3q', 'prev_incidents']]
   
    def assign_trend(growth):
        if pd.isna(growth):
            return "unknown"
        elif growth > 0.15:
            return "increasing"
        elif growth < -0.10:
            return "decreasing"
        else:
            return "stable"

    df['prev_incidents'] = df['prev_incidents'].fillna(df['incidents'].mean())
    df['rolling_avg_3q'] = df['rolling_avg_3q'].fillna(df['incidents'].mean())
    df["trend_label"] = df["growth_rate"].apply(assign_trend)  # ✅ <--- this line is crucial!

    return df
