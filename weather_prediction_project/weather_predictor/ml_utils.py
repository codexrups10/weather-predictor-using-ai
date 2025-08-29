"""
Machine Learning utilities for weather prediction
Handles model loading, data preprocessing, and prediction logic
"""

import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging

logger = logging.getLogger(__name__)

# Global variables to store loaded models
lstm_model = None
scaler = None
weather_data = None


def load_models():
    """Load LSTM model, scaler, and weather data at Django startup"""
    global lstm_model, scaler, weather_data

    try:
        # Define correct paths from settings
        model_path = settings.ML_MODELS_DIR / "lstm_weather_model.h5"
        scaler_path = settings.ML_MODELS_DIR / "scaler.pkl"
        data_path = settings.ML_MODELS_DIR / "dummy_weather_data.csv"

        # Load LSTM model
        if model_path.exists():
            lstm_model = load_model(model_path, compile=False)
            logger.info(f"✅ LSTM model loaded successfully from {model_path}")
        else:
            logger.error(f"❌ LSTM model not found at {model_path}")

        # Load scaler
        if scaler_path.exists():
            scaler = joblib.load(scaler_path)
            logger.info(f"✅ Scaler loaded successfully from {scaler_path}")
        else:
            logger.error(f"❌ Scaler not found at {scaler_path}")

        # Load weather data
        if data_path.exists():
            weather_data = pd.read_csv(data_path)
            if "date" in weather_data.columns:
                weather_data["date"] = pd.to_datetime(weather_data["date"])
            logger.info(f"✅ Weather data loaded successfully from {data_path}")
        else:
            logger.error(f"❌ Weather data not found at {data_path}")

    except Exception as e:
        logger.error(f"❌ Error loading models: {str(e)}")


def prepare_sequence_data(data, sequence_length=10):
    """Prepare sequence data for LSTM prediction"""
    if len(data) < sequence_length:
        padding_needed = sequence_length - len(data)
        last_row = data.iloc[-1:].values
        padding = np.repeat(last_row, padding_needed, axis=0)
        padded_data = np.vstack([padding, data.values])
        return padded_data[-sequence_length:]
    else:
        return data.iloc[-sequence_length:].values


def preprocess_data_for_prediction(city_data, sequence_length=10):
    """Preprocess data for LSTM prediction"""
    global scaler

    if scaler is None:
        raise Exception("Scaler not loaded. Please ensure models are properly initialized.")

    # Select features for prediction
    feature_cols = ['temperature', 'humidity', 'pressure', 'wind_speed']
    features = city_data[feature_cols]

    # Scale the data
    scaled_features = scaler.transform(features)

    # Prepare sequence
    sequence_data = prepare_sequence_data(pd.DataFrame(scaled_features), sequence_length)

    return np.expand_dims(sequence_data, axis=0)  # Add batch dimension


def make_prediction(city_name="Sample City"):
    """Make weather prediction using LSTM model"""
    global lstm_model, scaler, weather_data

    try:
        if lstm_model is None or scaler is None or weather_data is None:
            raise Exception("Models not properly loaded")

        # Filter for city if dataset has 'city' column
        if "city" in weather_data.columns:
            city_data = weather_data[weather_data["city"].str.lower() == city_name.lower()]
            if city_data.empty:
                raise Exception(f"No weather data found for {city_name}")
        else:
            logger.warning("⚠️ 'city' column missing in dataset, using all data")
            city_data = weather_data

        # Use last 50 days for evaluation
        eval_window = 50
        recent_data = city_data.tail(eval_window + 10)  # extra for sequences

        # Store true & predicted values
        true_values = []
        predicted_values = []

        feature_cols = ['temperature', 'humidity', 'pressure', 'wind_speed']
        scaled_features = scaler.transform(recent_data[feature_cols])

        # Sliding window prediction
        for i in range(len(scaled_features) - 10):
            seq_input = scaled_features[i:i+10]
            X_pred = np.expand_dims(seq_input, axis=0)
            pred_scaled = lstm_model.predict(X_pred, verbose=0)

            dummy_features = np.zeros((1, 4))
            dummy_features[0, 0] = pred_scaled[0, 0]
            pred_actual = scaler.inverse_transform(dummy_features)[0, 0]

            predicted_values.append(pred_actual)
            true_values.append(recent_data["temperature"].values[i+10])

        # Compute metrics
        metrics = {
            "mse": float(round(mean_squared_error(true_values, predicted_values), 4)),
            "mae": float(round(mean_absolute_error(true_values, predicted_values), 4)),
            "r2_score": float(round(r2_score(true_values, predicted_values), 4)),
            "test_samples": len(true_values)
        }

        # ✅ Final latest prediction
        latest_data = city_data.tail(10)
        X_latest = preprocess_data_for_prediction(latest_data)
        latest_scaled = lstm_model.predict(X_latest, verbose=0)

        dummy_latest = np.zeros((1, 4))
        dummy_latest[0, 0] = latest_scaled[0, 0]
        latest_prediction = scaler.inverse_transform(dummy_latest)[0, 0]

        # Historical data (for chart)
        chart_data = city_data.tail(10).copy()
        simplified_records = []
        for _, row in chart_data.iterrows():
            simplified_records.append({
                "date": row["date"].strftime("%Y-%m-%d") if not pd.isna(row["date"]) else None,
                "temperature": float(row["temperature"]) if "temperature" in row else None
            })

        return {
            "success": True,
            "prediction": float(round(latest_prediction, 2)),
            "city": city_name,
            "metrics": metrics,
            "historical_data": simplified_records
        }

    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}")
        return {
            "error": str(e),
            "success": False
        }
