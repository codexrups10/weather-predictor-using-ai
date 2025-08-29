:: STEP 1 - Go to project folder
cd C:\Users\<YourName>\Desktop\weather_prediction_project

:: STEP 2 - Create virtual environment
python -m venv venv

:: STEP 3 - Activate it
venv\Scripts\activate

:: STEP 4 - Upgrade pip
python -m pip install --upgrade pip

:: STEP 5 - Install dependencies
:: (use requirements.txt if available, else install manually)
pip install -r requirements.txt
:: OR
pip install django==4.2.7 numpy pandas scikit-learn joblib tensorflow-cpu==2.10.1

:: STEP 6 - Apply migrations
python manage.py migrate

:: STEP 7 - Run server
python manage.py runserver

:: STEP 8 - Open in browser
:: http://127.0.0.1:8000/
:: http://127.0.0.1:8000/api/health/

:: NOTE:
:: - Put lstm_weather_model.h5, scaler.pkl, and dummy_weather_data.csv inside ml_models/ folder before running.
