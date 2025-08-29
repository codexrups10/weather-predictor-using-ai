from django.apps import AppConfig


class WeatherPredictorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather_predictor'

    def ready(self):
        """Load ML models when Django starts"""
        from . import ml_utils
        ml_utils.load_models()
