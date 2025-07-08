from sklearn.metrics import r2_score, mean_absolute_error

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)

    print("📊 R² Score:", r2_score(y_test, y_pred))
    print("📉 MAE:", mean_absolute_error(y_test, y_pred))

    return r2_score(y_test, y_pred), mean_absolute_error(y_test, y_pred)
