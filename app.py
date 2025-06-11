from flask import Flask, render_template, request, jsonify
# import pickle
# import pandas as pd
# import requests
#
# app = Flask(__name__)
#
# pipe = pickle.load(open('pipe.pkl', 'rb'))
#
# teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
#          'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
#          'Rajasthan Royals', 'Delhi Capitals']
#
# cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
#           'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
#           'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
#           'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
#           'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
#           'Sharjah', 'Mohali', 'Bengaluru']
#
# @app.route('/')
# def home():
#     return render_template('predictor.html', teams=teams, cities=cities)
#
# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.json
#     batting_team = data['batting_team']
#     bowling_team = data['bowling_team']
#     city = data['city']
#     target = int(data['target'])
#     score = int(data['score'])
#     overs = float(data['overs'])
#     wickets_lost = int(data['wickets'])
#
#     runs_left = target - score
#     balls_left = 120 - (overs * 6)
#     wickets = 10 - wickets_lost
#     crr = score / overs
#     rrr = (runs_left * 6) / balls_left
#
#     input_df = pd.DataFrame({
#         'batting_team': [batting_team],
#         'bowling_team': [bowling_team],
#         'city': [city],
#         'runs_left': [runs_left],
#         'balls_left': [balls_left],
#         'wickets': [wickets],
#         'total_runs_x': [target],
#         'crr': [crr],
#         'rrr': [rrr]
#     })
#
#     result = pipe.predict_proba(input_df)[0]
#     response = {
#         "batting_team_win_probability": int(round(result[1] * 100)),
#         "bowling_team_win_probability": int(round(result[0] * 100)),
#         "batting_team": batting_team,
#         "bowling_team": bowling_team
#     }
#     return jsonify(response)
#
# @app.route('/live-matches')
# def live_matches():
#     api_key = "YOUR_CRICAPI_KEY"  # Replace with your actual CricAPI key
#     url = f"https://api.cricapi.com/v1/currentMatches?apikey={api_key}&offset=0"
#     response = requests.get(url)
#     matches = []
#     if response.status_code == 200:
#         matches = response.json().get("data", [])
#     return render_template('live_matches.html', matches=matches)
#
# @app.route('/login')
# def login():
#     return render_template('login.html')  # Renders login page
#
# if __name__ == '__main__':
#     app.run(debug=True)

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# app.py
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import pickle
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load model
pipe = pickle.load(open('pipe.pkl', 'rb'))

# Static data
teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
         'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
         'Rajasthan Royals', 'Delhi Capitals']

cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
          'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
          'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
          'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
          'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
          'Sharjah', 'Mohali', 'Bengaluru']

prediction_history = []
# ---------- Routes ----------

@app.route('/')
def login():
    return render_template('login.html')  # JS-only login page


@app.route('/home')
def home():
    return render_template('home.html')  # Homepage after login

@app.route('/ipl_teams_img/<path:filename>')
def custom_static(filename):
    return send_from_directory('ipl_teams_img', filename)

PREDICTIONS_FILE = "predictions.json"

# Helper to save prediction
def save_prediction(prediction_data):
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(prediction_data)

    with open(PREDICTIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route('/predictor')
def predictor():
    return render_template('predictor.html', teams=teams, cities=cities)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    batting_team = data['batting_team']
    bowling_team = data['bowling_team']
    city = data['city']
    target = int(data['target'])
    score = int(data['score'])
    overs = float(data['overs'])
    wickets_lost = int(data['wickets'])

    # Calculations
    runs_left = target - score
    balls_left = 120 - (overs * 6)
    wickets = 10 - wickets_lost
    crr = score / overs
    rrr = (runs_left * 6) / balls_left if balls_left > 0 else 0

    input_df = pd.DataFrame({
        'batting_team': [batting_team],
        'bowling_team': [bowling_team],
        'city': [city],
        'runs_left': [runs_left],
        'balls_left': [balls_left],
        'wickets': [wickets],
        'total_runs_x': [target],
        'crr': [crr],
        'rrr': [rrr]
    })

    result = pipe.predict_proba(input_df)[0]

    # Prediction result
    batting_team_win = int(round(result[1] * 100))
    bowling_team_win = int(round(result[0] * 100))

    # Assume user predicted batting_team
    prediction = {
        "match": f"{batting_team} vs {bowling_team}",
        "predicted_winner": batting_team,
        "confidence": batting_team_win,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save prediction into JSON
    save_prediction(prediction)

    return jsonify({
        "batting_team_win_probability": batting_team_win,
        "bowling_team_win_probability": bowling_team_win,
        "batting_team": batting_team,
        "bowling_team": bowling_team
    })



@app.route('/live_matches')
def live_matches():
    api_key = "c26e8ac3-a975-4eaa-ba4e-211a221ebba0"  # Replace this with your real key
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={api_key}&offset=0"

    try:
        response = requests.get(url)
        matches = response.json().get("data", []) if response.status_code == 200 else []
    except Exception as e:
        matches = []

    return render_template('live_matches.html', matches=matches)

@app.route('/teams')
def teams_page():
    return render_template('teams.html')

# Leaderboard Route
@app.route('/leaderboard')
def leaderboard_page():
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, "r") as f:
            predictions = json.load(f)
    else:
        predictions = []

    return render_template('leaderboard.html', prediction_history=predictions)


# Run
if __name__ == "__main__":
    app.run(debug=True)
