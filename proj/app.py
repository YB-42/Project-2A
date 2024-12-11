import requests
from flask import Flask, render_template
import json


app = Flask(__name__)

API_KEY = 'mUYuUqUwyTGa5S7IKkRWBloPTzVpTCU0'
lat = '51.5004'
lon = '-0.1214'

location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={lat},{lon}"
location_response = requests.get(location_url)

if location_response.status_code == 200:
    location_data = location_response.json()
    LOCATION_KEY = location_data['Key']
else:
    print(f"Ошибка при получении ключа местоположения: {location_response.status_code}")
    LOCATION_KEY = None


def check_bad_weather(temperature, wind_speed, precipitation_probability):
    if temperature < 0 or temperature > 35:
        return "Плохие погодные условия"
    if wind_speed > 50:
        return "Плохие погодные условия"
    if precipitation_probability > 70:
        return "Плохие погодные условия"

    return "Хорошие погодные условия"


@app.route('/')
def home():
    return "Добро пожаловать в приложение погоды!"


@app.route('/weather')
def get_weather():
    if LOCATION_KEY is None:
        return "Не удалось получить ключ местоположения", 500

    url = f"http://dataservice.accuweather.com/currentconditions/v1/{LOCATION_KEY}?apikey={API_KEY}&language=ru-ru"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            weather_info = {
                'temperature': data[0]['Temperature']['Metric']['Value'],
                'humidity': data[0].get('RelativeHumidity', 'Нет данных'),
                'wind_speed': data[0].get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 'Нет данных'),
                'precipitation_probability': data[0].get('PrecipitationProbability', 'Нет данных')
            }

            temperature = float(weather_info['temperature'])
            wind_speed = float(weather_info['wind_speed']) if weather_info['wind_speed'] != 'Нет данных' else 0
            precipitation_probability = float(weather_info['precipitation_probability']) if weather_info[
                                                                                                'precipitation_probability'] != 'Нет данных' else 0

            weather_condition = check_bad_weather(temperature, wind_speed, precipitation_probability)

            return render_template('weather.html', weather_info=weather_info, weather_condition=weather_condition)
        else:
            return "Нет данных о погоде", 404
    else:
        return "Не удалось получить данные о погоде", response.status_code


if __name__ == '__main__':
    app.run(debug=True)