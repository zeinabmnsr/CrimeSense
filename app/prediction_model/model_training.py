from sklearn.linear_model import LinearRegression
import joblib
import os

def train_model(X_train, y_train):
    model = LinearRegression() 
    model.fit(X_train, y_train) 

    # Save the trained model to a file
    os.makedirs("app/prediction_model/model", exist_ok=True)
    joblib.dump(model, "app/prediction_model/model/incidents_predictor.pkl")

    print("✅ Model training completed and saved.")

    return model
