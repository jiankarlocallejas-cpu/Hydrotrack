from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import json

app = Flask(__name__)
CORS(app)

# === Initial Hardcoded MLR Equation ===
# Example: water = 50 + 0.8*household_size + 0.5*income + 1.2*lot_area
coefficients = {
    "intercept": 50.0,
    "household_size": 0.8,
    "income": 0.5,
    "lot_area": 1.2
}

# Store data for retraining
DATA_FILE = "data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        stored_data = json.load(f)
else:
    stored_data = {"X": [], "y": []}


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    size = float(data.get("household_size", 0))
    income = float(data.get("income", 0))
    area = float(data.get("lot_area", 0))

    # Prediction using current equation
    y_pred = (
        coefficients["intercept"]
        + coefficients["household_size"] * size
        + coefficients["income"] * income
        + coefficients["lot_area"] * area
    )

    # Save this new record for possible retraining
    stored_data["X"].append([size, income, area])
    stored_data["y"].append(y_pred)

    with open(DATA_FILE, "w") as f:
        json.dump(stored_data, f)

    return jsonify({"prediction": y_pred})


@app.route("/retrain", methods=["POST"])
def retrain():
    global coefficients
    if len(stored_data["X"]) < 5:  # Require minimum data points
        return jsonify({"message": "Not enough data to retrain yet."})

    X = np.array(stored_data["X"])
    y = np.array(stored_data["y"])

    model = LinearRegression()
    model.fit(X, y)

    coefficients = {
        "intercept": model.intercept_.item(),
        "household_size": model.coef_[0].item(),
        "income": model.coef_[1].item(),
        "lot_area": model.coef_[2].item(),
    }

    return jsonify({"message": "Model retrained", "coefficients": coefficients})


@app.route("/equation", methods=["GET"])
def get_equation():
    return jsonify(coefficients)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
