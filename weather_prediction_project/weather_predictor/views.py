"""
Django views for weather prediction application
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from . import ml_utils


def index(request):
    """
    Main page view - renders the weather prediction interface
    """
    context = {
        "title": "Weather Prediction System",
        "description": "LSTM-based weather prediction using machine learning"
    }
    return render(request, "weather_predictor/index.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def predict_weather(request):
    """
    API endpoint for weather prediction
    Accepts POST request with city name and returns prediction
    """
    try:
        # Parse request data safely
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({
                "success": False,
                "error": "Invalid JSON format"
            }, status=400)

        city_name = data.get("city", "").strip()
        print(f"[DEBUG] City received: {city_name}")  # 👈 debug log

        if not city_name:
            return JsonResponse({
                "success": False,
                "error": "City name is required"
            }, status=400)

        # Make prediction
        prediction_result = ml_utils.make_prediction(city_name)
        print(f"[DEBUG] Prediction result from ml_utils: {prediction_result}")  # 👈 debug log

        if not prediction_result.get("success", False):
            return JsonResponse({
                "success": False,
                "error": prediction_result.get("error", "Prediction failed")
            }, status=500)

        prediction_value = prediction_result.get("prediction", None)

        if prediction_value is None:
            return JsonResponse({
                "success": False,
                "error": "Prediction value is None (check ml_utils)"
            }, status=500)

        # ✅ Now metrics come directly from ml_utils.make_prediction
        
        return JsonResponse({
            "success": True,
            "city": city_name,
            "prediction": float(prediction_value),
            "extra_info": prediction_result.get("extra_info", {}),
            "metrics": prediction_result.get("metrics", {}),
            "historical_data": prediction_result.get("historical_data", [])
        }, status=200)

    except Exception as e:
        print(f"[DEBUG] Server error: {e}")  # 👈 debug log
        return JsonResponse({
            "success": False,
            "error": f"Server error: {str(e)}"
        }, status=500)


def model_info(request):
    """
    API endpoint to get model information and metrics
    """
    try:
        return JsonResponse({
            "success": True,
            "model_info": {
                "name": "LSTM Weather Prediction Model",
                "architecture": "Long Short-Term Memory Neural Network",
                "features": ["Temperature", "Humidity", "Pressure", "Wind Speed"],
                "sequence_length": 10,
                "prediction_target": "Next Day Temperature",
                "framework": "TensorFlow/Keras"
            }
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error retrieving model information: {str(e)}"
        }, status=500)


def health_check(request):
    """
    Health check endpoint to verify system status
    """
    try:
        models_loaded = (
            getattr(ml_utils, "lstm_model", None) is not None and
            getattr(ml_utils, "scaler", None) is not None and
            getattr(ml_utils, "weather_data", None) is not None
        )

        return JsonResponse({
            "success": True,
            "status": "healthy" if models_loaded else "models_not_loaded",
            "models_loaded": models_loaded,
            "message": (
                "Weather prediction system is ready"
                if models_loaded else
                "Models are still loading, please try again shortly"
            )
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "status": "error",
            "error": str(e)
        }, status=500)
