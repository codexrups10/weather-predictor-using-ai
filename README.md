# 🌦️ Weather Prediction Web Application

A full-stack **Django-based web application** that predicts next-day weather conditions using **LSTM (Long Short-Term Memory) neural networks** trained on historical weather data.  
The app provides real-time predictions with an interactive interface styled using **Tailwind CSS** and **glassmorphism UI**.

---

## 📌 Features
- ✅ **Weather Prediction** using LSTM deep learning models  
- ✅ **Real-Time Data Visualization** (temperature, humidity, rainfall trends, etc.)  
- ✅ **Interactive Web Interface** built with Django + TailwindCSS  
- ✅ **Model Deployment Ready** for cloud platforms (Heroku, AWS, etc.)  
- ✅ **Scalable & Modular Code Structure** for easy updates  

---

## 📂 Project Structure

Weather-Prediction-WebApp/
├── data/                  # Dataset files (CSV, preprocessed data)
├── models/                # Trained ML/DL models (LSTM, Scaler, etc.)
├── weather_app/           # Main Django app (views, templates, static files)
├── static/                # CSS, JS, images
├── templates/             # HTML templates (frontend UI)
├── manage.py              # Django project manager
└── requirements.txt       # Dependencies

# 🛠️ Installation & Setup

# 1️⃣ Clone the repository
git clone https://github.com/codexrups10/weather-predictor-using-ai.git
cd weather-prediction-webapp

# 2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run Django migrations
python manage.py migrate

# 5️⃣ Start the development server
python manage.py runserver
