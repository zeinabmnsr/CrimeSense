import pandas as pd 
import numpy as np 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder 
import joblib 
import os 

def encode_and_split_data(df):
    location_encoder = LabelEncoder()
    year_encoder = LabelEncoder()
    quarter_encoder = LabelEncoder()
    desc_encoder = LabelEncoder()
    crime_type_encoder = LabelEncoder()
    trend_encoder = LabelEncoder()

    df['location_enc'] = location_encoder.fit_transform(df['location'])
    df['year_enc'] = year_encoder.fit_transform(df['year'])
    df['quarter_enc'] = quarter_encoder.fit_transform(df['quarter'])
    df['description_enc'] = desc_encoder.fit_transform(df['description'])
    df['crime_type_enc'] = crime_type_encoder.fit_transform(df['crime_type'])
    df["trend_label_enc"] = trend_encoder.fit_transform(df["trend_label"])
    
    df['rolling_avg_3q'] = df['rolling_avg_3q'].fillna(df['incidents'].mean())

    base_dir = os.path.dirname(__file__)
    encoder_dir = os.path.join(base_dir, "encoders")
    os.makedirs(encoder_dir, exist_ok=True)
    
    joblib.dump(location_encoder, os.path.join(encoder_dir, "location_encoder.pkl"))
    joblib.dump(year_encoder, os.path.join(encoder_dir, "year_encoder.pkl"))
    joblib.dump(quarter_encoder, os.path.join(encoder_dir, "quarter_encoder.pkl"))
    joblib.dump(desc_encoder, os.path.join(encoder_dir, "desc_encoder.pkl"))
    joblib.dump(crime_type_encoder, os.path.join(encoder_dir, "crime_type_encoder.pkl"))
    joblib.dump(trend_encoder, os.path.join(encoder_dir, "trend_encoder.pkl"))

    X = df[['location_enc','crime_type_enc', 'year_enc', 'quarter_enc', 'description_enc', 'trend_label_enc', 'rolling_avg_3q']]
    y = df[['incidents']].apply(lambda x: np.log1p(x))  # apply log(1 + x)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test