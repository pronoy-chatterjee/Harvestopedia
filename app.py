from flask import Flask, render_template, request, Markup, redirect
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import requests
import datetime
from dateutil import tz
import pickle
import tensorflow as tf
import config
from utils.disease import disease_dict
from utils.fertilizer import fertilizer_dict
import warnings
warnings.filterwarnings("ignore")

# Loading the crop recommendation and disease prediction models and their corresponding label data
crop_recommender_model_path = "models/crop_prediction_model.h5"
crop_recommender_label_path = "models/crop_mappings_data.p"
crop_recommender = tf.keras.models.load_model(crop_recommender_model_path)
with open(crop_recommender_label_path, 'rb') as fp:
    crop_recommender_label = pickle.load(fp)

disease_id_model_path = "models/plant_disease_detection.model"
disease_id_label_path = "models/plant_disease_mappings_data.p"
disease_pred = tf.keras.models.load_model(disease_id_model_path)
with open(disease_id_label_path, 'rb') as fp:
    disease_id_label = pickle.load(fp)

# This function fetches the temperature and weather city wise
def weather_fetch(city_name):
    api_key = config.weather_api_key
    base_url = config.base_url

    complete_url = base_url.format(api_key, city_name.strip())
    response = requests.get(complete_url)
    res = response.json()
    if res["cod"] == 200:
        data = res["main"]
        temperature = round((data["temp"] - 273.15), 2) # Kelvin to celcius
        humidity = data["humidity"]
        return temperature, humidity, res
    else:
        return None

# This function fetches 7 day weather forecast citywise on the basis of latitudes and longitudes
def weather_forecast(lat, lon):
    api_key = config.weather_api_key
    base_url = config.base_url_forecast

    complete_url = base_url.format(lat, lon, api_key)
    response = requests.get(complete_url)
    res = response.json()
    forecast = []
    if 'lat' in res.keys():
        daily_data = res['daily']
        for d in daily_data[1:]:
            day_dict = {}
            day_dict['dt'] = datetime.datetime.fromtimestamp(d['dt']).astimezone(tz.gettz('ITC')).strftime('%d-%m-%y')
            day_dict['temp'] = str(round((d['temp']['day'] - 273.15), 2)) + '°C'
            day_dict['icon'] = "http://openweathermap.org/img/wn/{}@2x.png".format(d['weather'][0]['icon'])
            forecast.append(day_dict)
        return forecast
    else:
        return None

app = Flask(__name__)

# Rendering the lading pages

@ app.route('/')
def home():
    title = 'Harvestopedia'
    return render_template('index.html', title=title)

@app.route('/crop-recommendation')
def crop_recommendation():
    title = 'Harvestopedia - Crop Recommendation'
    return render_template('crop.html', title=title)

@ app.route('/fertilizer-recommendation')
def fertilizer_recommendation():
    title = 'Harvestopedia - Fertilizer Suggestion'
    return render_template('fertilizer.html', title=title)

@app.route('/disease-prediction', methods=['GET', 'POST'])
def disease_prediction():
    title = 'Harvestopedia - Disease Detection'
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files.get('file')
        if not file:
            return render_template('disease.html', title=title)
        try:
            images = []
            image = Image.open(request.files['file'])
            image = ImageOps.fit(image, (224, 224), Image.ANTIALIAS)
            image = img_to_array(image)         
            image = preprocess_input(image)
            images.append(image)
            pred = np.argmax(disease_pred.predict(np.array(images, dtype="float32")), axis=1)
            for key, value in disease_id_label.items():
                if pred == value:
                    final_prediction = key
            prediction = Markup(str(disease_dict[final_prediction]))
            return render_template('disease-result.html', prediction=prediction, title=title)
        except Exception as e:
            print(e)
            pass
    return render_template('disease.html', title=title)

