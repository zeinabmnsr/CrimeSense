import joblib
import numpy as np

# Load encoders
location_dec = joblib.load("app/prediction_model/encoders/location_encoder.pkl")
year_enc = joblib.load("app/prediction_model/encoders/year_encoder.pkl")
quarter_enc = joblib.load("app/prediction_model/encoders/quarter_encoder.pkl")
crime_type_enc = joblib.load("app/prediction_model/encoders/crime_type_encoder.pkl")
trend_enc = joblib.load("app/prediction_model/encoders/trend_encoder.pkl")
desc_enc = joblib.load("app/prediction_model/encoders/desc_encoder.pkl")

# Load model
model = joblib.load("app/prediction_model/model/incidents_predictor.pkl")


def predict_incidents(crime_type, year, quarter, trend_label, description="unknown"):
    try:
        input_vector = [
            0,  # dummy location_enc
            crime_type_enc.transform([crime_type])[0],
            year_enc.transform([year])[0],
            quarter_enc.transform([quarter])[0],
            desc_enc.transform([description])[0],
            trend_enc.transform([trend_label])[0],
            0  # dummy rolling_avg_3q
        ]
        predicted_log = model.predict([input_vector])[0]
        predicted_incidents = np.expm1(predicted_log)
        return round(predicted_incidents.item())
    except Exception as e:
        return f"Prediction failed: {str(e)}"