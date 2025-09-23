from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

app = Flask(__name__)
CORS(app)  

coef = {
    "household_size": 10.0,
    "appliances": 5.0,
    "outdoor_use": 2.0,
    "income": 0.01,
    "season_summer": 3.0,
    "season_rainy": -2.0
}
intercept = 50.0

# Store past data for dynamic update
past_data = pd.DataFrame(columns=["household_size","appliances","outdoor_use","income","season_summer","season_rainy","meter_reading"])

@app.route("/predict", methods=["POST"])
def predict():
    global coef, intercept, past_data
    data = request.get_json()

    # Encode season
    season_summer = 1 if data.get("season","").lower() == "summer" else 0
    season_rainy = 1 if data.get("season","").lower() == "rainy" else 0

    # Fill missing income
    income = data.get("income")
    income = float(income) if income is not None else 0.0

    X_input = np.array([
        data["household_size"],
        data["appliances"],
        data["outdoor_use"],
        income,
        season_summer,
        season_rainy
    ]).reshape(1, -1)

    # Compute prediction using current coefficients
    coef_vector = np.array([
        coef["household_size"],
        coef["appliances"],
        coef["outdoor_use"],
        coef["income"],
        coef["season_summer"],
        coef["season_rainy"]
    ])
    prediction = float(np.dot(X_input, coef_vector) + intercept)

    # Store new data
    new_row = {
        "household_size": data["household_size"],
        "appliances": data["appliances"],
        "outdoor_use": data["outdoor_use"],
        "income": income,
        "season_summer": season_summer,
        "season_rainy": season_rainy,
        "meter_reading": data["meter_reading"]
    }
    past_data = pd.concat([past_data, pd.DataFrame([new_row])], ignore_index=True)

    # Update model dynamically if we have at least 5 records
    if len(past_data) >= 5:
        X_train = past_data[["household_size","appliances","outdoor_use","income","season_summer","season_rainy"]]
        y_train = past_data["meter_reading"]
        model = LinearRegression()
        model.fit(X_train, y_train)
        coef_vector = model.coef_
        intercept = model.intercept_
        # Update coefficient dict
        coef = dict(zip(["household_size","appliances","outdoor_use","income","season_summer","season_rainy"], coef_vector))

        # Compute metrics
        y_pred = model.predict(X_train)
        metrics = {
            "R2": round(r2_score(y_train, y_pred),3),
            "MAE": round(mean_absolute_error(y_train, y_pred),3),
            "RMSE": round(np.sqrt(mean_squared_error(y_train, y_pred)),3)
        }
    else:
        metrics = {"R2": None, "MAE": None, "RMSE": None}

    # Variable importance (absolute normalized)
    importance_vals = np.abs(list(coef.values()))
    importance_vals = importance_vals / np.sum(importance_vals)
    importance = dict(zip(coef.keys(), [round(v,3) for v in importance_vals]))

    return jsonify({
        "prediction": round(prediction,2),
        "importance": importance,
        "metrics": metrics
    })

if __name__ == "__main__":
    app.run(debug=True)