# Crop recommendation
@ app.route('/crop-prediction', methods=['POST'])
def crop_prediction():
    title = 'Harvestopedia - Crop Recommendation'
    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['potassium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        city = request.form.get("city")
        
        if weather_fetch(city) != None:
            temperature, humidity, _ = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            pred = np.argmax(crop_recommender.predict(data), axis=1)
            for key, value in crop_recommender_label.items():
                if pred == value:
                    final_prediction = key
            return render_template('crop-result.html', prediction=final_prediction, title=title)
        else:
            return render_template('try_again.html', title=title)

# Fertilizer recommendation
@ app.route('/fertilizer-prediction', methods=['POST'])
def fertilizer_prediction():
    title = 'Harvestopedia - Fertilizer Suggestion'
    crop = str(request.form['crop'])
    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['potassium'])

    df = pd.read_csv('utils/fertilizer.csv') # dataset having the ideal ranges of soil parameters for every crop

    n_reqd = df[df['Crop'] == crop]['N'].iloc[0]
    p_reqd = df[df['Crop'] == crop]['P'].iloc[0]
    k_reqd = df[df['Crop'] == crop]['K'].iloc[0]

    n = N - n_reqd
    p = P - p_reqd
    k = K - k_reqd
    keys = []
    if n >= 10:
        keys.append('NHigh')
    elif n <= -10:
        keys.append("Nlow")
    if p >= 10:
        keys.append('PHigh')
    elif p <= -10:
        keys.append("Plow")
    if k >= 10:
        keys.append('KHigh')
    elif k <= -10:
        keys.append("Klow")
    
    recom = """"""
    if len(keys) == 0:
        recom = '''<div class="card card-body" style="justify-content: center; background-color:blue">
				            <p class="text-center" style="color: white; font-size: 20px;">Your soil has all the nutrients required to grow {} and hence does not require any fertilizers to be added.</b></p>               
                        </div><br>'''.format(crop)
    else:
        for k in keys:
            html_tag = '''<div class="card card-body" style="justify-content: center; background-color:blue">
				            <p class="text-center" style="color: white; font-size: 20px;">{}</p>               
                        </div><br>'''.format(fertilizer_dict[k])
            recom = recom + html_tag

    response = Markup(recom)
    return render_template('fertilizer-result.html', recommendation=response, title=title)


@app.route('/weather-info')
def weather_info():
    title = 'Harvestopedia - Weather Info'
    return render_template('weather.html', title=title)

# Weather forecast data
@ app.route('/weather-data', methods=['POST'])
def weather_data():
    title = 'Harvestopedia - Weather Info'
    city = request.form.get("city")
    if weather_fetch(city) != None:
        t, h, res = weather_fetch(city)
        weather = {}
        weather['icon'] = "http://openweathermap.org/img/wn/{}@2x.png".format(res['weather'][0]['icon'])        
        weather['min_temp'] = str(round(res['main']['temp_min'] - 273.15, 2))+'°C'
        weather['max_temp'] = str(round(res['main']['temp_max'] - 273.15, 2))+'°C'
        weather['feels_like'] = str(round(res['main']['feels_like'] - 273.15, 2))+'°C'
        weather['cloudiness'] = res['weather'][0]['main']
        weather['humidity'] = h
        weather['temp'] = str(t)+'°C'
        weather['sunrise'] = datetime.datetime.fromtimestamp(res['sys']['sunrise']).astimezone(tz.gettz('ITC')).strftime('%H:%M')
        weather['sunset'] = datetime.datetime.fromtimestamp(res['sys']['sunset']).astimezone(tz.gettz('ITC')).strftime('%H:%M')
        weather['speed'] = str(round(res['wind']['speed']*3.6, 1))+" km/h"
        weather['lat'] = res['coord']['lat']
        weather['lon'] = res['coord']['lon']
        forecast_data = weather_forecast(weather['lat'], weather['lon'])
        return render_template('weather_data.html', weather = weather, forecast = forecast_data, city=city.upper(), title=title)
    else:
        return render_template('try_again.html', title=title)


if __name__ == '__main__':
    app.run(debug=False)